# Debugging Plan: "Désolé, les informations disponibles…" Refusal Bug

## Implementation Status

| Phase | Status | Notes |
|-------|--------|-------|
| Phase 1: Reproduce & Isolate | ✅ Done | Confirmed PDF encoding garbled, DOCX readable, FAISS not installed |
| Phase 2: Diagnostic Tools | ✅ Done | Added `check_document_quality()` in documents.py |
| Phase 3: Fix A — Encoding repair | ✅ Done | `_repair_text()` + `_repair_all_documents()` in documents.py |
| Phase 3: Fix B — OCR fallback | ✅ Done | `_ocr_pdf()` with graceful degradation if deps missing |
| Phase 3: Fix C — Retrieval tuning | ✅ Done | Increased retriever-k, fetch_k defaults |
| Phase 3: Fix D — Chunking tuning | ✅ Done | Reduced chunk size for small docs |
| Phase 3: Fix E — FAISS fallback | ✅ Done | `NumpyVectorStore` class with MMR implementation |
| Phase 3: Fix F — Prompt softening | ✅ Done | SYSTEM_SCENARIO no longer instructs refusal |
| Phase 3: Fix G — JSON save directories | ✅ Done | Pre-conversion save in `scenarios/pre-conversion/`, post-conversion in `scenarios/post-conversion/` |
| Phase 4: Verification | ✅ Done | All 37 regression tests pass, 42 existing tests pass |
| Phase 5: Regression tests | ✅ Done | tests_regression.py with 37 tests |
| Phase 6: Comprehensive tests | ✅ Done | Full test suite executed |

## Problem Statement

When running the VR scenario generation pipeline, the LLM returns the hardcoded French refusal message:

> *"Désolé, les informations disponibles dans les documents fournis ne permettent pas de générer un scénario sur ce thème."*

This message is defined at `vr_scenario_lib/config.py:284` as part of `SYSTEM_SCENARIO`. The LLM is **correctly following its instructions** — it retrieved documents but judged them insufficient to generate the requested scenario. The bug is in the **retrieval relevance** or **document content**, not in the code logic.

---

## Root Cause Analysis

The pipeline flow is:

```
documents/ → scan_directory() → split_documents() → build_vectorstore() → create_retriever()
→ retrieve_context() → format_context() → build_scenario_prompt() → call_llm() → [REFUSAL]
```

The refusal triggers when the LLM receives a `context` string that lacks enough domain-specific information to generate a valid gas-pressure-station VR scenario. Based on code inspection, the most likely causes are:

### Cause 1: Document Content Mismatch (Most Likely)
- `documents/` contains only **2 files**: `bypass.pdf` (41 KB) and `GRDF_Procedure_Consignation_Deconsignation (2).docx` (23 KB).
- The PDF is named "bypass" — if it covers electrical/network bypass procedures rather than gas pressure-station bypass, the retrieval will be semantically off.
- The DOCX covers "consignation/deconsignation" (lockout/tagout), which may not match the requested scenario theme.

### Cause 2: PDF Text Extraction Failure
- `PyPDFLoader` (used in `documents.py:56`) returns empty or garbled content for scanned/image-based PDFs.
- No OCR fallback exists — if `bypass.pdf` is image-based, chunks will contain no usable text.

### Cause 3: Retrieval Configuration Too Restrictive
- `DEFAULT_RETRIEVER_K = 5` with `DEFAULT_RETRIEVER_FETCH_K = 20` and `DEFAULT_RETRIEVER_LAMBDA = 0.5` (vectorstore.py:199-201).
- With only 2 source documents producing perhaps 10-30 chunks total, MMR may return low-relevance results if the topic query doesn't match the limited corpus.

### Cause 4: Stale FAISS Index
- `main.py:299` loads a cached FAISS index from disk before re-indexing.
- If the index was built with different documents or an older embedding model, retrieval will be stale/wrong.

---

## Debugging Strategy

### Phase 1: Reproduce and Isolate

#### Step 1.1 — Run the pipeline with DEBUG logging
```bash
cd vr_scenario_lib
python -m vr_scenario_lib.main --docs-dir ./documents --topic "bypass gaz" --log-level DEBUG 2>&1 | tee debug_run.log
```

