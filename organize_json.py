#!/usr/bin/env python3
"""Script d'organisation des fichiers JSON en répertoires config/ et data/.

Analyse la structure interne de chaque fichier JSON et le classe :
- config/ : fichiers de configuration (paramètres, settings, constantes)
- data/   : fichiers de données textuelles (scénarios, contenu, entrées)
- unknown/ : fichiers ambigus ou non classables

Usage:
    python organize_json.py --source ./ --dest ./organized --dry-run
    python organize_json.py --source ./scenarios --dest ./organized --move
"""

from __future__ import annotations

import argparse
import json
import logging
import shutil
import sys
from pathlib import Path
from typing import Any

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)

CONFIG_KEYS = {
    "model", "api_url", "api_key", "token", "temperature",
    "max_tokens", "timeout", "host", "port", "database", "version",
    "settings", "dependencies", "plugins", "rules", "commands",
    "agents", "providers", "permissions", "whitelist", "blacklist",
    "options", "headers", "endpoint", "base_url",
}

DATA_KEYS = {
    "scenario_id", "etapes", "titre", "content", "text", "messages",
    "history", "data", "results", "items", "records", "scenario_text",
    "page_content", "actions", "etat_initial", "etat_resultant",
    "conditions_erreur", "objectifs", "contexte", "consignes",
    "metadata", "source", "sources",
}

TEXT_FIELDS = {"text", "content", "description", "page_content", "scenario_text", "titre"}
MIN_TEXT_LENGTH = 100


def load_json(path: Path) -> dict | list | None:
    """Charge un fichier JSON et retourne l'objet parsé."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as exc:
        logger.warning("JSON invalide : %s (%s)", path.name, exc)
        return None
    except OSError as exc:
        logger.warning("Erreur lecture : %s (%s)", path.name, exc)
        return None


def has_long_text(obj: Any) -> bool:
    """Vérifie si l'objet contient des valeurs textuelles longues."""
    if isinstance(obj, dict):
        for key, value in obj.items():
            if key in TEXT_FIELDS and isinstance(value, str) and len(value) > MIN_TEXT_LENGTH:
                return True
            if has_long_text(value):
                return True
    elif isinstance(obj, list):
        for item in obj:
            if has_long_text(item):
                return True
    return False


def classify_json(obj: Any) -> str:
    """Classifie un objet JSON en 'config', 'data' ou 'unknown'."""
    if obj is None:
        return "unknown"

    if isinstance(obj, dict):
        keys = set(obj.keys())
        config_score = len(keys & CONFIG_KEYS)
        data_score = len(keys & DATA_KEYS)

        if config_score >= 2 and config_score > data_score:
            return "config"
        if data_score >= 1:
            return "data"
        if has_long_text(obj):
            return "data"
        if all(isinstance(v, (str, int, float, bool, type(None))) for v in obj.values()):
            return "config"
        return "data"

    if isinstance(obj, list) and len(obj) > 0:
        if isinstance(obj[0], dict):
            return "data"
        return "data"

    return "unknown"


def scan_json_files(source_dir: Path, depth: int = -1) -> list[Path]:
    """Scanne récursivement un répertoire et retourne les fichiers .json."""
    json_files: list[Path] = []
    if depth == 0:
        return json_files

    try:
        for entry in source_dir.iterdir():
            if entry.is_file() and entry.suffix.lower() == ".json":
                json_files.append(entry)
            elif entry.is_dir() and depth != 0:
                next_depth = depth - 1 if depth > 0 else -1
                json_files.extend(scan_json_files(entry, next_depth))
    except OSError as exc:
        logger.error("Erreur scan répertoire %s : %s", source_dir, exc)

    return json_files


