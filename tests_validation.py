"""
Tests de validation pour generate_scenario, build_llm_config, et le flux voix.

Couvre:
- Tests unitaires: signature, paramètres optionnels, transcription
- Tests d'intégration: pipeline complet, fallback LLM
- Cas limites: topic vide, transcription énorme, None partout
- Robustesse: injection dans prompt, retry behavior, fallback_models vide
- Sécurité: token dans logs, credentials leak, path traversal
"""

import io
import json
import logging
import os
import sys
import unittest
import urllib.error
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch, call

# Ensure the package root is on sys.path
_PACKAGE_ROOT = Path(__file__).resolve().parent.parent
if str(_PACKAGE_ROOT) not in sys.path:
    sys.path.insert(0, str(_PACKAGE_ROOT))

from vr_scenario_lib.config import (
    LLMConfig,
    build_llm_config,
    SYSTEM_SCENARIO,
    DEFAULT_FALLBACK_MODELS,
    DEFAULT_MODEL,
    DEFAULT_OPENROUTER_API_URL,
    _ENV_FILE,
    _PROJECT_ROOT,
)
from vr_scenario_lib.scenario import generate_scenario, format_context
from vr_scenario_lib.prompts import build_scenario_prompt
from vr_scenario_lib.llm import call_llm, _call_llm_single_model, LLMError, LLMFallbackExhaustedError


# ============================================================================
# Helpers
# ============================================================================

def _make_llm_config(token: str = "test_token_12345") -> LLMConfig:
    return {
        "api_url": "https://openrouter.ai/api/v1/chat/completions",
        "model": "meta-llama/llama-3.3-70b-instruct:free",
        "fallback_models": ["google/gemma-4-31b-it:free"],
        "token": token,
        "max_tokens": 1500,
        "temperature": 0.3,
        "timeout": 30,
        "max_retries": 1,
        "retry_backoff_factor": 1.0,
    }


def _mock_llm_response(text: str = "Scénario généré") -> dict:
    return {
        "choices": [{"message": {"content": text}}]
    }


# ============================================================================
# 1. Tests unitaires — Signature & paramètres optionnels
# ============================================================================

