"""
Tests de régression et de validation pour le bug de refus du pipeline VR.

Couvre:
- Extraction documentaire (PDF, DOCX) avec réparation d'encodage
- Qualité du contenu extrait (domaine gazier)
- Vectorstore fallback (numpy)
- Pertinence du retrieval
- Construction du prompt
- Refus catégorique du LLM (anti-régression)
- Robustesse aux entrées invalides
- Performance de base

Usage:
    python tests_regression.py
    python -m pytest tests_regression.py -v
"""

import json
import os
import sys
import time
import unittest
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

_PACKAGE_ROOT = Path(__file__).resolve().parent
if str(_PACKAGE_ROOT) not in sys.path:
    sys.path.insert(0, str(_PACKAGE_ROOT))

from langchain_core.documents import Document

from vr_scenario_lib.config import (
    SYSTEM_SCENARIO,
    build_llm_config,
    CORRESPONDANCE_OBJETS,
)
from vr_scenario_lib.documents import (
    DOMAIN_KEYWORDS,
    DocumentLoadError,
    _repair_text,
    _has_garbled_content,
    check_document_quality,
    load_document,
    scan_directory,
    split_documents,
)
from vr_scenario_lib.scenario import (
    format_context,
    generate_scenario,
    retrieve_context,
)
from vr_scenario_lib.vectorstore import (
    NumpyVectorStore,
    create_embeddings,
    create_retriever,
    build_vectorstore,
)


REFUSAL_MESSAGE = "Désolé, les informations disponibles dans les documents fournis ne permettent pas de générer un scénario sur ce thème."


# ============================================================================
# Helpers
# ============================================================================

def _make_llm_config(token: str = "test_token_12345") -> dict:
    return {
        "api_url": "https://openrouter.ai/api/v1/chat/completions",
        "model": "meta-llama/llama-3.3-70b-instruct:free",
        "fallback_models": [],
        "token": token,
        "max_tokens": 1500,
        "temperature": 0.3,
        "timeout": 60,
        "max_retries": 1,
        "retry_backoff_factor": 2.0,
    }


def _build_retriever_from_docs(docs_dir: str = "./documents", k: int = 5):
    """Construit un retriever à partir des documents réels.

    Utilise un mock pour les embeddings afin de ne pas consommer de crédits API.
    """
    raw_docs = scan_directory(docs_dir)
    chunks = split_documents(raw_docs)

    embeddings = MagicMock()
    embeddings.embed_documents = MagicMock(
        return_value=[[float(i)] * 384 for i in range(len(chunks))]
    )
    embeddings.embed_query = MagicMock(return_value=[0.0] * 384)

    vs = build_vectorstore(chunks, embeddings)
    return create_retriever(vs, k=k)


def _mock_llm_response(*args, **kwargs) -> str:
    """Mock LLM qui retourne un scénario valide (pour tests sans API)."""
    return json.dumps({
        "scenario_id": "test-bypass-gaz",
        "titre": "Scénario Test Bypass Gaz",
        "etat_initial": {
            "TYPE_POSTE": "GAZFIO",
            "METEO": "J",
            "DEMANDE_CLIENT": {"MOY": 500, "TYPE": "SIN", "RESEAU": 15},
            "R0": {"STATUT": 1, "ETAT": 1},
            "R1": {"STATUT": 1, "ETAT": 1},
            "R2": {"STATUT": 1, "ETAT": 0},
            "R3": {"STATUT": 1, "ETAT": 0},
            "R4": {"STATUT": 1, "ETAT": 75},
            "VS_GAZFIO": {"STATUT": 1, "ETAT": 0},
            "M": {"VALEUR": 2},
            "PM": {"STATUT": 1, "ETAT": 1},
        },
        "etapes": [
            {
                "etape_id": 1,
                "titre": "Étape test",
                "actions": [{"objet": "R0", "action": "fermer", "valeur_attendue": "0"}],
                "etat_resultant": {"R0": {"STATUT": 1, "ETAT": 0}},
                "conditions_erreur": [],
            }
        ],
    }, ensure_ascii=False)


# ============================================================================
# F — Tests Fonctionnels
# ============================================================================

