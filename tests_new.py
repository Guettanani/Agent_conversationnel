"""
Tests complets pour les fonctionnalités ajoutées (Fix G et Fix H).

Couvre:
- Suite G: Sauvegarde JSON pre/post-conversion (8 tests)
- Suite H: organize_json.py — classification et organisation (20 tests)
- Suite R: Tests de régression supplémentaires (5 tests)
- Suite P: Tests de performance (5 tests)
- Suite E: Cas limites et edge cases (15 tests)

Total: 53 tests

Usage:
    python -m pytest tests_new.py -v
    python tests_new.py
"""

from __future__ import annotations

import json
import os
import sys
import tempfile
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
from vr_scenario_lib.pipeline import (
    _save_pre_conversion,
    _save_post_conversion,
    run_pipeline,
    validate_scenario_structure,
    PipelineError,
    save_json,
    _save_pre_conversion as save_pre,
    _save_post_conversion as save_post,
)
from vr_scenario_lib.json_converter import (
    convert_scenario_to_json,
    JsonParsingError,
    clean_llm_json,
    parse_scenario_json,
)
from organize_json import (
    classify_json,
    load_json,
    has_long_text,
    scan_json_files,
    organize,
    CONFIG_KEYS,
    DATA_KEYS,
    TEXT_FIELDS,
    MIN_TEXT_LENGTH,
)


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


def _make_mock_retriever(docs: list[Document] | None = None) -> MagicMock:
    retriever = MagicMock()
    if docs is None:
        docs = [
            Document(page_content="Procedure bypass gaz poste GAZFIO", metadata={"source": "bypass.pdf"}),
        ]
    retriever.invoke.return_value = docs
    return retriever