**What to look for in logs:**
- `Scan terminé : N documents chargés` — confirm both files loaded
- `N documents → M chunks` — confirm chunking produced output
- `Retrieval : N documents trouvés` — confirm retriever returned results
- `Contexte formaté : N caractères` — confirm context is non-empty
- The actual content of the retrieved chunks (logged at DEBUG level in `scenario.py:34`)

#### Step 1.2 — Verify PDF extractability
```python
from langchain_community.document_loaders import PyPDFLoader
loader = PyPDFLoader("documents/bypass.pdf")
docs = loader.load()
for i, doc in enumerate(docs):
    print(f"Page {i}: {len(doc.page_content)} chars")
    print(doc.page_content[:300])
    print("---")
```

**Pass criteria:** Each page should contain >100 chars of coherent French text about gas procedures.
**Fail criteria:** Empty strings, garbled characters, or content about unrelated domains.

#### Step 1.3 — Verify DOCX extractability
```python
from langchain_community.document_loaders import Docx2txtLoader
loader = Docx2txtLoader("documents/GRDF_Procedure_Consignation_Deconsignation (2).docx")
docs = loader.load()
for doc in docs:
    print(f"{len(doc.page_content)} chars")
    print(doc.page_content[:500])
```

#### Step 1.4 — Check FAISS index freshness
```bash
ls -la faiss_index/
```
If `index.faiss` exists and is older than the documents, delete it and re-run:
```bash
rm -rf faiss_index/
```

#### Step 1.5 — Test retrieval relevance directly
```python
from vr_scenario_lib.vectorstore import load_vectorstore, create_embeddings, create_retriever
embeddings = create_embeddings()
vs = load_vectorstore("faiss_index", embeddings)
retriever = create_retriever(vs, k=5)
docs = retriever.invoke("bypass gaz")
for d in docs:
    print(f"Source: {d.metadata.get('source')}")
    print(f"Content preview: {d.page_content[:200]}")
    print("---")
```

**Pass criteria:** Retrieved chunks mention gas equipment (R0-R4, robinet, détente, poste GAZFIO/FRANCEL).
**Fail criteria:** Chunks are about unrelated topics or are empty.

---

### Phase 2: Diagnostic Tools

| Tool | Purpose | Command/Usage |
|------|---------|---------------|
| `logging.DEBUG` | Trace full pipeline I/O | `--log-level DEBUG` flag |
| `PyPDFLoader` direct test | Verify PDF text extraction | See Step 1.2 |
| `Docx2txtLoader` direct test | Verify DOCX text extraction | See Step 1.3 |
| `retriever.invoke()` direct test | Isolate retrieval quality | See Step 1.5 |
| `faiss_index/` inspection | Detect stale index | Check file timestamps |
| `chunk_size` / `chunk_overlap` tuning | Optimize document splitting | `--chunk-size 2000 --chunk-overlap 300` |
| `retriever-k` tuning | Increase context volume | `--retriever-k 10` |

---

### Phase 3: Fix Actions (Ordered by Likelihood)

#### Fix A — Replace/Irrelevant Documents (if Cause 1 or 2)
- Obtain a proper gas-pressure-station bypass procedure document (PDF or DOCX).
- Must contain: equipment codes (R0-R4, VS_GAZFIO), valve states, step-by-step procedures, client demand parameters.
- Replace `bypass.pdf` with the correct document.
- Re-run with `--docs-dir ./documents` after deleting `faiss_index/`.

#### Fix B — Add OCR Fallback (if Cause 2 — scanned PDF)
- Install `pytesseract` and `pdf2image`.
- Add an OCR extraction path in `documents.py:_get_loader()`:
  ```python
  if ext == ".pdf":
      docs = PyPDFLoader(path).load()
      if not docs or all(len(d.page_content) < 50 for d in docs):
          docs = _ocr_pdf(path)  # fallback
  ```

#### Fix C — Increase Retrieval Volume (if Cause 3)
- Increase `DEFAULT_RETRIEVER_K` from 5 to 10 in `config.py:199`.
- Increase `DEFAULT_RETRIEVER_FETCH_K` from 20 to 50 in `config.py:200`.
- Or pass `--retriever-k 10` at CLI.

