# Q&R System — Root Cause Analysis & Fix Plan

## Problem

All user questions in the Q&A loop trigger the fallback message:
```
"Je n'ai pas pu obtenir de réponse pour le moment. Vous pouvez reformuler votre question..."
```

Log evidence:
```
Q&R : toutes les stratégies ont échoué — message de repli
```
This appears for **every** question regardless of complexity.

## Pipeline Architecture

```
Q&A Loop (_qa_loop)
  └─ _get_answer(question, scenario_session, config)
       ├─ Strategy 1: _answer_via_custom_fn  → returns None (no fn injected)
       ├─ Strategy 2: _answer_via_library    → calls vr_scenario_lib.scenario.discuss_scenario()
       └─ Strategy 3: _answer_via_direct_llm  → calls _call_llm_raw() → HTTP to LLM API
       └─ Fallback: self.cfg.qa.fallback_message
```

## Identified Root Causes (by order of likely impact)

### RC-1: Library strategy calls `call_llm` with wrong keyword arguments

**Location:** `try_call_llm_via_library()` (line ~17927)

**Code:**
```python
return call_llm(system=system, user=user, llm_config=config, max_tokens=max_tokens)
```

**Actual signature** (in `vr_scenario_lib/llm.py:283`):
```python
def call_llm(system_prompt: str, user_prompt: str, config: LLMConfig, max_tokens: int | None = None)
```

**Result:** `TypeError` on every call → silently caught → falls through to HTTP path.
This affects **all three** strategies because `_call_llm_raw` also uses `try_call_llm_via_library`.

**Previous fix applied:** Changed to `system_prompt=system, user_prompt=user, config=config`.
**Status:** Still needs verification that the `discuss_scenario` path (Strategy 2) actually works end-to-end.

### RC-2: HTTP fallback uses `getattr` on dict-like config objects

**Location:** `perform_chat_http_call()` (line ~17903-17905)

**Code:**
```python
model = getattr(config, "model", endpoint_cfg.default_model)
api_url = getattr(config, "api_url", endpoint_cfg.default_api_url)
token = getattr(config, "token", "")
```

**Problem:** `build_llm_config()` returns `LLMConfig` which is a `TypedDict` (plain dict at runtime). `getattr(dict_obj, "model", default)` returns `default`, not `dict["model"]`.

**Result:** HTTP calls go to `https://api.openai.com/v1/chat/completions` (wrong endpoint) with model `gpt-3.5-turbo` (wrong model) and empty token → 401/403 or similar error.

**Previous fix applied:** Changed to `getattr(..., None) or config.get(...)` pattern.
**Status:** Fix applied, needs integration test.

### RC-3: `_answer_via_library` returns `None` when `scenario_session` is `None`

**Location:** `_answer_via_library` (line 19467)

**Code:**
```python
if scenario_session is None or config is None:
    return None
```

**Cause:** `_generate_and_announce()` returns `None` when scenario generation fails (line 19081). When `scenario_session` is `None`, Strategy 2 returns `None` immediately and cleanly — no exception, no log.

**Impact:** If scenario generation succeeded but the session was somehow lost, this creates silent failures. However, if generation worked, this is NOT the primary cause.

**Not yet addressed in previous fixes.**

### RC-4: `_answer_via_direct_llm` returns `None` when `config` is `None`

**Location:** `_answer_via_direct_llm` (line 19484)

**Code:**
```python
if config is None:
    return None
```

**Cause:** `_setup_llm()` returns `None` when `build_llm_config()` raises (no API key). This is clean and intentional — but combined with RC-1 and RC-2, the cascading `None` returns make ALL strategies fail silently.

**Impact:** If `OPENROUTER_API_KEY` is not set in `.env`, the entire pipeline is dead.

### RC-5: No exception traceback in early log output

**Observation:** The logs show clean `WARNING | Q&R : toutes les stratégies ont échoué` with **no preceding exception logs** from the individual strategies. This means strategies are returning `None` cleanly, not raising exceptions.

**Root cause:** The strategies catch all exceptions internally and return `None`:
- `_answer_via_library`: `except Exception as exc: logger.warning("discuss_scenario erreur : %s", exc)` 
- `_answer_via_direct_llm`: `except Exception as exc: logger.error("Appel direct Q&R erreur : %s", exc)`

But wait — the logs from the user's session show NO "discuss_scenario erreur" or "Appel direct Q&R erreur" lines. This means:
- Strategy 2 (`_answer_via_library`) returns `None` at the guard check (`scenario_session is None or config is None`)
- Strategy 3 (`_answer_via_direct_llm`) also returns `None` at its guard check

This proves **both `scenario_session` and/or `config` are `None` at runtime**.

## Tasks

### [ ] Task 1 (already done): Fix `try_call_llm_via_library` kwargs
Changed `system=`/`user=`/`llm_config=` to `system_prompt=`/`user_prompt=`/`config=`.

### [ ] Task 2 (already done): Fix `perform_chat_http_call` getattr
Changed to `getattr(..., None) or config.get(...)` pattern.

### [ ] Task 3 (already done): Add error logging in `_get_answer`
Added per-strategy debug logging and `exc_info=True` to exception handlers.

### [ ] Task 4 (NEW): Diagnose why config is None at runtime
Add explicit diagnostic at `_qa_loop` entry:
```python
logger.info("_qa_loop: scenario_session=%s, config=%s", 
            type(scenario_session).__name__, 
            "SET" if config else "NONE")
```

### [ ] Task 5 (NEW): Add guard in `_answer_via_library` for None session with logging
```python
if scenario_session is None:
    logger.warning("_answer_via_library: scenario_session is None — cannot use library strategy")
    return None
if config is None:
    logger.warning("_answer_via_library: config is None — cannot use library strategy")
    return None
```

### [ ] Task 6 (NEW): Add guard in `_answer_via_direct_llm` for None config/None session
```python
if config is None:
    logger.warning("_answer_via_direct_llm: config is None — cannot call LLM")
    return None
```

### [ ] Task 7 (NEW): Verify `.env` loading at application startup
Add config presence log before `_qa_loop`:
```python
config = self._setup_llm()
if config is None:
    self.io.speak("Attention : la configuration LLM n'a pas été chargée. 
                   Vérifiez votre fichier .env avec OPENROUTER_API_KEY.")
```

## Risks
- RC-1 and RC-2 are cosmetic if the primary issue is RC-4 (missing API key)
- If the API key IS set but the HTTP call fails due to RC-2, the user gets no feedback
- Fixing RC-1/RC-2 without confirming the key is set won't resolve the issue

## Validation

1. Run the app with a valid `.env` containing `OPENROUTER_API_KEY=sk-or-...`
2. Check startup log: `CONFIG LLM` should show the configured model/token
3. Ask a question — logs should show:
   - `_qa_loop: ... config=SET`
   - Either "réponse obtenue via _answer_via_library" or "réponse obtenue via _answer_via_direct_llm"
4. TTS should speak the LLM response, not the fallback

## Open Questions
- Is `OPENROUTER_API_KEY` actually set in the user's `.env` file?
- Did the user run `pip install python-dotenv`?
- Is the `.env` file in the correct directory (project root)?