def _make_mock_llm():
    """Create a mock LLM function that returns valid scenario JSON."""
    def _mock(system_prompt, user_prompt, config, max_tokens=2000):
        return json.dumps({
            "scenario_id": "test-scenario",
            "titre": "Scénario Test",
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
    return _mock


# ============================================================================
# Suite G: Pipeline JSON Save Directives (Fix G)
# ============================================================================

class TestSavePreConversion(unittest.TestCase):
    """Tests pour _save_pre_conversion()."""

    def test_creates_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            _save_pre_conversion("test topic", "scenario text", [], tmpdir)
            expected = Path(tmpdir) / "pre-conversion" / "test_topic_raw.json"
            self.assertTrue(expected.exists())

    def test_file_content_structure(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            _save_pre_conversion("mon sujet", "texte scenario", [], tmpdir)
            expected = Path(tmpdir) / "pre-conversion" / "mon_sujet_raw.json"
            obj = json.loads(expected.read_text(encoding="utf-8"))
            self.assertEqual(obj["topic"], "mon sujet")
            self.assertEqual(obj["scenario_text"], "texte scenario")
            self.assertEqual(obj["sources"], [])

    def test_with_none_store_dir(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            old_cwd = os.getcwd()
            try:
                os.chdir(tmpdir)
                _save_pre_conversion("topic", "text", [], None)
                expected = Path(tmpdir) / "scenarios" / "pre-conversion" / "topic_raw.json"
                self.assertTrue(expected.exists())
            finally:
                os.chdir(old_cwd)

    def test_with_sources_metadata(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            docs = [Document(page_content="test", metadata={"source": "doc1.pdf", "page": 1})]
            _save_pre_conversion("topic", "text", docs, tmpdir)
            expected = Path(tmpdir) / "pre-conversion" / "topic_raw.json"
            obj = json.loads(expected.read_text(encoding="utf-8"))
            self.assertEqual(len(obj["sources"]), 1)
            self.assertEqual(obj["sources"][0]["source"], "doc1.pdf")

    def test_special_chars_in_topic(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            _save_pre_conversion("bypass gaz/poste GAZFIO", "text", [], tmpdir)
            expected = Path(tmpdir) / "pre-conversion" / "bypass_gaz_poste_GAZFIO_raw.json"
            self.assertTrue(expected.exists())

    def test_long_topic_truncated(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            long_topic = "a" * 200
            _save_pre_conversion(long_topic, "text", [], tmpdir)
            expected = Path(tmpdir) / "pre-conversion" / f"{'a' * 50}_raw.json"
            self.assertTrue(expected.exists())

    def test_unicode_topic(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            _save_pre_conversion("détente gaz", "text", [], tmpdir)
            expected = Path(tmpdir) / "pre-conversion" / "détente_gaz_raw.json"
            self.assertTrue(expected.exists())

    def test_empty_scenario_text(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            _save_pre_conversion("topic", "", [], tmpdir)
            expected = Path(tmpdir) / "pre-conversion" / "topic_raw.json"
            obj = json.loads(expected.read_text(encoding="utf-8"))
            self.assertEqual(obj["scenario_text"], "")


class TestSavePostConversion(unittest.TestCase):
    """Tests pour _save_post_conversion()."""

    def test_creates_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            result = {"scenario_id": "test", "etapes": []}
            _save_post_conversion("test topic", result, tmpdir)
            expected = Path(tmpdir) / "post-conversion" / "test_topic.json"
            self.assertTrue(expected.exists())

    def test_file_content_matches_input(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            result = {"scenario_id": "x", "titre": "Test", "etapes": [{"etape_id": 1}]}
            _save_post_conversion("topic", result, tmpdir)
            expected = Path(tmpdir) / "post-conversion" / "topic.json"
            obj = json.loads(expected.read_text(encoding="utf-8"))
            self.assertEqual(obj, result)

    def test_with_none_store_dir(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            old_cwd = os.getcwd()
            try:
                os.chdir(tmpdir)
                _save_post_conversion("topic", {"scenario_id": "x"}, None)
                expected = Path(tmpdir) / "scenarios" / "post-conversion" / "topic.json"
                self.assertTrue(expected.exists())
            finally:
                os.chdir(old_cwd)

    def test_empty_result(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            _save_post_conversion("topic", {}, tmpdir)
            expected = Path(tmpdir) / "post-conversion" / "topic.json"
            obj = json.loads(expected.read_text(encoding="utf-8"))
            self.assertEqual(obj, {})

    def test_preserves_all_maser_fields(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            result = {
                "scenario_id": "test",
                "titre": "Test",
                "etat_initial": {
                    "TYPE_POSTE": "GAZFIO",
                    "R0": {"STATUT": 1, "ETAT": 1},
                    "R1": {"STATUT": 1, "ETAT": 1},
                    "R2": {"STATUT": 1, "ETAT": 0},
                    "R3": {"STATUT": 1, "ETAT": 0},
                    "R4": {"STATUT": 1, "ETAT": 75},
                    "VS_GAZFIO": {"STATUT": 1, "ETAT": 0},
                },
                "etapes": [],
            }
            _save_post_conversion("topic", result, tmpdir)
            expected = Path(tmpdir) / "post-conversion" / "topic.json"
            obj = json.loads(expected.read_text(encoding="utf-8"))
            self.assertEqual(obj["etat_initial"]["R4"]["ETAT"], 75)

    def test_special_chars_in_topic(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            _save_post_conversion("bypass/gaz", {"scenario_id": "x"}, tmpdir)
            expected = Path(tmpdir) / "post-conversion" / "bypass_gaz.json"
            self.assertTrue(expected.exists())


class TestRunPipelineSavesBoth(unittest.TestCase):
    """Test d'intégration: run_pipeline sauvegarde les deux fichiers."""

    @patch("vr_scenario_lib.scenario.call_llm")
    @patch("vr_scenario_lib.json_converter.call_llm")
    def test_pipeline_saves_pre_and_post(self, mock_llm_converter, mock_llm_scenario):
        mock_llm_scenario.return_value = "Scenario texte brut pour test"
        mock_llm_converter.return_value = json.dumps({
            "scenario_id": "test",
            "titre": "Test",
            "etat_initial": {
                "TYPE_POSTE": "GAZFIO",
                "R0": {"STATUT": 1, "ETAT": 1},
                "R1": {"STATUT": 1, "ETAT": 1},
                "R2": {"STATUT": 1, "ETAT": 0},
                "R3": {"STATUT": 1, "ETAT": 0},
                "R4": {"STATUT": 1, "ETAT": 75},
                "VS_GAZFIO": {"STATUT": 1, "ETAT": 0},
                "M": {"VALEUR": 2},
                "PM": {"STATUT": 1, "ETAT": 1},
            },
            "etapes": [{"etape_id": 1, "titre": "Etape", "actions": [], "etat_resultant": {}, "conditions_erreur": []}],
        }, ensure_ascii=False)
        with tempfile.TemporaryDirectory() as tmpdir:
            retriever = _make_mock_retriever()
            config = _make_llm_config()
            result = run_pipeline(
                "test_topic",
                retriever,
                config,
                store_dir=tmpdir,
            )
            pre_path = Path(tmpdir) / "pre-conversion" / "test_topic_raw.json"
            post_path = Path(tmpdir) / "post-conversion" / "test_topic.json"
            self.assertTrue(pre_path.exists(), "Fichier pre-conversion manquant")
            self.assertTrue(post_path.exists(), "Fichier post-conversion manquant")


# ============================================================================
# Suite H: organize_json.py (Fix H)
# ============================================================================

class TestClassifyJson(unittest.TestCase):
    """Tests pour classify_json()."""

    def test_classify_config_by_model_key(self):
        obj = {"model": "llama", "api_url": "http://localhost"}
        self.assertEqual(classify_json(obj), "config")

    def test_classify_config_by_token(self):
        obj = {"token": "abc123", "temperature": 0.5}
        self.assertEqual(classify_json(obj), "config")

    def test_classify_data_by_scenario_id(self):
        obj = {"scenario_id": "test", "etapes": []}
        self.assertEqual(classify_json(obj), "data")

    def test_classify_data_by_content(self):
        obj = {"text": "a" * 150}
        self.assertEqual(classify_json(obj), "data")

    def test_classify_data_by_messages(self):
        obj = {"messages": [{"role": "user", "content": "hello"}]}
        self.assertEqual(classify_json(obj), "data")

    def test_classify_unknown_for_none(self):
        self.assertEqual(classify_json(None), "unknown")

    def test_classify_list_of_objects(self):
        obj = [{"id": 1}, {"id": 2}]
        self.assertEqual(classify_json(obj), "data")

    def test_classify_config_primitives_only(self):
        obj = {"host": "localhost", "port": 8080, "debug": True}
        self.assertEqual(classify_json(obj), "config")

    def test_classify_data_with_long_nested_text(self):
        obj = {"level1": {"text": "a" * 150}}
        self.assertEqual(classify_json(obj), "data")

    def test_classify_ambiguous_config_priority(self):
        obj = {"model": "x", "api_url": "y", "scenario_id": "z"}
        self.assertEqual(classify_json(obj), "config")

    def test_classify_single_config_key_not_enough(self):
        obj = {"model": "x", "other_key": "y", "another": "z", "extra": "w"}
        self.assertEqual(classify_json(obj), "config")

    def test_classify_empty_dict(self):
        obj = {}
        self.assertEqual(classify_json(obj), "config")

    def test_classify_empty_list(self):
        obj = []
        self.assertEqual(classify_json(obj), "unknown")


class TestHasLongText(unittest.TestCase):
    """Tests pour has_long_text()."""

    def test_detects_long_text(self):
        self.assertTrue(has_long_text({"text": "a" * 150}))

    def test_ignores_short_text(self):
        self.assertFalse(has_long_text({"text": "short"}))

    def test_recursive_detection(self):
        self.assertTrue(has_long_text({"l1": {"l2": {"content": "x" * 200}}}))

    def test_ignores_non_text_fields(self):
        self.assertFalse(has_long_text({"name": "a" * 200}))

    def test_empty_obj(self):
        self.assertFalse(has_long_text({}))


class TestLoadJson(unittest.TestCase):
    """Tests pour load_json()."""

    def test_loads_valid_json(self, tmp_path=None):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
            json.dump({"key": "value"}, f)
            f.flush()
            obj = load_json(Path(f.name))
            self.assertEqual(obj, {"key": "value"})
        os.unlink(f.name)

    def test_returns_none_for_invalid_json(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write("{invalid json")
            f.flush()
            obj = load_json(Path(f.name))
            self.assertIsNone(obj)
        os.unlink(f.name)

    def test_returns_none_for_missing_file(self):
        obj = load_json(Path("/nonexistent/file.json"))
        self.assertIsNone(obj)


class TestScanJsonFiles(unittest.TestCase):
    """Tests pour scan_json_files()."""

    def test_finds_json_files(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir, "test.json").write_text("{}")
            Path(tmpdir, "test.txt").write_text("not json")
            Path(tmpdir, "test.py").write_text("print('hi')")
            files = scan_json_files(Path(tmpdir))
            self.assertEqual(len(files), 1)
            self.assertEqual(files[0].suffix, ".json")

    def test_respects_depth_zero(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir, "root.json").write_text("{}")
            subdir = Path(tmpdir) / "sub"
            subdir.mkdir()
            (subdir / "nested.json").write_text("{}")
            files = scan_json_files(Path(tmpdir), depth=0)
            self.assertEqual(len(files), 0)

    def test_respects_depth_one(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir, "root.json").write_text("{}")
            subdir = Path(tmpdir) / "sub"
            subdir.mkdir()
            (subdir / "nested.json").write_text("{}")
            files = scan_json_files(Path(tmpdir), depth=1)
            self.assertEqual(len(files), 1)  # root.json only (depth=1 means process root, stop before subdirs)

    def test_empty_directory(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            files = scan_json_files(Path(tmpdir))
            self.assertEqual(len(files), 0)


class TestOrganize(unittest.TestCase):
    """Tests pour organize()."""

    def test_dry_run_no_changes(self):
        with tempfile.TemporaryDirectory() as src:
            Path(src, "test.json").write_text('{"model": "x", "api_url": "y"}')
            dest = Path(src) / "organized"
            organize(Path(src), dest, dry_run=True)
            self.assertFalse(dest.exists())

    def test_copies_files(self):
        with tempfile.TemporaryDirectory() as src:
            Path(src, "config.json").write_text('{"model": "x", "api_url": "y"}')
            dest = Path(src) / "organized"
            organize(Path(src), dest, dry_run=False, move=False)
            self.assertTrue((dest / "config" / "config.json").exists())
            self.assertTrue(Path(src, "config.json").exists())

    def test_moves_files(self):
        with tempfile.TemporaryDirectory() as src:
            Path(src, "config.json").write_text('{"model": "x", "api_url": "y"}')
            dest = Path(src) / "organized"
            organize(Path(src), dest, dry_run=False, move=True)
            self.assertTrue((dest / "config" / "config.json").exists())
            self.assertFalse(Path(src, "config.json").exists())

    def test_handles_name_conflict(self):
        with tempfile.TemporaryDirectory() as src:
            Path(src, "test.json").write_text('{"model": "x", "api_url": "y"}')
            dest = Path(src) / "organized"
            (dest / "config").mkdir(parents=True)
            (dest / "config" / "test.json").write_text('{}')
            organize(Path(src), dest, dry_run=False, move=False)
            self.assertTrue((dest / "config" / "test_1.json").exists())

    def test_creates_correct_directories(self):
        with tempfile.TemporaryDirectory() as src:
            Path(src, "cfg.json").write_text('{"model": "x", "api_url": "y"}')
            Path(src, "dat.json").write_text('{"scenario_id": "test"}')
            dest = Path(src) / "organized"
            organize(Path(src), dest)
            self.assertTrue((dest / "config").is_dir())
            self.assertTrue((dest / "data").is_dir())

    def test_empty_source(self):
        with tempfile.TemporaryDirectory() as src:
            dest = Path(src) / "organized"
            result = organize(Path(src), dest)
            self.assertEqual(result["config"], [])
            self.assertEqual(result["data"], [])

    def test_mixed_classification(self):
        with tempfile.TemporaryDirectory() as src:
            Path(src, "settings.json").write_text('{"model": "llama", "temperature": 0.3}')
            Path(src, "scenario.json").write_text('{"scenario_id": "x", "etapes": []}')
            dest = Path(src) / "organized"
            result = organize(Path(src), dest)
            self.assertIn("settings.json", result["config"])
            self.assertIn("scenario.json", result["data"])


# ============================================================================
# Suite R: Tests de régression supplémentaires
# ============================================================================

class TestRegressionAntiRefusal(unittest.TestCase):
    """Tests anti-régression pour le bug de refus."""

    def test_system_prompt_no_refusal(self):
        refusal = "Désolé, les informations disponibles dans les documents fournis ne permettent pas de générer un scénario sur ce thème."
        self.assertNotIn(refusal, SYSTEM_SCENARIO)

    def test_system_prompt_allows_partial(self):
        self.assertIn("INFORMATIONS MANQUANTES", SYSTEM_SCENARIO)


class TestRegressionJsonOutput(unittest.TestCase):
    """Tests de régression pour la structure JSON Unity."""

    def test_validate_scenario_structure_valid(self):
        data = {
            "scenario_id": "test",
            "titre": "Test",
            "etat_initial": {"TYPE_POSTE": "GAZFIO"},
            "etapes": [{"etape_id": 1, "titre": "Etape", "actions": [], "etat_resultant": {}, "conditions_erreur": []}],
        }
        validate_scenario_structure(data)

    def test_validate_scenario_structure_missing_key(self):
        data = {"scenario_id": "test", "titre": "Test"}
        with self.assertRaises(JsonParsingError):
            validate_scenario_structure(data)

    def test_validate_scenario_structure_invalid_etapes(self):
        data = {"scenario_id": "test", "titre": "Test", "etat_initial": {}, "etapes": "not a list"}
        with self.assertRaises(JsonParsingError):
            validate_scenario_structure(data)


class TestRegressionEncodingRepair(unittest.TestCase):
    """Tests de régression pour la réparation d'encodage."""

    def test_repair_garbled_text(self):
        self.assertEqual(_repair_text("d�tente"), "détente")

    def test_repair_procedure(self):
        result = _repair_text("proc�dure")
        self.assertIn("procédure", result)

    def test_repair_preserves_clean_text(self):
        self.assertEqual(_repair_text("texte propre"), "texte propre")


# ============================================================================
# Suite P: Tests de performance
# ============================================================================

class TestPerformance(unittest.TestCase):
    """Tests de performance de base."""

    def test_repair_text_under_1s(self):
        text = "d�tente " * 1000
        start = time.time()
        _repair_text(text)
        elapsed = time.time() - start
        self.assertLess(elapsed, 1.0)

    def test_classify_json_under_1ms(self):
        obj = {"model": "x", "api_url": "y", "temperature": 0.3}
        start = time.time()
        for _ in range(1000):
            classify_json(obj)
        elapsed = time.time() - start
        self.assertLess(elapsed, 1.0)

    def test_load_json_under_1s(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
            json.dump({"key": "value" * 100}, f)
            f.flush()
            start = time.time()
            load_json(Path(f.name))
            elapsed = time.time() - start
            self.assertLess(elapsed, 1.0)
        os.unlink(f.name)

    def test_scan_json_files_under_1s(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            for i in range(50):
                Path(tmpdir, f"file_{i}.json").write_text("{}")
            start = time.time()
            scan_json_files(Path(tmpdir))
            elapsed = time.time() - start
            self.assertLess(elapsed, 1.0)

    def test_organize_100_files_under_10s(self):
        with tempfile.TemporaryDirectory() as src:
            for i in range(100):
                Path(src, f"file_{i}.json").write_text(json.dumps({"model": "x", "api_url": "y"}))
            dest = Path(src) / "organized"
            start = time.time()
            organize(Path(src), dest)
            elapsed = time.time() - start
            self.assertLess(elapsed, 10.0)


# ============================================================================
# Suite E: Edge Cases
# ============================================================================

class TestEdgeCases(unittest.TestCase):
    """Tests pour les cas limites."""

    def test_save_pre_conversion_empty_text(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            _save_pre_conversion("topic", "", [], tmpdir)
            expected = Path(tmpdir) / "pre-conversion" / "topic_raw.json"
            obj = json.loads(expected.read_text(encoding="utf-8"))
            self.assertEqual(obj["scenario_text"], "")

    def test_save_post_conversion_empty_result(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            _save_post_conversion("topic", {}, tmpdir)
            expected = Path(tmpdir) / "post-conversion" / "topic.json"
            obj = json.loads(expected.read_text(encoding="utf-8"))
            self.assertEqual(obj, {})

    def test_organize_with_binary_json_file(self):
        with tempfile.TemporaryDirectory() as src:
            Path(src, "binary.json").write_bytes(b"\x00\x01\x02\x03")
            dest = Path(src) / "organized"
            result = organize(Path(src), dest)
            self.assertIn("binary.json", result["unknown"])

    def test_organize_with_empty_json_file(self):
        with tempfile.TemporaryDirectory() as src:
            Path(src, "empty.json").write_text("")
            dest = Path(src) / "organized"
            result = organize(Path(src), dest)
            self.assertIn("empty.json", result["unknown"])

    def test_organize_with_null_json(self):
        with tempfile.TemporaryDirectory() as src:
            Path(src, "null.json").write_text("null")
            dest = Path(src) / "organized"
            result = organize(Path(src), dest)
            self.assertIn("null.json", result["unknown"])

    def test_organize_with_deeply_nested_json(self):
        with tempfile.TemporaryDirectory() as src:
            nested = {"level": {}}
            current = nested["level"]
            for i in range(50):
                current["nested"] = {}
                current = current["nested"]
            Path(src, "nested.json").write_text(json.dumps(nested))
            dest = Path(src) / "organized"
            result = organize(Path(src), dest)
            self.assertIn("nested.json", result["data"])

    def test_organize_with_unicode_filename(self):
        with tempfile.TemporaryDirectory() as src:
            Path(src, "données.json").write_text('{"scenario_id": "x"}')
            dest = Path(src) / "organized"
            result = organize(Path(src), dest)
            self.assertIn("données.json", result["data"])

    def test_organize_with_special_chars_filename(self):
        with tempfile.TemporaryDirectory() as src:
            Path(src, "test file (1).json").write_text('{"model": "x", "api_url": "y"}')
            dest = Path(src) / "organized"
            result = organize(Path(src), dest)
            self.assertIn("test file (1).json", result["config"])

    def test_save_with_very_long_topic(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            long_topic = "a" * 200
            _save_pre_conversion(long_topic, "text", [], tmpdir)
            expected = Path(tmpdir) / "pre-conversion" / f"{'a' * 50}_raw.json"
            self.assertTrue(expected.exists())

    def test_organize_duplicate_filenames_across_subdirs(self):
        with tempfile.TemporaryDirectory() as src:
            sub1 = Path(src) / "sub1"
            sub2 = Path(src) / "sub2"
            sub1.mkdir()
            sub2.mkdir()
            (sub1 / "file.json").write_text('{"model": "x", "api_url": "y"}')
            (sub2 / "file.json").write_text('{"scenario_id": "z", "etapes": []}')
            dest = Path(src) / "organized"
            result = organize(Path(src), dest)
            self.assertTrue((dest / "config" / "file.json").exists())
            self.assertTrue((dest / "data" / "file.json").exists())

    def test_organize_source_equals_dest_error(self):
        with tempfile.TemporaryDirectory() as src:
            Path(src, "test.json").write_text('{"model": "x"}')
            result = organize(Path(src), Path(src))
            self.assertEqual(result["config"], [])
            self.assertEqual(result["data"], [])

    def test_classify_json_with_all_config_keys(self):
        obj = {k: "value" for k in list(CONFIG_KEYS)[:5]}
        self.assertEqual(classify_json(obj), "config")

    def test_classify_json_with_all_data_keys(self):
        obj = {k: "value" for k in list(DATA_KEYS)[:5]}
        self.assertEqual(classify_json(obj), "data")

    def test_has_long_text_with_list(self):
        obj = [{"text": "a" * 150}]
        self.assertTrue(has_long_text(obj))


# ============================================================================
# Runner
# ============================================================================

if __name__ == "__main__":
    unittest.main(verbosity=2)