def organize(
    source_dir: Path,
    dest_dir: Path,
    dry_run: bool = False,
    move: bool = False,
) -> dict[str, list[str]]:
    """Organise les fichiers JSON dans config/, data/ et unknown/."""
    if source_dir == dest_dir:
        logger.error("Source et destination identiques : %s", source_dir)
        return {"config": [], "data": [], "unknown": []}

    json_files = scan_json_files(source_dir)
    logger.info("%d fichier(s) JSON trouvé(s) dans %s", len(json_files), source_dir)

    classification: dict[str, list[str]] = {"config": [], "data": [], "unknown": []}

    for json_path in json_files:
        obj = load_json(json_path)
        category = classify_json(obj)
        classification[category].append(json_path.name)

        dest_subdir = dest_dir / category
        dest_path = dest_subdir / json_path.name

        if dest_path.exists():
            stem = json_path.stem
            suffix = json_path.suffix
            counter = 1
            while dest_path.exists():
                dest_path = dest_subdir / f"{stem}_{counter}{suffix}"
                counter += 1

        action = "Déplacer" if move else "Copier"
        if dry_run:
            logger.info("[DRY-RUN] %s %s → %s/%s", action, json_path.name, category, dest_path.name)
        else:
            try:
                dest_subdir.mkdir(parents=True, exist_ok=True)
                if move:
                    shutil.move(str(json_path), str(dest_path))
                else:
                    shutil.copy2(str(json_path), str(dest_path))
                logger.info("%s %s → %s/%s", action, json_path.name, category, dest_path.name)
            except OSError as exc:
                logger.error("Échec %s %s : %s", action.lower(), json_path.name, exc)

    return classification


def print_summary(classification: dict[str, list[str]], dest_dir: Path) -> None:
    """Affiche un résumé de la classification."""
    print("\n" + "=" * 60)
    print("RÉSUMÉ DE L'ORGANISATION")
    print("=" * 60)
    print(f"Destination : {dest_dir}")
    print()

    for category, files in classification.items():
        print(f"  {category}/ : {len(files)} fichier(s)")
        for f in sorted(files)[:10]:
            print(f"    - {f}")
        if len(files) > 10:
            print(f"    ... et {len(files) - 10} autres")
        print()

    total = sum(len(f) for f in classification.values())
    print(f"Total : {total} fichier(s) classé(s)")
    print("=" * 60)


def main() -> None:
    """Point d'entrée CLI."""
    parser = argparse.ArgumentParser(
        description="Organise les fichiers JSON en config/, data/ et unknown/",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples:
  python organize_json.py --source ./ --dest ./organized --dry-run
  python organize_json.py --source ./scenarios --dest ./organized --move
  python organize_json.py --source . --dest ./organized --depth 2
        """,
    )
    parser.add_argument(
        "--source",
        type=str,
        default=".",
        help="Répertoire source à scanner (défaut: .)",
    )
    parser.add_argument(
        "--dest",
        type=str,
        default="./organized",
        help="Répertoire destination (défaut: ./organized)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Affiche la classification sans déplacer/copier",
    )
    parser.add_argument(
        "--move",
        action="store_true",
        help="Déplace les fichiers au lieu de les copier",
    )
    parser.add_argument(
        "--depth",
        type=int,
        default=-1,
        help="Profondeur de scan (-1 = infini, 0 = racine uniquement)",
    )
    parser.add_argument(
        "--log-level",
        type=str,
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Niveau de log (défaut: INFO)",
    )

    args = parser.parse_args()
    logging.getLogger().setLevel(getattr(logging, args.log_level))

    source_dir = Path(args.source).resolve()
    dest_dir = Path(args.dest).resolve()

    if not source_dir.is_dir():
        logger.error("Répertoire source introuvable : %s", source_dir)
        sys.exit(1)

    if source_dir == dest_dir:
        logger.error("Source et destination identiques")
        sys.exit(1)

    logger.info("Source : %s", source_dir)
    logger.info("Destination : %s", dest_dir)
    logger.info("Mode : %s", "déplacer" if args.move else "copier")
    if args.dry_run:
        logger.info("DRY-RUN activé — aucun fichier ne sera déplacé")

    classification = organize(source_dir, dest_dir, args.dry_run, args.move)
    print_summary(classification, dest_dir)


if __name__ == "__main__":
    main()
