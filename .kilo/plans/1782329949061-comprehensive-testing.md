# Plan: Comprehensive Testing Plan — VR Scenario Library

## Objectives

1. **Validate all recent fixes** (A-H) work correctly in isolation and integration
2. **Ensure no regressions** in existing functionality (42 existing tests still pass)
3. **Cover new code**: `_save_pre_conversion`, `_save_post_conversion`, `organize_json.py`
4. **Verify edge cases**: empty inputs, invalid JSON, permissions, large files
5. **Document defects** with severity and reproduction steps

## Test Environment

| Component | Version |
|-----------|---------|
| Python | 3.14.6 |
| OS | Windows 10 |
| pytest | 9.1.0 |
| Working directory | `vr_scenario_lib/` |

## Mocking Strategy

### For Pipeline Tests (Fix G)

```python
from unittest.mock import MagicMock, patch
from vr_scenario_lib.pipeline import _save_pre_conversion, _save_post_conversion, run_pipeline

# Mock LLM to avoid API calls
mock_llm_config = {
    "model": "test-model",
    "api_url": "http://localhost",
    "token": "test-token",
    "max_tokens": 100,
    "temperature": 0.3,
    "timeout": 10,
    "max_retries": 1,
    "retry_backoff_factor": 1.0,
    "fallback_models": [],
}

# Mock retriever
mock_retriever = MagicMock()
mock_retriever.invoke.return_value = [
    Document(page_content="test gaz procedure", metadata={"source": "test.pdf"})
]
```

### For organize_json.py Tests (Fix H)

```python
import tempfile
import json
from pathlib import Path

# Use tmp_path fixture (pytest built-in)
def test_classify_config(tmp_path):
    config_file = tmp_path / "config.json"
    config_file.write_text(json.dumps({"model": "llama", "api_url": "http://..."}))
    obj = load_json(config_file)
    assert classify_json(obj) == "config"
```

### Key Mock Points

| Component | Mock Target | Reason |
|-----------|-------------|--------|
| LLM calls | `vr_scenario_lib.scenario.call_llm` | Avoid API costs |
| Embeddings | `vr_scenario_lib.vectorstore.create_embeddings` | Avoid model loading |
| File system | `Path.write_text` | Test error handling |
| `os.walk` | `os.walk` | Control directory structure |

---

## Test Execution Commands

```bash
# Run all tests
python -m pytest tests_validation.py tests_regression.py tests_new.py -v --tb=short

# Run specific test file
python -m pytest tests_new.py -v

# Run with coverage
python -m pytest tests_validation.py tests_regression.py tests_new.py --cov=vr_scenario_lib --cov-report=term-missing

# Run specific test class
python -m pytest tests_new.py::TestOrganizeJson -v

# Run specific test
python -m pytest tests_new.py::TestOrganizeJson::test_classify_config -v
```

---

## Test Suite 1: Pipeline JSON Save Directives (Fix G)

### Test G-1: `test_save_pre_conversion_creates_file`

**Objective**: Verify that `_save_pre_conversion()` creates a file in `pre-conversion/`

**Steps**:
1. Create temp `store_dir`
2. Call `_save_pre_conversion("test topic", "scenario text", [], store_dir)`
3. Assert `store_dir/pre-conversion/test_topic_raw.json` exists
4. Assert JSON contains `{"topic": "test topic", "scenario_text": "scenario text", "sources": []}`

**Expected**: File created with correct structure

---

### Test G-2: `test_save_post_conversion_creates_file`

**Objective**: Verify that `_save_post_conversion()` creates a file in `post-conversion/`

**Steps**:
1. Create temp `store_dir`
2. Call `_save_post_conversion("test topic", {"scenario_id": "test", "etapes": []}, store_dir)`
3. Assert `store_dir/post-conversion/test_topic.json` exists
4. Assert JSON matches input dict

**Expected**: File created with correct content

---

### Test G-3: `test_save_pre_conversion_with_none_store_dir`

**Objective**: Verify default path when `store_dir=None`

**Steps**:
1. Call `_save_pre_conversion("topic", "text", [], None)`
2. Assert `./scenarios/pre-conversion/topic_raw.json` exists
3. Cleanup

**Expected**: Uses default `./scenarios` path

---

### Test G-4: `test_save_post_conversion_with_none_store_dir`

**Objective**: Verify default path when `store_dir=None`