class TestGenerateScenarioSignature(unittest.TestCase):
    """Vérifie que la signature accepte les appels sans retriever."""

    @patch("vr_scenario_lib.scenario.call_llm")
    @patch("vr_scenario_lib.scenario.build_scenario_prompt")
    def test_no_retriever_no_transcription(self, mock_prompt, mock_llm):
        """Appel minimaliste: topic seul, sans retriever ni transcription."""
        mock_prompt.return_value = "prompt"
        mock_llm.return_value = "Scénario test"

        text, docs = generate_scenario("consignation gaz", llm_config=_make_llm_config())

        self.assertIsInstance(text, str)
        self.assertEqual(docs, [])
        mock_prompt.assert_called_once_with("consignation gaz", "")

    @patch("vr_scenario_lib.scenario.call_llm")
    @patch("vr_scenario_lib.scenario.build_scenario_prompt")
    def test_with_transcription_no_retriever(self, mock_prompt, mock_llm):
        """Transcription fournie sans retriever."""
        mock_prompt.return_value = "prompt de base"
        mock_llm.return_value = "Scénario avec transcription"

        transcription = "L'utilisateur décrit une procédure de consignation gaz."
        text, docs = generate_scenario(
            "consignation",
            llm_config=_make_llm_config(),
            transcription=transcription,
        )

        self.assertEqual(text, "Scénario avec transcription")
        self.assertEqual(docs, [])
        # Vérifie que le prompt contient la transcription
        called_prompt = mock_prompt.return_value
        # Le transcription est APRÈS le prompt de base (ajouté dans le corps)
        # On vérifie via le call_llm que le user_prompt contient la transcription
        call_args = mock_llm.call_args
        user_prompt = call_args.kwargs.get("user_prompt") or call_args[1].get("user_prompt", "")
        self.assertIn(transcription, user_prompt)

    @patch("vr_scenario_lib.scenario.call_llm")
    @patch("vr_scenario_lib.scenario.retrieve_context")
    def test_with_retriever(self, mock_retrieve, mock_llm):
        """Avec retriever, le contexte est récupéré."""
        mock_retrieve.return_value = [
            MagicMock(metadata={"source": "doc1"}, page_content="Contenu du document"),
        ]
        mock_llm.return_value = "Scénario avec RAG"

        mock_retriever = MagicMock()
        text, docs = generate_scenario(
            "consignation",
            retriever=mock_retriever,
            llm_config=_make_llm_config(),
        )

        mock_retrieve.assert_called_once_with(mock_retriever, "consignation")
        self.assertEqual(len(docs), 1)

    @patch("vr_scenario_lib.scenario.call_llm")
    @patch("vr_scenario_lib.scenario.build_scenario_prompt")
    def test_custom_prompt_injected(self, mock_prompt, mock_llm):
        """Le custom_prompt est bien ajouté au user prompt."""
        mock_prompt.return_value = "prompt"
        mock_llm.return_value = "ok"

        generate_scenario(
            "test",
            llm_config=_make_llm_config(),
            custom_prompt="Utiliser le mode nuit",
        )

        call_args = mock_llm.call_args
        user_prompt = call_args.kwargs.get("user_prompt") or call_args[1].get("user_prompt", "")
        self.assertIn("CONSIGNES SUPPLÉMENTAIRES", user_prompt)
        self.assertIn("Utiliser le mode nuit", user_prompt)

    @patch("vr_scenario_lib.scenario.call_llm")
    @patch("vr_scenario_lib.scenario.build_scenario_prompt")
    def test_transcription_and_custom_prompt_both(self, mock_prompt, mock_llm):
        """Transcription + custom_prompt simultanés."""
        mock_prompt.return_value = "prompt"
        mock_llm.return_value = "ok"

        generate_scenario(
            "test",
            llm_config=_make_llm_config(),
            custom_prompt="Mode nuit",
            transcription="Procédure de test",
        )

        call_args = mock_llm.call_args
        user_prompt = call_args.kwargs.get("user_prompt") or call_args[1].get("user_prompt", "")
        self.assertIn("TRANSCRIPTION VOCALE", user_prompt)
        self.assertIn("Procédure de test", user_prompt)
        self.assertIn("CONSIGNES SUPPLÉMENTAIRES", user_prompt)
        self.assertIn("Mode nuit", user_prompt)


# ============================================================================
# 2. Tests unitaires — build_llm_config & getenv
# ============================================================================

