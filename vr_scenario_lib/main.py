#!/usr/bin/env python3
"""Point d'entrée et exemple d'utilisation de vr_scenario_lib.

Démontre le pipeline complet : chargement documents → indexation →
génération de scénario VR → export JSON pour Unity.

Usage:
    python -m vr_scenario_lib.main --docs-dir ./documents --topic "consignation gaz"
    python -m vr_scenario_lib.main --voice
    python -m vr_scenario_lib.main --narrate

    Ou en tant que bibliothèque importable :

    >>> from vr_scenario_lib import (
    ...     build_llm_config, scan_directory, split_documents,
    ...     create_embeddings, build_vectorstore, create_retriever,
    ...     run_pipeline,
    ... )
"""

from __future__ import annotations

import json
import logging
import os
import sys
from dotenv import load_dotenv

# Charger les variables d'environnement depuis .env
load_dotenv()

# Allow running this file directly via `python -m main` or `python main.py` from the package directory.
package_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if package_root not in sys.path:
    sys.path.insert(0, package_root)

# If the project files live at the repository root (not installed as a package),
# create a synthetic `vr_scenario_lib` package in `sys.modules` by loading the
# local modules so `from vr_scenario_lib import ...` imports work inside the
# container when the package wasn't installed via `pip install .`.
try:
    import importlib.util
    import types

    pkg_name = "vr_scenario_lib"
    if pkg_name not in sys.modules:
        pkg = types.ModuleType(pkg_name)
        pkg.__path__ = [os.path.dirname(os.path.abspath(__file__))]
        sys.modules[pkg_name] = pkg

        # list of module filenames to expose under vr_scenario_lib.<name>
        local_modules = [
            "config",
            "documents",
            "pipeline",
            "vectorstore",
            "llm",
            "grpc_server",
            "prompts",
            "vectorstore",
            "documents",
            "scenario",
        ]

        for mod_name in set(local_modules):
            file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), f"{mod_name}.py")
            if os.path.exists(file_path):
                full_name = f"{pkg_name}.{mod_name}"
                try:
                    spec = importlib.util.spec_from_file_location(full_name, file_path)
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)  # type: ignore
                    sys.modules[full_name] = module
                except Exception:
                    pass
except Exception:
    pass

from vr_scenario_lib.config import (
    build_llm_config,
    DEFAULT_DOCS_DIR,
    DEFAULT_OUTPUT_PATH,
    DEFAULT_SCENARIOS_DIR,
    DEFAULT_FAISS_INDEX_DIR,
    DEFAULT_LOG_LEVEL,
)
from vr_scenario_lib.documents import scan_directory, split_documents
from vr_scenario_lib.vectorstore import (
    build_vectorstore,
    create_embeddings,
    create_retriever,
    load_vectorstore,
    save_vectorstore,
)
from vr_scenario_lib.pipeline import run_pipeline


def sanitize_topic(topic: str) -> str:
    """Sanitize and validate the scenario topic.

    Args:
        topic: Raw topic string.

    Returns:
        Cleaned topic string.

    Raises:
        ValueError: If topic is invalid.
    """
    if not topic or not topic.strip():
        raise ValueError("Le sujet ne peut pas être vide")
    topic = topic.strip()
    if len(topic) > 500:
        raise ValueError("Le sujet est trop long (max 500 caractères)")
    return topic