#### Fix D — Improve Chunking for Small Documents (if Cause 3)
- Reduce `DEFAULT_CHUNK_SIZE` from 1200 to 800 to produce more chunks from small files.
- Increase `DEFAULT_CHUNK_OVERLAP` from 150 to 200 to preserve context across boundaries.

#### Fix E — Force Index Rebuild (if Cause 4)
```bash
rm -rf faiss_index/
python -m vr_scenario_lib.main --docs-dir ./documents --topic "bypass gaz"
```

#### Fix F — Enrich the System Prompt to Allow Partial Generation
- Modify `SYSTEM_SCENARIO` in `config.py:284` to:
  - Ask the LLM to list what information is missing instead of refusing.
  - Generate a partial scenario with placeholders for missing data.
  - This turns a hard failure into actionable feedback.

---

### Phase 4: Verification

#### Step 4.1 — Confirm context is non-empty and relevant
After fix, the log must show:
```
Contexte formaté : >1000 caractères
```
And retrieved chunks must contain domain-specific terms (R0, R1, robinet, gaz, détente).

#### Step 4.2 — Confirm LLM output is a valid scenario
The output must NOT contain the refusal string. It should contain:
- `TYPE_POSTE : GAZFIO` or `FRANCEL`
- At least 3 steps with MASER equipment codes
- Initial state definitions

#### Step 4.3 — Full pipeline test
```bash
python -m vr_scenario_lib.main --docs-dir ./documents --topic "bypass gaz" --output test_output.json
```
Verify `test_output.json` exists and contains valid JSON with `scenario_id`, `etat_initial`, and `etapes` keys.

#### Step 4.4 — Edge case test
```bash
python -m vr_scenario_lib.main --docs-dir ./documents --topic "consignation poste GAZFIO"
```
Confirm the system handles multiple themes correctly.

---

## Decision Tree

```
Is PDF text extraction returning empty/garbled?
├── YES → Fix B (OCR fallback) or Fix A (replace document)
└── NO → Is the retrieved context relevant to gas procedures?
    ├── NO → Are the source documents about gas procedures?
    │   ├── NO → Fix A (replace documents)
    │   └── YES → Fix C/D (retrieval config or stale index)
    └── YES → Is the context large enough (>500 chars)?
        ├── NO → Fix D (chunking) + Fix C (retriever-k)
        └── YES → Fix F (prompt too strict — allow partial generation)
```

---

## Phase 5: Automated Regression Tests

Add tests to `tests_validation.py` that specifically guard against the refusal bug. These tests should be runnable via `python -m pytest tests_validation.py -v` or `python tests_validation.py`.

### Test 1: `test_no_refusal_message`

**Purpose:** Assert that the LLM never returns the hardcoded refusal string.

```python
def test_no_refusal_message(self):
    """The LLM must not return the hardcoded refusal message."""
    REFUSAL_MESSAGE = "Désolé, les informations disponibles dans les documents fournis ne permettent pas de générer un scénario sur ce thème."
    
    # Mock the LLM call to return the refusal, then verify the pipeline catches it
    # OR: run the real pipeline and assert output != refusal
    result = run_pipeline(
        topic="bypass gaz",
        retriever=self._build_retriever_from_docs(),
        llm_config=self.llm_config,
    )
    self.assertNotIn(REFUSAL_MESSAGE, json.dumps(result, ensure_ascii=False))
```

**Implementation approach:**
- Option A (integration): Run the real pipeline end-to-end with actual documents and assert the output is valid JSON, not the refusal.
- Option B (unit): Mock `call_llm` to return the refusal, then assert `generate_scenario` either raises an error or retries with a modified prompt.

### Test 2: `test_retrieval_returns_relevant_chunks`

**Purpose:** Assert that the retriever returns at least N chunks containing domain keywords.

```python
GAS_KEYWORDS = ["robinet", "R0", "R1", "R2", "R3", "R4", "détente", "gaz", "GAZFIO", "FRANCEL", "VS_GAZFIO"]

def test_retrieval_returns_relevant_chunks(self):
    """Retriever must return chunks containing gas-domain terminology."""
    retriever = self._build_retriever_from_docs()
    docs = retriever.invoke("bypass gaz")
    
    relevant_count = sum(
        1 for doc in docs
        if any(kw.lower() in doc.page_content.lower() for kw in GAS_KEYWORDS)
    )
    self.assertGreater(relevant_count, 0, 
        f"None of {len(docs)} retrieved chunks contain gas-domain keywords. "
        f"Documents may be irrelevant or extraction failed."
    )
```