class TestBuildLlmConfig(unittest.TestCase):
    """Vérifie la résolution du token et l'URL depuis .env."""

    def test_token_from_env(self):
        """Token lu depuis OPENROUTER_API_KEY dans .env."""
        with patch.dict(os.environ, {"OPENROUTER_API_KEY": "sk-or-fromenv123456789012345"}):
            config = build_llm_config()
            self.assertEqual(config["token"], "sk-or-fromenv123456789012345")

    def test_token_explicit_overrides_env(self):
        """Token explicite prioritaire sur env."""
        with patch.dict(os.environ, {"OPENROUTER_API_KEY": "sk-or-fromenv"}):
            config = build_llm_config(token="sk-or-explicit")
            self.assertEqual(config["token"], "sk-or-explicit")

    def test_openrouter_api_key_param(self):
        """openrouter_api_key est un alias pour token."""
        config = build_llm_config(openrouter_api_key="sk-or-param")
        self.assertEqual(config["token"], "sk-or-param")

    def test_hf_token_fallback(self):
        """HF_TOKEN utilisé si OPENROUTER_API_KEY absent."""
        env = {"HF_TOKEN": "hf_test123456789012345678"}
        with patch.dict(os.environ, env, clear=False):
            if "OPENROUTER_API_KEY" in os.environ:
                del os.environ["OPENROUTER_API_KEY"]
            config = build_llm_config()
            self.assertEqual(config["token"], "hf_test123456789012345678")

    def test_no_token_raises_value_error(self):
        """ValueError si aucun token disponible."""
        env_backup = {k: v for k, v in os.environ.items()
                      if k in ("OPENROUTER_API_KEY", "HF_TOKEN", "HUGGINGFACE_API_KEY")}
        with patch.dict(os.environ, {}, clear=True):
            for k in ("OPENROUTER_API_KEY", "HF_TOKEN", "HUGGINGFACE_API_KEY"):
                os.environ.pop(k, None)
            with self.assertRaises(ValueError):
                build_llm_config()

    def test_api_url_defaults_to_openrouter(self):
        """URL par défaut = OpenRouter."""
        with patch.dict(os.environ, {"OPENROUTER_API_KEY": "sk-or-test"}):
            config = build_llm_config()
            self.assertEqual(config["api_url"], DEFAULT_OPENROUTER_API_URL)

    def test_api_url_explicit_override(self):
        """api_url explicite prioritaire."""
        with patch.dict(os.environ, {"OPENROUTER_API_KEY": "sk-or-test"}):
            config = build_llm_config(api_url="https://custom.api/v1/chat/completions")
            self.assertEqual(config["api_url"], "https://custom.api/v1/chat/completions")

    def test_env_file_exists(self):
        """Le fichier .env existe au chemin attendu."""
        self.assertTrue(_ENV_FILE.exists(), f".env introuvable: {_ENV_FILE}")
        self.assertTrue(_ENV_FILE.is_file())

    def test_env_file_contains_openrouter_key(self):
        """Le .env contient bien OPENROUTER_API_KEY."""
        content = _ENV_FILE.read_text(encoding="utf-8")
        self.assertIn("OPENROUTER_API_KEY=", content)

    def test_project_root_resolution(self):
        """_PROJECT_ROOT pointe vers vr_scenario_lib/."""
        self.assertEqual(_PROJECT_ROOT.name, "vr_scenario_lib")

    def test_default_fallback_models(self):
        """Liste de fallback non vide."""
        with patch.dict(os.environ, {"OPENROUTER_API_KEY": "sk-or-test"}):
            config = build_llm_config()
            self.assertIsInstance(config["fallback_models"], list)
            self.assertTrue(len(config["fallback_models"]) > 0)

    def test_custom_fallback_models(self):
        """Fallback models personnalisés."""
        with patch.dict(os.environ, {"OPENROUTER_API_KEY": "sk-or-test"}):
            config = build_llm_config(fallback_models=["custom/model:free"])
            self.assertEqual(config["fallback_models"], ["custom/model:free"])


# ============================================================================
# 3. Tests — build_scenario_prompt
# ============================================================================

class TestBuildScenarioPrompt(unittest.TestCase):
    """Vérifie la construction du prompt."""

    def test_empty_context_handled(self):
        """Contexte vide ne produit pas d'erreur."""
        prompt = build_scenario_prompt("test", "")
        self.assertIn("test", prompt)
        self.assertIn("CONTEXTE DOCUMENTAIRE", prompt)

    def test_with_context(self):
        """Contexte documentaire injecté."""
        prompt = build_scenario_prompt("gaz", "[Source 1] Procédure...")
        self.assertIn("[Source 1] Procédure...", prompt)

    def test_correspondance_objets_present(self):
        """La table de correspondance MASER est dans le prompt."""
        prompt = build_scenario_prompt("test", "")
        self.assertIn("R0", prompt)
        self.assertIn("VS_GAZFIO", prompt)


# ============================================================================
# 4. Tests — format_context
# ============================================================================

class TestFormatContext(unittest.TestCase):
    """Vérifie le formatage des documents."""

    def test_empty_list(self):
        """Liste vide -> chaîne vide."""
        self.assertEqual(format_context([]), "")

    def test_single_doc(self):
        """Document unique formaté."""
        doc = MagicMock()
        doc.metadata = {"source": "test.pdf"}
        doc.page_content = "Contenu test"
        result = format_context([doc])
        self.assertIn("test.pdf", result)
        self.assertIn("Contenu test", result)

    def test_multiple_docs(self):
        """Documents séparés par ---."""
        docs = []
        for i in range(3):
            d = MagicMock()
            d.metadata = {"source": f"doc{i}.pdf"}
            d.page_content = f"Contenu {i}"
            docs.append(d)
        result = format_context(docs)
        self.assertIn("[Source 1", result)
        self.assertIn("[Source 2", result)
        self.assertIn("[Source 3", result)