def main() -> None:
    """Main entry point for the VR Scenario Library."""
    import argparse

    parser = argparse.ArgumentParser(
        description="VR Scenario Library — Générateur de scénarios de formation gazière pour Unity VR",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples:
  # Génération par thème (mode batch)
  python -m vr_scenario_lib.main --topic "consignation gaz"

  # Mode vocal interactif (flux 2 phases : annonce → confirmation → JSON)
  python -m vr_scenario_lib.main --voice

  # Mode texte interactif avec annonce narrative (flux 2 phases)
  python -m vr_scenario_lib.main --narrate

  # Mode texte interactif simple
  python -m vr_scenario_lib.main --text

  # Reprendre une session existante
  python -m vr_scenario_lib.main --continue mon-scenario-id
        """,
    )

    # Mode selection
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument(
        "--topic",
        type=str,
        help="Scenario topic (batch mode) — generates and saves directly",
    )
    mode_group.add_argument(
        "--voice",
        action="store_true",
        help="Run in voice mode with narrative announcement (2-phase flow)",
    )
    mode_group.add_argument(
        "--narrate",
        action="store_true",
        help="Run in text mode with narrative announcement (2-phase flow: announce → confirm → save)",
    )
    mode_group.add_argument(
        "--text",
        action="store_true",
        help="Run in interactive text mode (no voice)",
    )
    mode_group.add_argument(
        "--continue",
        dest="continue_session",
        metavar="SESSION_ID",
        type=str,
        help="Reprendre une session de scénario sauvegardée (discussion LLM)",
    )

    # Pipeline configuration
    parser.add_argument(
        "--docs-dir",
        type=str,
        default=DEFAULT_DOCS_DIR,
        help=f"Directory containing source documents (default: {DEFAULT_DOCS_DIR})",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=DEFAULT_OUTPUT_PATH,
        help=f"Output JSON file path (default: {DEFAULT_OUTPUT_PATH})",
    )
    parser.add_argument(
        "--scenarios-dir",
        type=str,
        default=DEFAULT_SCENARIOS_DIR,
        help=f"Directory for persisted scenario sessions (default: {DEFAULT_SCENARIOS_DIR})",
    )
    parser.add_argument(
        "--faiss-index-dir",
        type=str,
        default=DEFAULT_FAISS_INDEX_DIR,
        help=f"FAISS index directory (default: {DEFAULT_FAISS_INDEX_DIR})",
    )
    parser.add_argument(
        "--log-level",
        type=str,
        default=DEFAULT_LOG_LEVEL,
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help=f"Logging level (default: {DEFAULT_LOG_LEVEL})",
    )

    # Voice configuration
    parser.add_argument(
        "--stt-backend",
        type=str,
        default="whisper",
        choices=["whisper", "google"],
        help="Speech-to-text backend (default: whisper)",
    )
    parser.add_argument(
        "--tts-backend",
        type=str,
        default="pyttsx3",
        choices=["pyttsx3", "gtts"],
        help="Text-to-speech backend (default: pyttsx3)",
    )
    parser.add_argument(
        "--language",
        type=str,
        default="fr",
        help="Language code for voice interaction (default: fr)",
    )
    parser.add_argument(
        "--whisper-model",
        type=str,
        default="base",
        choices=["tiny", "base", "small", "medium"],
        help="Whisper model size (default: base)",
    )

    # LLM configuration
    parser.add_argument(
        "--embedding-model",
        type=str,
        default=None,
        help="Embedding model name (default: from env or sentence-transformers/all-MiniLM-L6-v2)",
    )
    parser.add_argument(
        "--llm-model",
        type=str,
        default=None,
        help="LLM model name (default: from env)",
    )
    parser.add_argument(
        "--chunk-size",
        type=int,
        default=None,
        help="Document chunk size (default: from env or 1200)",
    )
    parser.add_argument(
        "--chunk-overlap",
        type=int,
        default=None,
        help="Chunk overlap size (default: from env or 150)",
    )
    parser.add_argument(
        "--retriever-k",
        type=int,
        default=None,
        help="Number of documents to retrieve (default: from env or 5)",
    )

    args = parser.parse_args()

    # Setup logging
    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
    logger = logging.getLogger(__name__)

    # Get API keys from environment
    hf_token = os.environ.get("HF_TOKEN") or os.environ.get("HUGGINGFACE_API_KEY")
    openrouter_api_key = os.environ.get("OPENROUTER_API_KEY")
    openrouter_api_url = os.environ.get("OPENROUTER_API_URL")

    # ── Batch mode: --topic ──────────────────────────────────────────────
    if args.topic:
        topic = sanitize_topic(args.topic)
        logger.info("Mode batch — Sujet: '%s'", topic)

        llm_config = build_llm_config(
            token=hf_token,
            openrouter_api_key=openrouter_api_key,
            openrouter_api_url=openrouter_api_url,
            model=args.llm_model,
        )

        embeddings = create_embeddings(
            model_name=args.embedding_model or os.environ.get("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2"),
            device=os.environ.get("DEVICE", "cpu"),
        )

        vectorstore = load_vectorstore(args.faiss_index_dir, embeddings)
        if not vectorstore:
            raw_docs = scan_directory(args.docs_dir)
            chunks = split_documents(
                raw_docs,
                chunk_size=args.chunk_size or int(os.environ.get("CHUNK_SIZE", 1200)),
                chunk_overlap=args.chunk_overlap or int(os.environ.get("CHUNK_OVERLAP", 150)),
            )
            vectorstore = build_vectorstore(chunks, embeddings)
            save_vectorstore(vectorstore, args.faiss_index_dir)

        retriever = create_retriever(
            vectorstore,
            k=args.retriever_k or int(os.environ.get("RETRIEVER_K", 5)),
        )

        result = run_pipeline(
            topic=topic,
            retriever=retriever,
            llm_config=llm_config,
            output_path=args.output,
            store_dir=args.scenarios_dir,
        )

        if result:
            print(f"\n✅ Scénario généré et sauvegardé: {args.output}")
            print(json.dumps(result, ensure_ascii=False, indent=2)[:500])
        else:
            print("❌ Échec de la génération")
            sys.exit(1)
        return

    # ── Interactive modes ────────────────────────────────────────────────
    from vr_scenario_lib.conversational_agent import ConversationalAgent

    agent_kwargs = dict(
        docs_dir=args.docs_dir,
        output_path=args.output,
        scenarios_dir=args.scenarios_dir,
        faiss_index_dir=args.faiss_index_dir,
        log_level=args.log_level,
        hf_token=hf_token,
        openrouter_api_key=openrouter_api_key,
        openrouter_api_url=openrouter_api_url,
        embedding_model=args.embedding_model,
        llm_model=args.llm_model,
        chunk_size=args.chunk_size,
        chunk_overlap=args.chunk_overlap,
        retriever_k=args.retriever_k,
    )

    if args.continue_session:
        agent = ConversationalAgent(**agent_kwargs)
        agent.run_discussion_session(args.continue_session)

    elif args.voice:
        agent = ConversationalAgent(
            **agent_kwargs,
            stt_backend=args.stt_backend,
            tts_backend=args.tts_backend,
            language=args.language,
            whisper_model=args.whisper_model,
        )
        agent.run_voice_session()

    elif args.narrate:
        agent = ConversationalAgent(**agent_kwargs)
        agent.run_text_session(narrate=True)

    elif args.text:
        agent = ConversationalAgent(**agent_kwargs)
        agent.run_text_session()

    else:
        parser.print_help()
        sys.exit(0)


if __name__ == "__main__":
    main()