**Steps**:
1. Call `_save_post_conversion("topic", {"scenario_id": "x"}, None)`
2. Assert `./scenarios/post-conversion/topic.json` exists
3. Cleanup

**Expected**: Uses default `./scenarios` path

---

### Test G-5: `test_save_pre_conversion_with_sources`

**Objective**: Verify sources metadata is serialized correctly

**Steps**:
1. Create sources list: `[Document(page_content="test", metadata={"source": "doc1.pdf"})]`
2. Call `_save_pre_conversion("topic", "text", sources, store_dir)`
3. Load JSON, assert `sources[0].metadata.source == "doc1.pdf"`

**Expected**: Sources metadata preserved

---

### Test G-6: `test_save_pre_conversion_special_chars_in_topic`

**Objective**: Verify topic sanitization

**Steps**:
1. Call with topic `"bypass gaz/poste GAZFIO"`
2. Assert filename uses underscores, no slashes

**Expected**: `bypass_gaz_poste_GAZFIO_raw.json`

---

### Test G-7: `test_save_does_not_crash_on_permission_error`

**Objective**: Verify graceful handling of disk errors

**Steps**:
1. Mock `Path.write_text` to raise `OSError`
2. Call `_save_pre_conversion()`
3. Assert no exception raised, warning logged

**Expected**: Warning logged, no crash

---

### Test G-8: `test_run_pipeline_saves_both_files`

**Objective**: Integration test — full pipeline saves pre and post files

**Steps**:
1. Mock `generate_scenario` to return `("text", [])`
2. Mock `convert_scenario_to_json` to return `{"scenario_id": "x", "etapes": []}`
3. Call `run_pipeline("test", retriever_mock, llm_config_mock, store_dir=tmpdir)`
4. Assert both `pre-conversion/test_raw.json` and `post-conversion/test.json` exist

**Expected**: Both files created in correct directories

---

## Test Suite 2: organize_json.py (Fix H)

### Test H-1: `test_classify_config_by_keys`

**Objective**: Verify config classification by key patterns

**Input**: `{"model": "llama", "api_url": "http://...", "temperature": 0.3}`

**Expected**: Returns `"config"`

---

### Test H-2: `test_classify_data_by_keys`

**Objective**: Verify data classification by key patterns

**Input**: `{"scenario_id": "test", "etapes": [...], "titre": "Test"}`

**Expected**: Returns `"data"`

---

### Test H-3: `test_classify_data_by_long_text`

**Objective**: Verify data classification by long text content

**Input**: `{"text": "a" * 150}`

**Expected**: Returns `"data"`

---

### Test H-4: `test_classify_unknown_for_none`

**Objective**: Verify unknown for None input (invalid JSON)

**Input**: `None`

**Expected**: Returns `"unknown"`

---

### Test H-5: `test_classify_list_of_objects`

**Objective**: Verify list of dicts classified as data

**Input**: `[{"id": 1}, {"id": 2}]`

**Expected**: Returns `"data"`

---

### Test H-6: `test_classify_config_primitives_only`

**Objective**: Verify dict with all primitive values classified as config

**Input**: `{"host": "localhost", "port": 8080, "debug": true}`

**Expected**: Returns `"config"`

---

### Test H-7: `test_load_json_valid`

**Objective**: Verify loading valid JSON file

**Steps**: Create temp file `{"key": "value"}`, load it

**Expected**: Returns `{"key": "value"}`

---

### Test H-8: `test_load_json_invalid`

**Objective**: Verify graceful handling of invalid JSON

**Steps**: Create temp file `{invalid json`, load it

**Expected**: Returns `None`, warning logged

---

### Test H-9: `test_load_json_missing_file`

**Objective**: Verify handling of non-existent file

**Steps**: Call `load_json(Path("/nonexistent/file.json"))`

**Expected**: Returns `None`, warning logged

---

### Test H-10: `test_scan_json_files_finds_json`

**Objective**: Verify scanner finds .json files

**Steps**: Create temp dir with `.json`, `.txt`, `.py` files

**Expected**: Returns only `.json` files

---

### Test H-11: `test_scan_json_files_respects_depth`

**Objective**: Verify depth parameter

**Steps**: Create nested structure with depth=1 vs depth=0

**Expected**: depth=0 returns root only, depth=1 returns root + 1 level

---

### Test H-12: `test_organize_dry_run_no_changes`

**Objective**: Verify dry-run mode doesn't modify filesystem

**Steps**: Run `organize(source, dest, dry_run=True)`, check dest doesn't exist