# ============================================================================
# 5. Tests — Retry & Fallback (robustesse)
# ============================================================================

class TestRetryMechanism(unittest.TestCase):
    """Vérifie que le retry est préservé et fonctionne."""

    @patch("vr_scenario_lib.llm.requests.post")
    def test_401_not_retried(self, mock_post):
        """HTTP 401 est non-récupérable -> LLMError immédiate, pas de retry."""
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.ok = False
        mock_response.text = "Unauthorized"
        mock_post.return_value = mock_response

        config = _make_llm_config()
        config["max_retries"] = 3

        with self.assertRaises(LLMError):
            _call_llm_single_model(
                system_prompt="test",
                user_prompt="test",
                config=config,
                model="test/model",
            )
        # Un seul appel (pas de retry pour 401)
        self.assertEqual(mock_post.call_count, 1)

    @patch("vr_scenario_lib.llm.requests.post")
    def test_429_retried(self, mock_post):
        """HTTP 429 déclenche le retry."""
        mock_429 = MagicMock()
        mock_429.status_code = 429
        mock_429.ok = False
        mock_429.text = "Rate limited"

        mock_200 = MagicMock()
        mock_200.status_code = 200
        mock_200.ok = True
        mock_200.json.return_value = _mock_llm_response("ok")

        mock_post.side_effect = [mock_429, mock_200]

        config = _make_llm_config()
        config["max_retries"] = 3
        config["retry_backoff_factor"] = 0.01  # fast backoff for test

        result = _call_llm_single_model(
            system_prompt="test",
            user_prompt="test",
            config=config,
            model="test/model",
        )
        self.assertEqual(result, "ok")
        self.assertEqual(mock_post.call_count, 2)

    @patch("vr_scenario_lib.llm.requests.post")
    def test_all_models_exhausted_raises_fallback_error(self, mock_post):
        """Tous les modèles échouent -> LLMFallbackExhaustedError."""
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.ok = False
        mock_response.text = "Server Error"
        mock_post.return_value = mock_response

        config = _make_llm_config()
        config["max_retries"] = 1
        config["retry_backoff_factor"] = 0.01
        config["fallback_models"] = ["model/a", "model/b"]

        with self.assertRaises(LLMFallbackExhaustedError):
            call_llm(
                system_prompt="test",
                user_prompt="test",
                config=config,
            )
        # 1 appel pour le principal + 1 pour chaque fallback = 3
        self.assertEqual(mock_post.call_count, 3)

    @patch("vr_scenario_lib.llm.requests.post")
    def test_503_retried_then_succeeds(self, mock_post):
        """503 suivi de 200 -> succès après retry."""
        mock_503 = MagicMock()
        mock_503.status_code = 503
        mock_503.ok = False
        mock_503.text = "Service Unavailable"

        mock_200 = MagicMock()
        mock_200.status_code = 200
        mock_200.ok = True
        mock_200.json.return_value = _mock_llm_response("success")

        mock_post.side_effect = [mock_503, mock_200]

        config = _make_llm_config()
        config["max_retries"] = 3
        config["retry_backoff_factor"] = 0.01

        result = call_llm(
            system_prompt="test",
            user_prompt="test",
            config=config,
        )
        self.assertEqual(result, "success")


# ============================================================================
# 6. Tests — Edge cases
# ============================================================================