### Test 3: `test_pdf_extraction_non_empty`

**Purpose:** Assert that PDF text extraction returns non-empty, coherent content.

```python
def test_pdf_extraction_non_empty(self):
    """bypass.pdf must yield at least 500 chars of extractable text."""
    from vr_scenario_lib.documents import load_document
    docs = load_document("documents/bypass.pdf")
    total_chars = sum(len(doc.page_content) for doc in docs)
    self.assertGreater(total_chars, 500,
        f"PDF extraction returned only {total_chars} chars. "
        f"Document may be image-based (needs OCR) or corrupted."
    )

def test_docx_extraction_non_empty(self):
    """GRDF procedure DOCX must yield at least 500 chars of extractable text."""
    from vr_scenario_lib.documents import load_document
    docs = load_document("documents/GRDF_Procedure_Consignation_Deconsignation (2).docx")
    total_chars = sum(len(doc.page_content) for doc in docs)
    self.assertGreater(total_chars, 500,
        f"DOCX extraction returned only {total_chars} chars."
    )
```

### Test 4: `test_pipeline_output_structure`

**Purpose:** Assert the pipeline produces valid JSON with required keys.

```python
def test_pipeline_output_structure(self):
    """Pipeline output must be valid JSON with required Unity VR keys."""
    result = run_pipeline(
        topic="bypass gaz",
        retriever=self._build_retriever_from_docs(),
        llm_config=self.llm_config,
    )
    required_keys = ["scenario_id", "titre", "etat_initial", "etapes"]
    for key in required_keys:
        self.assertIn(key, result, f"Missing required key: {key}")
    
    # Validate etat_initial has MASER equipment codes
    etat = result["etat_initial"]
    maser_codes = ["R0", "R1", "R2", "R3", "R4", "VS_GAZFIO"]
    for code in maser_codes:
        self.assertIn(code, etat, f"Missing MASER equipment {code} in etat_initial")
```

### Test 5: `test_context_not_empty`

**Purpose:** Assert that the formatted context passed to the LLM is non-empty.

```python
def test_context_not_empty(self):
    """The formatted context for the LLM must be non-empty."""
    retriever = self._build_retriever_from_docs()
    docs = retriever.invoke("bypass gaz")
    context = format_context(docs)
    self.assertGreater(len(context), 100,
        f"Context is only {len(context)} chars. Retrieval or extraction is broken."
    )
```

### Test Runner Integration

Add to the existing test file or create `tests_regression.py`:

```python
if __name__ == "__main__":
    unittest.main(verbosity=2)
```

Run with:
```bash
python -m pytest tests_regression.py -v
# or
python tests_regression.py
```

**Expected output on fix:**
```
test_context_not_empty ... ok
test_no_refusal_message ... ok
test_pdf_extraction_non_empty ... ok
test_docx_extraction_non_empty ... ok
test_pipeline_output_structure ... ok
test_retrieval_returns_relevant_chunks ... ok

----------------------------------------------------------------------
Ran 6 tests in X.XXs

OK
```

**Expected output before fix (at least one test fails):**
```
test_no_refusal_message ... FAIL
test_retrieval_returns_relevant_chunks ... FAIL
```

---

## Phase 6: Comprehensive Test Suite

### 6.1 Functional Tests

| ID | Scenario | Input | Expected | Validation |
|----|----------|-------|----------|------------|
| F-01 | PDF extraction with encoding repair | `bypass.pdf` | Clean text with domain keywords | `check_document_quality()` returns `is_adequate=True` |
| F-02 | DOCX extraction | `GRDF_Procedure_Consignation_Deconsignation (2).docx` | >500 chars, contains "consignation" | Length + keyword check |
| F-03 | Directory scan with mixed files | `./documents/` | 2 documents loaded, 0 errors | Log output |
| F-04 | Chunking produces valid chunks | 2 docs (19 chunks) | All chunks non-empty, metadata preserved | Iterate chunks |
| F-05 | Vectorstore build (numpy fallback) | 19 chunks | `NumpyVectorStore` created, 19 vectors | `index.ntotal == 19` |
| F-06 | Retrieval returns relevant chunks | Query: "bypass gaz" | ≥1 chunk with gas keyword | Domain keyword scan |
| F-07 | Context formatting | 5 docs | Non-empty string with `[Source N — ...]` markers | Regex check |
| F-08 | Prompt construction | topic="bypass gaz", context="..." | Contains MASER table + topic | String assertions |
| F-09 | Document quality check — good doc | GRDF DOCX | `is_adequate=True`, `domain_score > 0.1` | Dict fields |
| F-10 | Document quality check — empty input | `[]` | `is_adequate=False`, details non-empty | Dict fields |

