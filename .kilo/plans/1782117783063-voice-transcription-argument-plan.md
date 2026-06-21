# Plan: Voice transcription as argument to `generate_scenario` + API key verification

## Context (verified)

- `.env` confirmed at `vr_scenario_lib/.env` (4914 bytes, contains `OPENROUTER_API_KEY=sk-or-v1-...` on line 12)
- `config.py` at `vr_scenario_lib/vr_scenario_lib/config.py` — `Path(__file__).resolve().parent.parent` = `vr_scenario_lib/` → `.env` path is correct
- `load_dotenv(dotenv_path=str(_ENV_FILE), override=True)` is called at module import time (line 21) → `os.environ.get("OPENROUTER_API_KEY")` in `build_llm_config` will read the correct value
- The active `VRScenarioApp._generate_scenario` (line 19097) calls `lib_generate(topic=topic, llm_config=config)` — missing `retriever` arg
- The active `run()` (line 18945) flows: `_ask_topic()` → returns topic string from STT → `_generate_and_announce(topic, config)`
- `call_with_retry` (line 17850) retries on `(urllib.error.URLError, TimeoutError, ValueError, KeyError)` — `HTTPError` is a subclass of `URLError` so 401 IS retried (wastes retries on non-retryable error)

## Tasks

### 1. `vr_scenario_lib/scenario.py` — Make `retriever` optional + add `transcription` param

**`generate_scenario` signature (line 53):**
```python
def generate_scenario(
    topic: str,
    retriever: VectorStoreRetriever | None = None,
    llm_config: LLMConfig,
    custom_prompt: str = "",
    transcription: str = "",
) -> tuple[str, list[Document]]:
```

**Body changes:**
- When `retriever is None`: skip `retrieve_context` + `format_context`, set `context = ""`
- When `transcription` is non-empty: append it to the user prompt after the context block:
  ```
  TRANSCRIPTION VOCALE DE L'UTILISATEUR :
  {transcription}
  ```
- Return `(scenario_text, [])` when retriever is None (already returns `docs` which would be `[]`)

### 2. `scenario_conversation_app_vocal_only_fixed.py` — Pass transcription through

**`run()` (line 18945):**
- `_ask_topic()` already returns the STT transcription → rename variable to `topic` (unchanged), pass it as `transcription` to `_generate_and_announce`

**`_generate_and_announce` (line 19063):**
- Add `transcription: str = ""` parameter
- Forward to `_run_scenario_generation(topic, config, transcription=transcription)`

**`_run_scenario_generation` (line 19087):**
- Add `transcription: str = ""` parameter
- Forward to `self._generate_scenario(topic, config, transcription=transcription)`

**`_generate_scenario` (line 19097):**
- Add `transcription: str = ""` parameter
- Change call: `lib_generate(topic=topic, llm_config=config, transcription=transcription)`
- Remove the `retriever` error from the except block's caught exception — the `TypeError` for missing `retriever` will no longer occur since `retriever` is now optional. Keep the broad `except Exception` for other failures (network, etc.)

### 3. Preserve retry — no changes needed

- `call_with_retry` (line 17850): unchanged
- `_call_llm_single_model` in `vr_scenario_lib/llm.py` (line 199): unchanged — retries on 429/5xx, raises immediately on 401/403 (non-retryable). This is correct behavior.

### 4. `config.py` — `getenv` verification (no change needed)

- `_PROJECT_ROOT = Path(__file__).resolve().parent.parent` → `vr_scenario_lib/`
- `_ENV_FILE = _PROJECT_ROOT / ".env"` → `vr_scenario_lib/.env` ✓
- `load_dotenv(dotenv_path=str(_ENV_FILE), override=True)` called at import → `os.environ` populated before `build_llm_config` is called
- `os.environ.get("OPENROUTER_API_KEY")` on line 131 reads correctly from the `.env` file
- **No code change required** — verified correct.

### 5. `vr_scenario_lib/pipeline.py` — No change needed

- `run_pipeline` (line 41) calls `generate_scenario(topic, retriever, llm_config, custom_prompt=custom_prompt)` — `retriever` is still passed positionally, so backward compatible.

### 6. `vr_scenario_lib/__init__.py` — No change needed

- `generate_scenario` is already exported; signature change is backward compatible (new params have defaults).

## Risks

| Risk | Mitigation |
|------|-----------|
| `retriever=None` + `transcription=""` → empty prompt | `build_scenario_prompt` handles empty context; topic alone is sufficient for LLM |
| `transcription` contains more than the topic (user speaks freely) | Good — richer input for the LLM, no truncation needed |
| Other callers of `generate_scenario` break | `pipeline.py` passes `retriever` positionally — unchanged. All other callers in the codebase either commented out or use the voice app path |

## Validation

1. `python -c "from vr_scenario_lib import generate_scenario; print('OK')"` — library imports
2. `python -c "from vr_scenario_lib.config import build_llm_config; c = build_llm_config(); print(c['token'][:8])"` — API key loaded from `.env`
3. `python -c "from vr_scenario_lib.scenario import generate_scenario; from vr_scenario_lib.config import build_llm_config; cfg = build_llm_config(); print('retriever optional:', generate_scenario('test', llm_config=cfg)[0][:50])"` — retriever=None works
4. Voice app text mode: `python scenario_conversation_app_vocal_only_fixed.py --text` — no `missing 1 required positional argument` warning

## Open questions

None.