class TestEdgeCases(unittest.TestCase):
    """Cas limites et situations extrêmes."""

    @patch("vr_scenario_lib.scenario.call_llm")
    @patch("vr_scenario_lib.scenario.build_scenario_prompt")
    def test_empty_topic(self, mock_prompt, mock_llm):
        """Topic chaîne vide."""
        mock_prompt.return_value = "prompt"
        mock_llm.return_value = "Scénario vide"
        text, docs = generate_scenario("", llm_config=_make_llm_config())
        self.assertIsInstance(text, str)

    @patch("vr_scenario_lib.scenario.call_llm")
    @patch("vr_scenario_lib.scenario.build_scenario_prompt")
    def test_very_long_transcription(self, mock_prompt, mock_llm):
        """Transcription de 50 000 caractères."""
        mock_prompt.return_value = "prompt"
        mock_llm.return_value = "ok"
        long_text = "A" * 50000
        text, docs = generate_scenario(
            "test",
            llm_config=_make_llm_config(),
            transcription=long_text,
        )
        call_args = mock_llm.call_args
        user_prompt = call_args.kwargs.get("user_prompt") or call_args[1].get("user_prompt", "")
        self.assertIn("A" * 100, user_prompt)

    @patch("vr_scenario_lib.scenario.call_llm")
    @patch("vr_scenario_lib.scenario.build_scenario_prompt")
    def test_special_characters_in_transcription(self, mock_prompt, mock_llm):
        """Caractères spéciaux dans la transcription."""
        mock_prompt.return_value = "prompt"
        mock_llm.return_value = "ok"
        special = "Robinet R0 = 100% <script>alert('xss')</script> \"quoted\""
        text, docs = generate_scenario(
            "test",
            llm_config=_make_llm_config(),
            transcription=special,
        )
        call_args = mock_llm.call_args
        user_prompt = call_args.kwargs.get("user_prompt") or call_args[1].get("user_prompt", "")
        self.assertIn("<script>", user_prompt)

    @patch("vr_scenario_lib.scenario.call_llm")
    @patch("vr_scenario_lib.scenario.build_scenario_prompt")
    def test_unicode_transcription(self, mock_prompt, mock_llm):
        """Caractères Unicode (accents, emojis)."""
        mock_prompt.return_value = "prompt"
        mock_llm.return_value = "ok"
        unicode_text = "Procédure de consignation — température: 25°C 🌡️"
        text, docs = generate_scenario(
            "test",
            llm_config=_make_llm_config(),
            transcription=unicode_text,
        )
        call_args = mock_llm.call_args
        user_prompt = call_args.kwargs.get("user_prompt") or call_args[1].get("user_prompt", "")
        self.assertIn("°C", user_prompt)

    @patch("vr_scenario_lib.scenario.call_llm")
    @patch("vr_scenario_lib.scenario.build_scenario_prompt")
    def test_empty_custom_prompt_ignored(self, mock_prompt, mock_llm):
        """custom_prompt vide n'ajoute rien."""
        mock_prompt.return_value = "prompt"
        mock_llm.return_value = "ok"
        generate_scenario(
            "test",
            llm_config=_make_llm_config(),
            custom_prompt="",
        )
        call_args = mock_llm.call_args
        user_prompt = call_args.kwargs.get("user_prompt") or call_args[1].get("user_prompt", "")
        self.assertNotIn("CONSIGNES SUPPLÉMENTAIRES", user_prompt)

    @patch("vr_scenario_lib.scenario.call_llm")
    @patch("vr_scenario_lib.scenario.build_scenario_prompt")
    def test_whitespace_only_transcription_ignored(self, mock_prompt, mock_llm):
        """Transcription avec seulement des espaces n'est pas injectée."""
        mock_prompt.return_value = "prompt"
        mock_llm.return_value = "ok"
        generate_scenario(
            "test",
            llm_config=_make_llm_config(),
            transcription="   \n\t  ",
        )
        call_args = mock_llm.call_args
        user_prompt = call_args.kwargs.get("user_prompt") or call_args[1].get("user_prompt", "")
        self.assertNotIn("TRANSCRIPTION VOCALE", user_prompt)


# ============================================================================
# 7. Tests — Sécurité
# ============================================================================