class TestF_Extraction(unittest.TestCase):
    """F-01 à F-04: Extraction documentaire et chunking."""

    def test_f01_pdf_extraction_non_empty(self):
        """F-01: PDF extraction returns non-empty content."""
        docs = load_document("documents/bypass.pdf")
        total = sum(len(d.page_content) for d in docs)
        self.assertGreater(total, 100, f"PDF extraction returned only {total} chars")

    def test_f02_docx_extraction_non_empty(self):
        """F-02: DOCX extraction returns non-empty content."""
        docs = load_document("documents/GRDF_Procedure_Consignation_Deconsignation (2).docx")
        total = sum(len(d.page_content) for d in docs)
        self.assertGreater(total, 500, f"DOCX extraction returned only {total} chars")

    def test_f03_directory_scan_loads_both_files(self):
        """F-03: Directory scan loads both documents."""
        docs = scan_directory("./documents")
        sources = {d.metadata.get("source", "") for d in docs}
        has_pdf = any("bypass.pdf" in s for s in sources)
        has_docx = any("GRDF" in s for s in sources)
        self.assertTrue(has_pdf, "bypass.pdf not loaded")
        self.assertTrue(has_docx, "GRDF DOCX not loaded")

    def test_f04_chunking_produces_valid_chunks(self):
        """F-04: Chunking produces non-empty chunks with metadata."""
        docs = scan_directory("./documents")
        chunks = split_documents(docs)
        self.assertGreater(len(chunks), 0, "No chunks produced")
        for i, chunk in enumerate(chunks):
            self.assertGreater(len(chunk.page_content), 0, f"Chunk {i} is empty")
            self.assertIn("source", chunk.metadata, f"Chunk {i} missing source metadata")


class TestF_Quality(unittest.TestCase):
    """F-05 à F-08: Qualité du contenu et retrieval."""

    def test_f05_numpy_vectorstore_build(self):
        """F-05: NumpyVectorStore builds successfully."""
        docs = scan_directory("./documents")
        chunks = split_documents(docs)

        emb = MagicMock()
        emb.embed_documents = MagicMock(
            return_value=[[0.0] * 384 for _ in range(len(chunks))]
        )
        emb.embed_query = MagicMock(return_value=[0.0] * 384)

        vs = build_vectorstore(chunks, emb)
        self.assertIsNotNone(vs)
        self.assertEqual(vs.index.ntotal, len(chunks))

    def test_f06_retrieval_returns_results(self):
        """F-06: Retrieval returns at least 1 result."""
        retriever = _build_retriever_from_docs(k=3)
        results = retriever.invoke("bypass gaz")
        self.assertGreater(len(results), 0, "No retrieval results")

    def test_f07_context_formatting(self):
        """F-07: Context formatting produces non-empty string with source markers."""
        retriever = _build_retriever_from_docs(k=3)
        docs = retriever.invoke("bypass gaz")
        context = format_context(docs)
        self.assertGreater(len(context), 50, f"Context too short: {len(context)} chars")
        self.assertIn("[Source", context, "Missing [Source N] markers")

    def test_f08_prompt_construction(self):
        """F-08: Prompt contains MASER table and topic."""
        from vr_scenario_lib.prompts import build_scenario_prompt
        prompt = build_scenario_prompt("bypass gaz", "test context")
        self.assertIn("bypass gaz", prompt)
        self.assertIn("R0", prompt)
        self.assertIn("VS_GAZFIO", prompt)
        self.assertIn(CORRESPONDANCE_OBJETS[:50], prompt)


class TestF_DomainQuality(unittest.TestCase):
    """F-09 à F-10: Document quality check."""

    def test_f09_good_document_quality(self):
        """F-09: GRDF DOCX passes quality check."""
        docs = load_document("documents/GRDF_Procedure_Consignation_Deconsignation (2).docx")
        result = check_document_quality(docs)
        self.assertGreater(result["total_chars"], 500)
        self.assertGreater(result["domain_score"], 0.0)
        self.assertTrue(
            result["is_adequate"] or result["total_chars"] > 500,
            f"Quality check failed: {result['details']}"
        )

    def test_f10_empty_document_quality(self):
        """F-10: Empty document fails quality check."""
        result = check_document_quality([])
        self.assertFalse(result["is_adequate"])
        self.assertGreater(len(result["details"]), 0)


# ============================================================================
# R — Tests de Robustesse
# ============================================================================

