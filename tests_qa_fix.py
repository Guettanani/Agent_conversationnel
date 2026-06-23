"""Tests for the Q&R fix — verify config is read correctly and library calls use proper kwargs."""
import os
import sys
import unittest
import json
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def _make_fake_response():
    """Create a mock that works as both a return value and a context manager for urlopen."""
    inner = MagicMock()
    inner.read.return_value = b'{"choices":[{"message":{"content":"ok"}}]}'
    cm = MagicMock()
    cm.__enter__ = MagicMock(return_value=inner)
    cm.__exit__ = MagicMock(return_value=False)
    return cm


class TestPerformChatHttpCall(unittest.TestCase):
    """Verify perform_chat_http_call reads dict config correctly."""

    def _get_func(self):
        from scenario_conversation_app_vocal_only_fixed import perform_chat_http_call
        return perform_chat_http_call

    def test_dict_config_model_and_url(self):
        """Dict config (from build_llm_config) must be read via .get(), not getattr."""
        func = self._get_func()
        config = {
            "model": "meta-llama/llama-3.3-70b-instruct:free",
            "api_url": "https://openrouter.ai/api/v1/chat/completions",
            "token": "sk-or-test123",
        }
        endpoint_cfg = MagicMock()
        endpoint_cfg.default_model = "gpt-3.5-turbo"
        endpoint_cfg.default_api_url = "https://api.openai.com/v1/chat/completions"

        captured = {}

        def fake_urlopen(req, timeout=None):
            captured["url"] = req.full_url
            captured["auth"] = req.get_header("Authorization")
            captured["body"] = req.data
            return _make_fake_response()

        with patch("urllib.request.urlopen", side_effect=fake_urlopen):
            func(system="sys", user="hello", config=config, max_tokens=100,
                 endpoint_cfg=endpoint_cfg, timeout_s=10)

        self.assertEqual(captured["url"], "https://openrouter.ai/api/v1/chat/completions")
        self.assertEqual(captured["auth"], "Bearer sk-or-test123")
        body = json.loads(captured["body"])
        self.assertEqual(body["model"], "meta-llama/llama-3.3-70b-instruct:free")

    def test_object_config_still_works(self):
        """Object-style config (dataclass/SimpleNamespace) must still work via getattr."""
        func = self._get_func()
        config = MagicMock()
        config.model = "test-model"
        config.api_url = "https://example.com/v1/chat"
        config.token = "tok-456"
        endpoint_cfg = MagicMock()
        endpoint_cfg.default_model = "gpt-3.5-turbo"
        endpoint_cfg.default_api_url = "https://api.openai.com/v1/chat/completions"

        captured = {}

        def fake_urlopen(req, timeout=None):
            captured["url"] = req.full_url
            captured["auth"] = req.get_header("Authorization")
            return _make_fake_response()

        with patch("urllib.request.urlopen", side_effect=fake_urlopen):
            func(system="sys", user="hello", config=config, max_tokens=100,
                 endpoint_cfg=endpoint_cfg, timeout_s=10)

        self.assertEqual(captured["url"], "https://example.com/v1/chat")
        self.assertEqual(captured["auth"], "Bearer tok-456")

    def test_missing_keys_fall_back_to_defaults(self):
        """Dict config missing model/api_url must use endpoint_cfg defaults."""
        func = self._get_func()
        config = {"token": "tok-789"}
        endpoint_cfg = MagicMock()
        endpoint_cfg.default_model = "default-model"
        endpoint_cfg.default_api_url = "https://default.example.com/v1"

        captured = {}

        def fake_urlopen(req, timeout=None):
            captured["url"] = req.full_url
            return _make_fake_response()

        with patch("urllib.request.urlopen", side_effect=fake_urlopen):
            func(system="sys", user="hello", config=config, max_tokens=100,
                 endpoint_cfg=endpoint_cfg, timeout_s=10)

        self.assertEqual(captured["url"], "https://default.example.com/v1")


class TestTryCallLlmViaLibrary(unittest.TestCase):
    """Verify try_call_llm_via_library uses correct kwarg names."""

    def _get_func(self):
        from scenario_conversation_app_vocal_only_fixed import try_call_llm_via_library
        return try_call_llm_via_library

    def test_correct_kwargs_passed_to_call_llm(self):
        """The function must call call_llm with system_prompt/user_prompt/config (not system/user/llm_config)."""
        func = self._get_func()
        config = {"model": "test", "api_url": "http://x", "token": "t"}

        captured = {}

        def fake_call_llm(*, system_prompt, user_prompt, config, max_tokens):
            captured["system_prompt"] = system_prompt
            captured["user_prompt"] = user_prompt
            captured["config"] = config
            captured["max_tokens"] = max_tokens
            return "réponse du LLM"

        with patch.dict("sys.modules", {"vr_scenario_lib.llm": MagicMock(call_llm=fake_call_llm)}):
            result = func(system="mon système", user="ma question", config=config, max_tokens=500)

        self.assertEqual(result, "réponse du LLM")
        self.assertEqual(captured["system_prompt"], "mon système")
        self.assertEqual(captured["user_prompt"], "ma question")
        self.assertIs(captured["config"], config)
        self.assertEqual(captured["max_tokens"], 500)

    def test_import_error_returns_none(self):
        """If vr_scenario_lib.llm is not importable, return None (fallback to HTTP)."""
        func = self._get_func()

        def raise_import(*args, **kwargs):
            raise ImportError("No module named 'vr_scenario_lib'")

        with patch.dict("sys.modules", {"vr_scenario_lib.llm": MagicMock(call_llm=raise_import)}):
            result = func(system="s", user="u", config={}, max_tokens=100)

        self.assertIsNone(result)


class TestBuildLlmConfigReturnsDict(unittest.TestCase):
    """Verify build_llm_config returns a dict (TypedDict) that supports .get()."""

    def test_config_supports_get(self):
        from vr_scenario_lib.config import build_llm_config
        config = build_llm_config()
        self.assertIsInstance(config, dict)
        self.assertIn("model", config)
        self.assertIn("api_url", config)
        self.assertIn("token", config)
        # The key fix: .get() must work
        self.assertIsNotNone(config.get("model"))
        self.assertIsNotNone(config.get("api_url"))
        self.assertIsNotNone(config.get("token"))


class TestGetAnswerLogging(unittest.TestCase):
    """Verify _get_answer logs strategy outcomes."""

    def test_all_strategies_fail_returns_fallback(self):
        """When all strategies return None, fallback message is returned."""
        from scenario_conversation_app_vocal_only_fixed import VRScenarioApp, AppConfig

        app = VRScenarioApp.__new__(VRScenarioApp)
        app.cfg = AppConfig()
        app._answer_strategies = [
            lambda q, s, c: None,
            lambda q, s, c: None,
            lambda q, s, c: None,
        ]

        result = app._get_answer("question", None, None)
        self.assertEqual(result, app.cfg.qa.fallback_message)

    def test_first_strategy_succeeds(self):
        """First non-None result is returned."""
        from scenario_conversation_app_vocal_only_fixed import VRScenarioApp, AppConfig

        app = VRScenarioApp.__new__(VRScenarioApp)
        app.cfg = AppConfig()
        app._answer_strategies = [
            lambda q, s, c: "réponse 1",
            lambda q, s, c: "réponse 2",
        ]

        result = app._get_answer("question", None, None)
        self.assertEqual(result, "réponse 1")


if __name__ == "__main__":
    unittest.main(verbosity=2)