**Expected**: No files created/moved

---

### Test H-13: `test_organize_copies_files`

**Objective**: Verify organize copies (not moves) by default

**Steps**: Run `organize(source, dest)`, check source still has files

**Expected**: Source unchanged, dest has copies

---

### Test H-14: `test_organize_moves_files`

**Objective**: Verify organize moves when `--move` flag

**Steps**: Run `organize(source, dest, move=True)`, check source is empty

**Expected**: Source empty, dest has files

---

### Test H-15: `test_organize_handles_name_conflict`

**Objective**: Verify auto-renaming on filename conflict

**Steps**: Create `dest/config/file.json`, then organize with same filename

**Expected**: Creates `file_1.json`

---

### Test H-16: `test_organize_creates_correct_directories`

**Objective**: Verify output directory structure

**Steps**: Run organize on mixed config/data files

**Expected**: `dest/config/`, `dest/data/`, `dest/unknown/` created as needed

---

### Test H-17: `test_organize_empty_source_directory`

**Objective**: Verify handling of empty source

**Steps**: Run organize on empty dir

**Expected**: Returns empty classification, no crash

---

### Test H-18: `test_organize_source_equals_dest`

**Objective**: Verify error when source == dest

**Steps**: Run `organize(dir, dir)`

**Expected**: Error message, exit code != 0

---

### Test H-19: `test_clify_config_with_data_keys_ambiguous`

**Objective**: Verify priority when both config and data keys present

**Input**: `{"model": "x", "scenario_id": "y"}` (1 config, 1 data)

**Expected**: Returns `"data"` (data key has priority when config_score < 2)

---

### Test H-20: `test_has_long_text_nested`

**Objective**: Verify recursive text detection in nested structures

**Input**: `{"level1": {"text": "a" * 150}}`

**Expected**: Returns `True`

---

## Test Suite 3: Regression Tests (Existing)

### Test R-1: `test_no_refusal_message`

**Objective**: Ensure LLM refusal instruction is removed from SYSTEM_SCENARIO

**Expected**: `SYSTEM_SCENARIO` does not contain the French refusal string

---

### Test R-2: `test_pipeline_output_structure`

**Objective**: Validate JSON output has required Unity VR keys

**Expected**: Contains `scenario_id`, `titre`, `etat_initial`, `etapes`

---

### Test R-3: `test_encoding_repair_garbage_chars`

**Objective**: Verify `_repair_text()` fixes garbled PDF text

**Input**: `"d�tente"`

**Expected**: Returns `"détente"`

---

### Test R-4: `test_numpy_vectorstore_build_and_search`

**Objective**: Verify fallback vectorstore works

**Steps**: Build from 3 documents, search

**Expected**: Returns relevant results

---

### Test R-5: `test_empty_directory_raises_error`

**Objective**: Verify `scan_directory()` raises ValueError on empty dir

**Expected**: `ValueError` raised

---

## Test Suite 4: Performance Tests

### Test P-1: `test_pdf_extraction_under_5s`

**Expected**: PDF extraction completes in <5 seconds

---

### Test P-2: `test_docx_extraction_under_5s`

**Expected**: DOCX extraction completes in <5 seconds

---

### Test P-3: `test_chunking_under_2s`

**Expected**: 19 chunks from 2 docs in <2 seconds

---

### Test P-4: `test_vectorstore_build_under_60s`

**Expected**: Build with mocked embeddings in <60 seconds

---

### Test P-5: `test_organize_100_files_under_10s`

**Objective**: Performance test for organize_json.py

**Steps**: Create 100 JSON files, run organize

**Expected**: Completes in <10 seconds

---

## Test Suite 5: Edge Cases

### Test E-1: `test_save_pre_conversion_with_empty_scenario_text`

**Objective**: Verify handling of empty scenario text

**Steps**: Call with `scenario_text=""`

**Expected**: File created with empty text field

---

### Test E-2: `test_save_post_conversion_with_empty_result`

**Objective**: Verify handling of empty result dict

**Steps**: Call with `result={}`

**Expected**: File created with empty dict

---

### Test E-3: `test_organize_with_binary_file_named_json`

**Objective**: Verify handling of non-JSON file with .json extension

**Steps**: Create binary file named `test.json`

**Expected**: Classified as `unknown`, skipped gracefully

---

### Test E-4: `test_organize_with_very_large_json`

**Objective**: Verify handling of large JSON files

**Steps**: Create 10MB JSON file