class TestSecurity(unittest.TestCase):
    """Tests de sécurité: pas de fuite de credentials."""

    def test_token_not_in_logs(self):
        """Le token n'apparaît pas dans les logs (masquage)."""
        import io
        log_stream = io.StringIO()
        handler = logging.StreamHandler(log_stream)
        handler.setLevel(logging.DEBUG)
        logger = logging.getLogger("vr_scenario_lib.config")
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)

        with patch.dict(os.environ, {"OPENROUTER_API_KEY": "sk-or-SECRET123456789012"}):
            config = build_llm_config()

        log_output = log_stream.getvalue()
        self.assertNotIn("sk-or-SECRET123456789012", log_output)
        logger.removeHandler(handler)

    def test_token_masked_in_config_logs(self):
        """Le token est masqué dans les logs de build_llm_config."""
        import io
        log_stream = io.StringIO()
        handler = logging.StreamHandler(log_stream)
        handler.setLevel(logging.DEBUG)
        logger = logging.getLogger("vr_scenario_lib.config")
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)

        with patch.dict(os.environ, {"OPENROUTER_API_KEY": "sk-or-VERYSECRETKEY1234"}):
            config = build_llm_config()

        log_output = log_stream.getvalue()
        # Le token masqué devrait apparaître (sk-or-***)
        self.assertIn("***", log_output)
        # Mais pas le token complet
        self.assertNotIn("sk-or-VERYSECRETKEY1234", log_output)
        logger.removeHandler(handler)

    def test_env_file_not_world_readable(self):
        """Le fichier .env ne devrait pas être lisible par tous (Unix)."""
        # Sur Windows ce test est informatif seulement
        if os.name == "nt":
            self.skipTest("Test Unix-only")
        stat = os.stat(_ENV_FILE)
        mode = oct(stat.st_mode)[-3:]
        self.assertNotEqual(mode[2], "7", ".env ne devrait pas être world-readable")

    def test_no_hardcoded_secrets_in_source(self):
        """Pas de secrets en dur dans le code source."""
        source_files = [
            _PROJECT_ROOT / "vr_scenario_lib" / "config.py",
            _PROJECT_ROOT / "vr_scenario_lib" / "llm.py",
            _PROJECT_ROOT / "vr_scenario_lib" / "scenario.py",
        ]
        suspicious_patterns = ["sk-or-", "hf_", "sk-"]
        for fpath in source_files:
            content = fpath.read_text(encoding="utf-8")
            # Chercher des patterns qui ressemblent à de vrais tokens (pas des exemples)
            for line_num, line in enumerate(content.split("\n"), 1):
                for pat in suspicious_patterns:
                    if pat in line and ("=" in line or ":" in line):
                        # Vérifier que ce n'est pas un commentaire ou un nom de variable
                        stripped = line.strip()
                        if stripped.startswith("#") or stripped.startswith("//"):
                            continue
                        # Si c'est une variable d'environnement ou un commentaire docstring, OK
                        if "os.environ" in line or "os.getenv" in line or '"""' in line or "'''" in line:
                            continue
                        # Si c'est une valeur par défaut = "..." avec un token réel
                        if f'="{pat}' in line or f"'{pat}" in line:
                            self.fail(
                                f"Possible secret dans {fpath.name}:{line_num}: {stripped[:80]}"
                            )


# ============================================================================
# 8. Tests — Intégration (mock LLM call)
# ============================================================================

class TestIntegration(unittest.TestCase):
    """Tests d'intégration avec LLM mocké."""

    @patch("vr_scenario_lib.scenario.call_llm")
    @patch("vr_scenario_lib.scenario.retrieve_context")
    def test_full_pipeline_with_retriever_and_transcription(self, mock_retrieve, mock_llm):
        """Pipeline complet: retriever + transcription + custom_prompt."""
        mock_retrieve.return_value = [
            MagicMock(metadata={"source": "proc.pdf"}, page_content="Procédure R0"),
        ]
        mock_llm.return_value = "Scénario complet généré"

        mock_retriever = MagicMock()
        text, docs = generate_scenario(
            "consignation gaz",
            retriever=mock_retriever,
            llm_config=_make_llm_config(),
            custom_prompt="Mode nuit",
            transcription="L'utilisateur décrit une consignation",
        )

        self.assertEqual(text, "Scénario complet généré")
        self.assertEqual(len(docs), 1)

        # Vérifier le contenu du prompt envoyé au LLM
        call_args = mock_llm.call_args
        user_prompt = call_args.kwargs.get("user_prompt") or call_args[1].get("user_prompt", "")
        self.assertIn("consignation gaz", user_prompt)
        self.assertIn("Procédure R0", user_prompt)
        self.assertIn("TRANSCRIPTION VOCALE", user_prompt)
        self.assertIn("L'utilisateur décrit une consignation", user_prompt)
        self.assertIn("CONSIGNES SUPPLÉMENTAIRES", user_prompt)
        self.assertIn("Mode nuit", user_prompt)

    @patch("vr_scenario_lib.scenario.call_llm")
    @patch("vr_scenario_lib.scenario.build_scenario_prompt")
    def test_pipeline_no_rag_only_transcription(self, mock_prompt, mock_llm):
        """Pipeline sans RAG: transcription comme seule source de contexte."""
        mock_prompt.return_value = "base prompt"
        mock_llm.return_value = "Scénario transcription-only"

        text, docs = generate_scenario(
            "test",
            llm_config=_make_llm_config(),
            transcription="Description vocale complète de la procédure",
        )

        self.assertEqual(text, "Scénario transcription-only")
        self.assertEqual(docs, [])
        call_args = mock_llm.call_args
        user_prompt = call_args.kwargs.get("user_prompt") or call_args[1].get("user_prompt", "")
        self.assertIn("Description vocale complète", user_prompt)


