"""Pipeline orchestrateur pour la génération de scénarios VR avec fallback.

Combine toutes les étapes : documents → vectorstore → scénario → JSON.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from langchain_core.vectorstores import VectorStoreRetriever

from .config import LLMConfig
from .json_converter import JsonParsingError, convert_scenario_to_json
from .scenario import generate_scenario
from .scenario_store import create_session

logger = logging.getLogger(__name__)


class PipelineError(Exception):
    """Erreur lors de l'exécution du pipeline."""
    pass


def save_json(data: dict[str, Any], output_path: str) -> None:
    """Sauvegarde un dictionnaire en fichier JSON formaté.

    Args:
        data: Données à sauvegarder.
        output_path: Chemin du fichier de sortie.
    """
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    logger.info("JSON sauvegardé : %s", output_path)


def run_pipeline(
    topic: str,
    retriever: VectorStoreRetriever,
    llm_config: LLMConfig,
    output_path: str | None = None,
    custom_prompt: str = "",
    store_dir: str | None = None,
) -> dict[str, Any]:
    """Exécute le pipeline complet : scénario texte → JSON Unity.

    Args:
        topic: Thème du scénario à générer.
        retriever: Retriever vectoriel configuré avec les documents.
        llm_config: Configuration du LLM.
        output_path: Chemin optionnel pour sauvegarder le JSON résultant.
        custom_prompt: Consignes supplémentaires injectées dans le prompt.
        store_dir: Répertoire optionnel pour persister la session (texte + JSON + historique).

    Returns:
        Dictionnaire JSON du scénario structuré pour Unity VR.

    Raises:
        PipelineError: Si une étape du pipeline échoue.
        JsonParsingError: Si la conversion JSON échoue.
    """
    logger.info("=" * 70)
    logger.info("PIPELINE DÉMARRÉ")
    logger.info("=" * 70)
    logger.info("  Thème        : '%s'", topic[:100])
    logger.info("  Modèle LLM   : %s", llm_config.get("model", "inconnu"))
    logger.info("  API URL       : %s", llm_config.get("api_url", "inconnu"))
    logger.info("  Retriever     : %s", type(retriever).__name__)
    if custom_prompt:
        logger.info("  Custom prompt : %s", custom_prompt[:200])
    logger.info("=" * 70)

    try:
        logger.info("[PIPELINE ÉTAPE 1/3] Génération du scénario texte...")
        scenario_text, sources = generate_scenario(topic, retriever, llm_config, custom_prompt=custom_prompt)
        logger.info("[PIPELINE ÉTAPE 1/3] OK — Scénario texte : %d car., %d sources", len(scenario_text), len(sources))
    except Exception as exc:
        logger.exception("[PIPELINE ÉTAPE 1/3] ÉCHEC — Génération du scénario")
        raise PipelineError(f"Échec de la génération du scénario : {exc}") from exc

    # === Sauvegarde PRE-conversion (scénario texte brut) ===
    _save_pre_conversion(topic, scenario_text, sources, store_dir)

    try:
        logger.info("[PIPELINE ÉTAPE 2/3] Conversion en JSON Unity...")
        result = convert_scenario_to_json(scenario_text, llm_config)
        logger.info("[PIPELINE ÉTAPE 2/3] OK — JSON converti, clés: %s", list(result.keys()))
    except Exception as exc:
        logger.exception("[PIPELINE ÉTAPE 2/3] ÉCHEC — Conversion JSON")
        raise PipelineError(f"Échec de la conversion JSON : {exc}") from exc

    # === Sauvegarde POST-conversion (JSON structuré) ===
    _save_post_conversion(topic, result, store_dir)

    # Validation de la structure du JSON généré
    try:
        logger.info("[PIPELINE ÉTAPE 3/3] Validation de la structure JSON...")
        validate_scenario_structure(result)
        logger.info("[PIPELINE ÉTAPE 3/3] OK — Structure JSON validée")
    except JsonParsingError as exc:
        logger.exception("[PIPELINE ÉTAPE 3/3] ÉCHEC — Validation JSON : %s", exc)
        raise PipelineError(f"Structure JSON invalide : {exc}") from exc

    if output_path:
        save_json(result, output_path)

    if store_dir:
        create_session(topic, scenario_text, result, store_dir)
        logger.info("Session scénario persistée dans : %s", store_dir)

    logger.info("=" * 70)
    logger.info("PIPELINE TERMINÉ AVEC SUCCÈS")
    logger.info("=" * 70)
    return result