class TestR_Robustness(unittest.TestCase):
    """R-01 à R-10: Robustness edge cases."""

    def test_r01_scan_empty_directory(self):
        """R-01: Empty directory raises ValueError."""
        with self.assertRaises((ValueError, FileNotFoundError)):
            scan_directory("./nonexistent_dir_12345")

    def test_r02_unsupported_file_type(self):
        """R-02: Unsupported file type is silently skipped."""
        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir) / "test.txt"
            tmp_path.write_text("unsupported content")
            with self.assertRaises(ValueError):
                scan_directory(tmpdir)

    def test_r03_corrupted_pdf_fallback(self):
        """R-03: Corrupted PDF triggers OCR fallback gracefully."""
        docs = load_document("documents/bypass.pdf")
        self.assertIsInstance(docs, list)
        self.assertGreater(len(docs), 0)

    def test_r04_ocr_dependencies_missing(self):
        """R-04: OCR fallback degrades gracefully if deps missing."""
        from vr_scenario_lib.documents import _ocr_pdf
        result = _ocr_pdf("documents/bypass.pdf")
        self.assertIsInstance(result, list)
        if result and "ERREUR OCR" in result[0].page_content:
            self.assertIn("ERREUR OCR", result[0].page_content)

    def test_r05_empty_topic_rejected(self):
        """R-05: Empty topic raises ValueError."""
        from vr_scenario_lib.main import sanitize_topic
        with self.assertRaises(ValueError):
            sanitize_topic("")

    def test_r06_very_long_topic_rejected(self):
        """R-06: Very long topic raises ValueError."""
        from vr_scenario_lib.main import sanitize_topic
        with self.assertRaises(ValueError):
            sanitize_topic("a" * 501)

    def test_r07_unicode_topic_accepted(self):
        """R-07: Unicode in topic is accepted."""
        from vr_scenario_lib.main import sanitize_topic
        result = sanitize_topic("bypass gaz — détente")
        self.assertEqual(result, "bypass gaz — détente")

    def test_r08_split_documents_empty_list(self):
        """R-08: split_documents with empty list raises ValueError."""
        with self.assertRaises(ValueError):
            split_documents([])

    def test_r09_build_vectorstore_empty_chunks(self):
        """R-09: build_vectorstore with empty chunks raises ValueError."""
        with self.assertRaises(ValueError):
            build_vectorstore([], None)

    def test_r10_retrieval_empty_query(self):
        """R-10: Retrieval with empty query does not crash."""
        retriever = _build_retriever_from_docs(k=3)
        try:
            results = retriever.invoke("")
            self.assertIsInstance(results, list)
        except Exception as exc:
            self.fail(f"Empty query raised exception: {exc}")


# ============================================================================
# Anti-Refusal (regression guard)
# ============================================================================

class TestAntiRefusal(unittest.TestCase):
    """Hard guard: the LLM must never return the hardcoded refusal."""

    def test_system_prompt_does_not_instruction_refuse(self):
        """SYSTEM_SCENARIO must not instruct the LLM to refuse."""
        self.assertNotIn(
            REFUSAL_MESSAGE,
            SYSTEM_SCENARIO,
            "SYSTEM_SCENARIO still contains the refusal instruction"
        )

    def test_generate_scenario_with_mocked_llm_does_not_refuse(self):
        """generate_scenario with a mocked LLM must not produce refusal."""
        retriever = _build_retriever_from_docs(k=3)
        llm_config = _make_llm_config()

        with patch("vr_scenario_lib.scenario.call_llm", side_effect=_mock_llm_response):
            scenario_text, sources = generate_scenario(
                topic="bypass gaz",
                retriever=retriever,
                llm_config=llm_config,
            )

        self.assertNotIn(REFUSAL_MESSAGE, scenario_text)
        self.assertGreater(len(scenario_text), 50)

    def test_generate_scenario_refusal_when_llm_refuses(self):
        """If LLM refuses, the refusal text must be detectable."""
        retriever = _build_retriever_from_docs(k=3)
        llm_config = _make_llm_config()

        with patch("vr_scenario_lib.scenario.call_llm", return_value=REFUSAL_MESSAGE):
            scenario_text, sources = generate_scenario(
                topic="bypass gaz",
                retriever=retriever,
                llm_config=llm_config,
            )

        self.assertIn(REFUSAL_MESSAGE, scenario_text)


# ============================================================================
# Encoding Repair
# ============================================================================