**Expected**: Classified correctly, no memory issues

---

### Test E-5: `test_organize_with_unicode_filenames`

**Objective**: Verify handling of Unicode in filenames

**Steps**: Create file `données_é.json`

**Expected**: Classified and copied correctly

---

### Test E-6: `test_save_with_very_long_topic_name`

**Objective**: Verify topic truncation

**Steps**: Call with topic of 200 characters

**Expected**: Filename truncated to 50 chars

---

## Known Risks in Current Implementation

### Risk 1: `has_long_text()` Recursion Depth

**Location**: `organize_json.py:64-76`

The `has_long_text()` function uses recursion without depth limit. A deeply nested JSON structure (>1000 levels) could hit Python's recursion limit.

**Mitigation**: Test with deeply nested JSON (Test E-10). If issue found, convert to iterative approach with explicit stack.

### Risk 2: `_save_pre_conversion` Sources Serialization

**Location**: `pipeline.py:142`

```python
"sources": [s.metadata if hasattr(s, "metadata") else {"source": str(s)} for s in sources],
```

If `sources` contains objects without `metadata` attribute and whose `str()` is not informative, the output may be unhelpful.

**Mitigation**: Test with various source types (Test G-5).

### Risk 3: `organize_json.py` — `scan_json_files` Infinite Recursion

**Location**: `organize_json.py:107-123`

With `depth=-1` (default), circular symlinks could cause infinite recursion.

**Mitigation**: Test with symlinks (Test E-7). Consider adding `followlinks=False` or visited set.

### Risk 4: `classify_json` — `all()` on Large Dicts

**Location**: `organize_json.py:95`

```python
if all(isinstance(v, (str, int, float, bool, type(None))) for v in obj.values()):
```

For dicts with millions of values, this iterates all values. Acceptable for typical JSON files.

---

## Defect Tracking Template

| ID | Severity | Test Case | Description | Reproduction | Status |
|----|----------|-----------|-------------|--------------|--------|
| D-1 | Critical | | | | Open |
| D-2 | High | | | | Open |
| D-3 | Medium | | | | Open |
| D-4 | Low | | | | Open |

## Severity Definitions

- **Critical**: Data loss, crash, security vulnerability
- **High**: Feature broken, no workaround
- **Medium**: Feature degraded, workaround exists
- **Low**: Cosmetic, minor inconvenience

## Test Report Summary

| Suite | Total | Pass | Fail | Skip | Coverage Target |
|-------|-------|------|------|------|-----------------|
| Pipeline JSON Save (G) | 8 | | | | 90% |
| organize_json.py (H) | 20 | | | | 85% |
| Regression (R) | 5 | | | | 95% |
| Performance (P) | 5 | | | | N/A |
| Edge Cases (E) | 15 | | | | 80% |
| **Total** | **53** | | | | **85% overall** |

## Coverage Targets

| Module | Target | Priority |
|--------|--------|----------|
| `pipeline.py` | 90% | High |
| `organize_json.py` | 85% | High |
| `documents.py` | 85% | Medium |
| `vectorstore.py` | 80% | Medium |
| `config.py` | 70% | Low |
| `llm.py` | 75% | Medium |

```bash
# Generate coverage report
python -m pytest tests_new.py tests_validation.py tests_regression.py \
    --cov=vr_scenario_lib \
    --cov-report=term-missing \
    --cov-report=html:coverage_html

# Check specific module coverage
python -m pytest tests_new.py --cov=vr_scenario_lib.pipeline --cov-report=term-missing
```

## Acceptance Criteria

- [ ] All 53 new tests pass
- [ ] All 79 existing tests still pass (42 validation + 37 regression)
- [ ] No regression in existing functionality
- [ ] Coverage targets met for priority modules
- [ ] No Critical or High severity defects open
- [ ] All Medium defects documented with workaround
- [ ] Performance thresholds met on reference hardware

## Execution Steps

1. Create `tests_new.py` with all test cases
2. Run: `python -m pytest tests_new.py -v --tb=short`
3. Run: `python -m pytest tests_validation.py tests_regression.py -v --tb=short`
4. Fix any failures
5. Generate coverage report
6. Document defects
7. Produce final report

## Open Questions

1. Should performance thresholds be adjusted for CI environments (slower machines)?
2. Should we add integration tests with real LLM API calls (requires API key)?
3. Should organize_json.py tests clean up temp files or use `tmp_path` fixture exclusively?