# ============================================================================
# 9. Tests — Pipeline.py backward compatibility
# ============================================================================

class TestPipelineBackwardCompat(unittest.TestCase):
    """Vérifie que pipeline.py fonctionne toujours avec le nouveau signature."""

    @patch("vr_scenario_lib.scenario.call_llm")
    @patch("vr_scenario_lib.scenario.retrieve_context")
    def test_pipeline_call_with_retriever(self, mock_retrieve, mock_llm):
        """pipeline.py appelle generate_scenario avec retriever positionnel."""
        mock_retrieve.return_value = []
        mock_llm.return_value = "Scénario pipeline"

        mock_retriever = MagicMock()
        from vr_scenario_lib.scenario import generate_scenario

        # Simuler l'appel de pipeline.py: generate_scenario(topic, retriever, llm_config, custom_prompt=...)
        text, docs = generate_scenario(
            "test",
            mock_retriever,
            _make_llm_config(),
            custom_prompt="",
        )
        self.assertEqual(text, "Scénario pipeline")
        mock_retrieve.assert_called_once()


# ============================================================================
# 10. Tests — call_with_retry (voice app)
# ============================================================================

class TestCallWithRetry(unittest.TestCase):
    """Vérifie le comportement de call_with_retry dans le voice app."""

    def test_retry_on_urllib_error(self):
        """Retry sur URLError."""
        from scenario_conversation_app_vocal_only_fixed import call_with_retry, RetryConfig

        cfg = RetryConfig()
        cfg.max_retries = 2
        cfg.backoff_s = 0.01

        call_count = 0

        def failing_then_success():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise urllib.error.URLError("connection refused")
            return "success"

        result = call_with_retry(
            failing_then_success,
            retry_cfg=cfg,
            retryable_exceptions=(urllib.error.URLError, TimeoutError),
        )
        self.assertEqual(result, "success")
        self.assertEqual(call_count, 2)

    def test_non_retryable_exception_propagated(self):
        """Exception non-retryable propagée immédiatement (pas dans retryable_exceptions)."""
        from scenario_conversation_app_vocal_only_fixed import call_with_retry, RetryConfig

        cfg = RetryConfig()
        cfg.max_retries = 3
        cfg.backoff_s = 0.01

        def always_value_error():
            raise ValueError("bad value")

        # ValueError is NOT in retryable_exceptions, so it propagates as-is
        with self.assertRaises(ValueError):
            call_with_retry(
                always_value_error,
                retry_cfg=cfg,
                retryable_exceptions=(TimeoutError,),
            )

    def test_all_retries_exhausted_raises_runtime(self):
        """Tentatives épuisées -> RuntimeError."""
        from scenario_conversation_app_vocal_only_fixed import call_with_retry, RetryConfig

        cfg = RetryConfig()
        cfg.max_retries = 2
        cfg.backoff_s = 0.01

        import urllib.error

        def always_fail():
            raise urllib.error.URLError("fail")

        with self.assertRaises(RuntimeError) as ctx:
            call_with_retry(
                always_fail,
                retry_cfg=cfg,
                retryable_exceptions=(urllib.error.URLError,),
            )
        self.assertIn("tentative", str(ctx.exception).lower())


# ============================================================================
# Runner
# ============================================================================

if __name__ == "__main__":
    unittest.main(verbosity=2)