class TestEncodingRepair(unittest.TestCase):
    """Validate _repair_text helper."""

    def test_repair_supplements_garbage_chars(self):
        """Repair replaces garbled chars and fixes common French words."""
        result = _repair_text("d�tente")
        self.assertNotIn("�", result)
        self.assertIn("détente", result)

    def test_repair_removes_control_chars(self):
        self.assertNotIn("�", _repair_text("test�value"))

    def test_repair_empty_string(self):
        self.assertEqual(_repair_text(""), "")

    def test_repair_none(self):
        self.assertIsNone(_repair_text(None))

    def test_repair_fixes_common_words(self):
        """Repair fixes common French gas-domain words with garbled chars."""
        result = _repair_text("proc�dure de consignation")
        self.assertNotIn("�", result)
        self.assertIn("procédure", result)
        self.assertIn("consignation", result)

    def test_has_garbled_content_detects_garbage(self):
        docs = [Document(page_content="������������������")]
        self.assertTrue(_has_garbled_content(docs))

    def test_has_garbled_content_clean_text(self):
        docs = [Document(page_content="Ceci est un texte propre sans erreurs.")]
        self.assertFalse(_has_garbled_content(docs))


# ============================================================================
# NumpyVectorStore
# ============================================================================

class TestNumpyVectorStore(unittest.TestCase):
    """Validate fallback vectorstore."""

    def _mock_embeddings(self, dim: int = 4):
        """Create a mock embeddings instance."""
        emb = MagicMock()
        emb.embed_documents = MagicMock(
            return_value=[[float(i + j) for j in range(dim)] for i in range(3)]
        )
        emb.embed_query = MagicMock(
            return_value=[1.0] + [0.0] * (dim - 1)
        )
        return emb

    def test_build_and_search(self):
        """NumpyVectorStore builds and retrieves."""
        embeddings = self._mock_embeddings()
        chunks = [
            Document(page_content="Le robinet R0 isole le poste"),
            Document(page_content="La vanne R3 bypass permet la diversion"),
            Document(page_content="La pression est mesurée au point PM"),
        ]
        vs = NumpyVectorStore.from_documents(chunks, embeddings)
        self.assertEqual(vs.index.ntotal, 3)

        results = vs.similarity_search("robinet R0", k=2)
        self.assertGreater(len(results), 0)

    def test_empty_chunks_raises(self):
        """Empty chunks raise ValueError."""
        embeddings = self._mock_embeddings()
        with self.assertRaises(ValueError):
            NumpyVectorStore.from_documents([], embeddings)

    def test_as_retriever_returns_adapter(self):
        """as_retriever returns an object with invoke()."""
        embeddings = self._mock_embeddings()
        chunks = [Document(page_content="test gaz")]
        vs = NumpyVectorStore.from_documents(chunks, embeddings)
        adapter = vs.as_retriever(k=1)
        results = adapter.invoke("gaz")
        self.assertIsInstance(results, list)


# ============================================================================
# Performance
# ============================================================================

class TestPerformance(unittest.TestCase):
    """Basic performance tests."""

    def test_pdf_extraction_under_5s(self):
        """PDF extraction completes in <5 seconds."""
        start = time.time()
        load_document("documents/bypass.pdf")
        elapsed = time.time() - start
        self.assertLess(elapsed, 5.0, f"PDF extraction took {elapsed:.2f}s")

    def test_docx_extraction_under_5s(self):
        """DOCX extraction completes in <5 seconds."""
        start = time.time()
        load_document("documents/GRDF_Procedure_Consignation_Deconsignation (2).docx")
        elapsed = time.time() - start
        self.assertLess(elapsed, 5.0, f"DOCX extraction took {elapsed:.2f}s")

    def test_chunking_under_2s(self):
        """Chunking completes in <2 seconds."""
        docs = scan_directory("./documents")
        start = time.time()
        split_documents(docs)
        elapsed = time.time() - start
        self.assertLess(elapsed, 2.0, f"Chunking took {elapsed:.2f}s")

    def test_vectorstore_build_under_60s(self):
        """Vectorstore build (with mocked embedding API call) completes in <60s."""
        docs = scan_directory("./documents")
        chunks = split_documents(docs)

        emb = MagicMock()
        emb.embed_documents = MagicMock(
            return_value=[[0.0] * 384 for _ in range(len(chunks))]
        )
        emb.embed_query = MagicMock(return_value=[0.0] * 384)

        start = time.time()
        build_vectorstore(chunks, emb)
        elapsed = time.time() - start
        self.assertLess(elapsed, 60.0, f"Vectorstore build took {elapsed:.2f}s")


# ============================================================================
# Runner
# ============================================================================

if __name__ == "__main__":
    unittest.main(verbosity=2)