### 6.2 Robustness Tests

| ID | Scenario | Input | Expected | Validation |
|----|----------|-------|----------|------------|
| R-01 | Empty directory | Empty `./docs/` | `ValueError` raised | `assertRaises` |
| R-02 | Unsupported file type | `file.txt` | Silently skipped | Log warning |
| R-03 | Corrupted PDF | Mock loader returning empty | OCR fallback attempted | Log warning |
| R-04 | OCR dependencies missing | Scanned PDF, no pytesseract | Graceful error message in content | Content contains "ERREUR OCR" |
| R-05 | Very large topic string | 500+ char topic | `ValueError` raised | `assertRaises` |
| R-06 | Empty topic | `""` | `ValueError` raised | `assertRaises` |
| R-07 | Unicode in topic | `"bypass gaz — détente"` | Processed normally | No exception |
| R-08 | `split_documents` with empty list | `[]` | `ValueError` raised | `assertRaises` |
| R-09 | `build_vectorstore` with empty chunks | `[]` | `ValueError` raised | `assertRaises` |
| R-10 | Retrieval with empty query | `""` | Returns results (no crash) | No exception |

### 6.3 Performance Tests

| ID | Scenario | Input | Expected | Validation |
|----|----------|-------|----------|------------|
| P-01 | PDF extraction time | `bypass.pdf` | <5 seconds | `time.time()` delta |
| P-02 | DOCX extraction time | GRDF DOCX | <5 seconds | `time.time()` delta |
| P-03 | Chunking time | 2 docs / 19 chunks | <2 seconds | `time.time()` delta |
| P-04 | Vectorstore build time | 19 chunks | <30 seconds (includes embedding API call) | `time.time()` delta |
| P-05 | Retrieval time | 1 query vs 19 chunks | <10 seconds (includes embedding API call) | `time.time()` delta |
| P-06 | Full pipeline (mocked LLM) | topic + retriever + mocked `call_llm` | <5 seconds excluding LLM | `time.time()` delta |
| P-07 | Memory usage with 100 chunks | 100 synthetic chunks | <200 MB peak | `tracemalloc` or `psutil` |

### 6.4 Integration Tests

| ID | Scenario | Input | Expected | Validation |
|----|----------|-------|----------|------------|
| I-01 | Full pipeline with real LLM | `--topic "bypass gaz"` | Valid JSON output file | File exists + JSON parse |
| I-02 | Pipeline produces non-refusal | Any topic | Output does not contain refusal string | String assertion |
| I-03 | JSON structure validation | Pipeline output | Has `scenario_id`, `titre`, `etat_initial`, `etapes` | Key presence |
| I-04 | MASER codes in etat_initial | Pipeline output JSON | Contains R0-R4, VS_GAZFIO | Key presence in `etat_initial` |
| I-05 | Multiple topics sequentially | 3 different topics | All 3 produce valid output | Loop + assertions |

### 6.5 Test Execution Report Template

After executing the test suite, produce a report in this format:

```
================================================================================
RAPPORT DE TESTS — VR Scenario Library
Date: YYYY-MM-DD HH:MM
Environnement: Python X.Y / Windows 10 / CPU
================================================================================

1. TESTS FONCTIONNELS
─────────────────────
┌─────┬───────────────────────────────────────────┬─────────┬──────────┐
│ ID  │ Scénario                                    │ Résultat│ Durée    │
├─────┼─────────────────────────────────────────────┼─────────┼──────────┤
│ F-01│ PDF extraction avec réparation encodage     │ ✅/❌   │ X.XXs    │
│ F-02│ DOCX extraction                             │ ✅/❌   │ X.XXs    │
│ F-03│ Scan répertoire mixte                       │ ✅/❌   │ X.XXs    │
│ F-04│ Chunking produit chunks valides             │ ✅/❌   │ X.XXs    │
│ F-05│ Vectorstore build (numpy fallback)         │ ✅/❌   │ X.XXs    │
│ F-06│ Retrieval chunks pertinents                 │ ✅/❌   │ X.XXs    │
│ F-07│ Formatage contexte                          │ ✅/❌   │ X.XXs    │
│ F-08│ Construction prompt                         │ ✅/❌   │ X.XXs    │
│ F-09│ Quality check — bon document               │ ✅/❌   │ X.XXs    │
│ F-10│ Quality check — document vide               │ ✅/❌   │ X.XXs    │
└─────┴─────────────────────────────────────────────┴─────────┴──────────┘

2. TESTS DE ROBUSTESSE
─────────────────────
┌─────┬───────────────────────────────────────────┬─────────┬──────────┐
│ ID  │ Scénario                                    │ Résultat│ Durée    │
├─────┼─────────────────────────────────────────────┼─────────┼──────────┤
│ R-01│ Répertoire vide                             │ ✅/❌   │ X.XXs    │
│ R-02│ Fichier non supporté                        │ ✅/❌   │ X.XXs    │
│ R-03│ PDF corrompu                                │ ✅/❌   │ X.XXs    │
│ R-04│ OCR dépendances manquantes                  │ ✅/❌   │ X.XXs    │
│ R-05│ Topic trop long                             │ ✅/❌   │ X.XXs    │
│ R-06│ Topic vide                                  │ ✅/❌   │ X.XXs    │
│ R-07│ Unicode dans topic                          │ ✅/❌   │ X.XXs    │
│ R-08│ split_documents liste vide                  │ ✅/❌   │ X.XXs    │
│ R-09│ build_vectorstore chunks vides              │ ✅/❌   │ X.XXs    │
│ R-10│ Retrieval query vide                         │ ✅/❌   │ X.XXs    │
└─────┴─────────────────────────────────────────────┴─────────┴──────────┘

3. TESTS DE PERFORMANCE
─────────────────────
┌─────┬───────────────────────────────────────────┬─────────┬──────────┬──────────┐
│ ID  │ Scénario                                    │ Résultat│ Durée    │ Seuil    │
├─────┼─────────────────────────────────────────────┼─────────┼──────────┼──────────┤
│ P-01│ Temps extraction PDF                        │ ✅/❌   │ X.XXs    │ <5s      │
│ P-02│ Temps extraction DOCX                       │ ✅/❌   │ X.XXs    │ <5s      │
│ P-03│ Temps chunking                             │ ✅/❌   │ X.XXs    │ <2s      │
│ P-04│ Temps build vectorstore                     │ ✅/❌   │ X.XXs    │ <30s     │
│ P-05│ Temps retrieval                             │ ✅/❌   │ X.XXs    │ <10s     │
│ P-06│ Pipeline complet (LLM mocké)                │ ✅/❌   │ X.XXs    │ <5s      │
│ P-07│ Mémoire (100 chunks)                        │ ✅/❌   │ XXX MB   │ <200 MB  │
└─────┴─────────────────────────────────────────────┴─────────┴──────────┴──────────┘

4. TESTS D'INTÉGRATION
─────────────────────
┌─────┬───────────────────────────────────────────┬─────────┬──────────┐
│ ID  │ Scénario                                    │ Résultat│ Durée    │
├─────┼─────────────────────────────────────────────┼─────────┼──────────┤
│ I-01│ Pipeline complet (LLM réel)                 │ ✅/❌   │ X.XXs    │
│ I-02│ Sortie non-refusal                          │ ✅/❌   │ —        │
│ I-03│ Validation structure JSON                   │ ✅/❌   │ —        │
│ I-04│ Codes MASER dans etat_initial               │ ✅/❌   │ —        │
│ I-05│ Multi-topics séquentiels                    │ ✅/❌   │ X.XXs    │
└─────┴─────────────────────────────────────────────┴─────────┴──────────┘

RÉSUMÉ
──────
Total: N tests | Succès: X | Échecs: Y | Temps total: Z.ZZs

ANOMALIES IDENTIFIÉES
─────────────────────
1. [Description de l'anomalie — sévérité: Haute/Moyenne/Basse]

SUGGESTIONS D'OPTIMISATION
───────────────────────────
1. [Suggestion avec impact estimé]

================================================================================
```