def _save_pre_conversion(topic: str, scenario_text: str, sources: list, store_dir: str | None) -> None:
    """Sauvegarde le scénario texte brut AVANT conversion JSON.

    Args:
        topic: Thème du scénario.
        scenario_text: Texte brut du scénario généré.
        sources: Liste des documents sources utilisés.
        store_dir: Répertoire de persistance (défaut: ./scenarios).
    """
    if store_dir is None:
        store_dir = "./scenarios"

    pre_dir = Path(store_dir) / "pre-conversion"
    pre_dir.mkdir(parents=True, exist_ok=True)

    safe_topic = topic.replace(" ", "_").replace("/", "_")[:50]
    pre_path = pre_dir / f"{safe_topic}_raw.json"

    payload = {
        "topic": topic,
        "scenario_text": scenario_text,
        "sources": [s.metadata if hasattr(s, "metadata") else {"source": str(s)} for s in sources],
    }

    try:
        pre_path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        logger.info("Scénario brut sauvegardé (pre-conversion) : %s", pre_path)
    except OSError as exc:
        logger.warning("Impossible de sauvegarder le scénario brut : %s", exc)


def _save_post_conversion(topic: str, result: dict[str, Any], store_dir: str | None) -> None:
    """Sauvegarde le scénario JSON structuré APRÈS conversion.

    Args:
        topic: Thème du scénario.
        result: Dictionnaire JSON du scénario converti.
        store_dir: Répertoire de persistance (défaut: ./scenarios).
    """
    if store_dir is None:
        store_dir = "./scenarios"

    post_dir = Path(store_dir) / "post-conversion"
    post_dir.mkdir(parents=True, exist_ok=True)

    safe_topic = topic.replace(" ", "_").replace("/", "_")[:50]
    post_path = post_dir / f"{safe_topic}.json"

    try:
        post_path.write_text(
            json.dumps(result, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        logger.info("Scénario converti sauvegardé (post-conversion) : %s", post_path)
    except OSError as exc:
        logger.warning("Impossible de sauvegarder le scénario converti : %s", exc)


def validate_scenario_structure(data: dict[str, Any]) -> None:
    """Valide la structure minimale du scénario JSON produit pour Unity.

    Args:
        data: Dictionnaire du scénario généré.

    Raises:
        JsonParsingError: Si un élément obligatoire est manquant ou invalide.
    """
    required_keys = ["scenario_id", "titre", "etat_initial", "etapes"]
    for key in required_keys:
        if key not in data:
            raise JsonParsingError(f"Clé obligatoire manquante dans le JSON généré : '{key}'")

    # Validation etat_initial
    etat_initial = data.get("etat_initial")
    if not isinstance(etat_initial, dict):
        raise JsonParsingError("Le champ 'etat_initial' doit être un dictionnaire.")

    # Validation etapes
    etapes = data.get("etapes")
    if not isinstance(etapes, list):
        raise JsonParsingError("Le champ 'etapes' doit être une liste.")

    for idx, etape in enumerate(etapes):
        if not isinstance(etape, dict):
            raise JsonParsingError(f"L'étape {idx} n'est pas un dictionnaire.")
        if "etape_id" not in etape or "titre" not in etape:
            raise JsonParsingError(f"Clé 'etape_id' ou 'titre' manquante dans l'étape {idx}.")
        
        # Validation actions
        actions = etape.get("actions", [])
        if not isinstance(actions, list):
            raise JsonParsingError(f"Le champ 'actions' de l'étape {idx} doit être une liste.")
            
        # Validation conditions_erreur
        erreurs = etape.get("conditions_erreur", [])
        if not isinstance(erreurs, list):
            raise JsonParsingError(f"Le champ 'conditions_erreur' de l'étape {idx} doit être une liste.")