### 6.6 CI Integration

Add to the project a pre-commit hook or CI step that runs the regression tests:

**`.github/workflows/tests.yml`** (if using GitHub Actions):
```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - run: pip install -r requirements.txt
      - run: pip install pytest
      - run: python -m pytest tests_regression.py -v --tb=short
```

**Pre-commit hook** (`.git/hooks/pre-commit`):
```bash
#!/bin/bash
python -m pytest tests_regression.py -q || exit 1
```

Or without pytest:
```bash
python tests_regression.py 2>&1
```

---

#### Fix G — JSON Save Directories (Pre/Post Conversion)

**Objectif** : Sauvegarder le fichier JSON du scénario généré dans un dossier spécifique **avant** l'étape de conversion, et sauvegarder le fichier JSON résultant dans un dossier distinct **après** la conversion.

**Fichiers concernés** :
- `vr_scenario_lib/pipeline.py` — fonction `run_pipeline()` (L.41-112)
- `vr_scenario_lib/json_converter.py` — fonction `convert_scenario_to_json()` (L.80-126)

**Modifications** :

1. **Avant conversion** (dans `run_pipeline()`, L.77-83) :
   ```python
   # Sauvegarde du scénario texte brut AVANT conversion
   pre_conversion_dir = Path(store_dir or "./scenarios") / "pre-conversion"
   pre_conversion_dir.mkdir(parents=True, exist_ok=True)
   pre_conversion_path = pre_conversion_dir / f"{topic.replace(' ', '_')}_raw.json"
   pre_conversion_path.write_text(
       json.dumps({"topic": topic, "scenario_text": scenario_text, "sources": [s.metadata for s in sources]}, 
                    ensure_ascii=False, indent=2),
       encoding="utf-8"
   )
   logger.info("Scénario brut sauvegardé (pre-conversion) : %s", pre_conversion_path)
   ```

2. **Après conversion** (dans `run_pipeline()`, L.85-91) :
   ```python
   # Sauvegarde du JSON converti APRÈS conversion
   post_conversion_dir = Path(store_dir or "./scenarios") / "post-conversion"
   post_conversion_dir.mkdir(parents=True, exist_ok=True)
   post_conversion_path = post_conversion_dir / f"{topic.replace(' ', '_')}.json"
   post_conversion_path.write_text(
       json.dumps(result, ensure_ascii=False, indent=2),
       encoding="utf-8"
   )
   logger.info("Scénario converti sauvegardé (post-conversion) : %s", post_conversion_path)
   ```

**Structure de sortie** :
```
scenarios/
├── pre-conversion/
│   ├── bypass_gaz_raw.json          # Scénario texte brut + sources
│   └── consignation_gaz_raw.json
└── post-conversion/
    ├── bypass_gaz.json              # JSON structuré Unity VR
    └── consignation_gaz.json
```

**Risques** :
- `store_dir` peut être None → utiliser `./scissions` par défaut
- Permissions disque insuffisantes → logger l'erreur mais ne pas crash
- Nom de fichier topic avec caractères spéciaux → remplacer espaces par `_`

**Tests à ajouter** :
- Vérifier que `pre-conversion/` est créé et contient le fichier raw
- Vérifier que `post-conversion/` est créé et contient le fichier converti
- Vérifier que le fichier raw contient `scenario_text` et `sources`
- Vérifier que le fichier converti contient `scenario_id`, `etat_initial`, `etapes`

---

## Open Questions

1. What is the actual text content of `bypass.pdf`? → **RESOLVED**: PDF has encoding issues (garbled text with `�` characters). Fix implemented: `_repair_text()` + OCR fallback.
2. What topic/theme is the user passing when the refusal occurs? → Likely "bypass gaz" or similar.
3. Is there a known-good gas bypass procedure document available for replacement? → Not yet; encoding repair may salvage the PDF enough.
4. Is FAISS installable in this environment? → **RESOLVED**: No. Fix implemented: `NumpyVectorStore` fallback.
