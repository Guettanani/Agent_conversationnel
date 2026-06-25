"""Chargement et découpage de documents (PDF, DOCX) avec fallback.

Fonctions atomiques pour charger des fichiers depuis le filesystem
et les découper en chunks prêts pour l'indexation vectorielle.
Inclut réparation d'encodage et fallback OCR pour PDFs scannées.
"""

from __future__ import annotations

import logging
import os
import re
from pathlib import Path

from langchain_community.document_loaders import Docx2txtLoader, PyPDFLoader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from .config import DEFAULT_CHUNK_OVERLAP, DEFAULT_CHUNK_SIZE, SUPPORTED_EXTENSIONS

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Encodage / Fallback helpers
# ---------------------------------------------------------------------------

_GARBLE_PATTERN = re.compile(r"[�\x00-\x08\x0b\x0e\x1f]")
_SPACED_DIGITS = re.compile(r"(?<=\d) (?=\d)")
_SPACED_LETTERS_AFTER_DOT = re.compile(r"\. ([A-Za-zÀ-ÿ])")


def _repair_text(text: str) -> str:
    """Répare les problèmes courants d'encodage extraits des PDF.

    - Supprime les caractères de contrôle et remplacements Unicode.
    - Corrige les espaces inter-chiffres (ex: '1 2 0 0' -> '1200').
    - Corrige les séquences 'a p r è s' -> 'après', etc.
    - Remplace '�' par 'é' dans les contextes de mots français courants.
    """
    if not text:
        return text

    cleaned = text.replace("�", "é")

    cleaned = _SPACED_DIGITS.sub("", cleaned)

    corrections = {
        "�": "é",
        "Ã©": "é",
        "Ã¨": "è",
        "Ã¼": "ü",
        "Ã´": "ô",
        "Ã®": "î",
        "Ã¢": "â",
        "Ã ": "à",
        "Ã§": "ç",
        "Ãª": "ê",
        "Ã«": "ë",
        "Ã¯": "ï",
        "Ã¶": "ö",
        "Ã¹": "ù",
        "Ã»": "û",
        "t�te": "tête",
        "tr�s": "très",
        "proc�dure": "procédure",
        "�viter": "éviter",
        "d�marrer": "démarrer",
        "d�s": "dès",
        "�tat": "état",
        "op�rateur": "opérateur",
        "s�curité": "sécurité",
        "gazi�re": "gazière",
        "r�seau": "réseau",
        "r�gulation": "régulation",
        "d�bit": "débit",
    }
    for wrong, right in corrections.items():
        cleaned = cleaned.replace(wrong, right)

    cleaned = _GARBLE_PATTERN.sub("", cleaned)

    cleaned = re.sub(
        r"(?<=[a-zA-ZÀ-ÿ\u00C0-\u017F]) (?=[a-zA-ZÀ-ÿ\u00C0-\u017F]( |$))",
        "",
        cleaned,
    )

    return cleaned


def _has_garbled_content(docs: list[Document]) -> bool:
    """Détecte si un document contient du texte illisible (garbled)."""
    if not docs:
        return True
    total = sum(len(d.page_content) for d in docs)
    if total == 0:
        return True
    garbled = sum(len(_GARBLE_PATTERN.findall(d.page_content)) for d in docs)
    return garbled / max(total, 1) > 0.05


def _ocr_pdf(path: str) -> list[Document]:
    """Fallback OCR pour PDF scannés (image-based).

    Utilise pdf2image + pytesseract comme solution de dernier recours.
    Si les dépendances ne sont pas disponibles, retourne un document
    avec un avertissement explicite.
    """
    try:
        from pdf2image import convert_from_path
        import pytesseract
    except ImportError:
        logger.warning(
            "PDF scanné détetecté mais dépendances OCR manquantes. "
            "Installez : pip install pdf2image pytesseract"
        )
        return [Document(
            page_content=(
                f"ERREUR OCR: Le fichier {Path(path).name} est un PDF scanné (image) "
                "et les dépendances OCR ne sont pas installées. "
                "Installez pdf2image + pytesseract ou fournissez un PDF texte."
            ),
            metadata={"source": path, "ocr_status": "dependencies_missing"},
        )]

    try:
        images = convert_from_path(path, dpi=300)
        pages_text: list[str] = []
        for i, img in enumerate(images):
            text = pytesseract.image_to_string(img, lang="fra")
            if text.strip():
                pages_text.append(text)

        if not pages_text:
            return [Document(
                page_content=f"ERREUR OCR: Aucun texte extrait de {Path(path).name}.",
                metadata={"source": path, "ocr_status": "empty_output"},
            )]

        return [
            Document(page_content=txt, metadata={"source": path, "page": i, "ocr_status": "success"})
            for i, txt in enumerate(pages_text)
        ]
    except Exception as exc:
        logger.error("Échec OCR pour %s : %s", path, exc)
        return [Document(
            page_content=f"ERREUR OCR: {exc}",
            metadata={"source": path, "ocr_status": "error"},
        )]


class DocumentLoadError(Exception):
    """Erreur lors du chargement d'un document."""
    pass


class DocumentLoadWarning(UserWarning):
    """Avertissement lors du chargement d'un document (non bloquant)."""
    pass


# ---------------------------------------------------------------------------
# Fonctions atomiques
# ---------------------------------------------------------------------------


def _get_loader(path: str) -> PyPDFLoader | Docx2txtLoader:
    """Retourne le loader approprié selon l'extension du fichier.

    Args:
        path: Chemin absolu du fichier.

    Returns:
        Instance du loader LangChain correspondant.

    Raises:
        DocumentLoadError: Si l'extension n'est pas supportée.
    """
    ext = Path(path).suffix.lower()
    if ext == ".pdf":
        return PyPDFLoader(path)
    if ext == ".docx":
        return Docx2txtLoader(path)
    raise DocumentLoadError(f"Extension non supportée : {ext}")


def load_document(path: str) -> list[Document]:
    """Charge un document depuis un chemin fichier.

    Args:
        path: Chemin absolu vers un fichier PDF ou DOCX.

    Returns:
        Liste de documents LangChain extraits du fichier.

    Raises:
        DocumentLoadError: Si le fichier ne peut pas être chargé.
        FileNotFoundError: Si le fichier n'existe pas.
    """
    if not os.path.isfile(path):
        raise FileNotFoundError(f"Fichier introuvable : {path}")
    try:
        loader = _get_loader(path)
        docs = loader.load()
        logger.info("Chargé : %s (%d pages/sections)", Path(path).name, len(docs))

        docs = _repair_all_documents(docs)

        if _has_garbled_content(docs) and Path(path).suffix.lower() == ".pdf":
            logger.warning(
                "Contenu garbled détecté dans %s, tentative de fallback OCR…",
                Path(path).name,
            )
            ocr_docs = _ocr_pdf(path)
            if ocr_docs and any(d.metadata.get("ocr_status") == "success" for d in ocr_docs):
                docs = ocr_docs
                logger.info("OCR réussi pour %s (%d pages)", Path(path).name, len(docs))

        return docs
    except DocumentLoadError:
        raise
    except Exception as exc:
        raise DocumentLoadError(f"Erreur chargement {path} : {exc}") from exc


def _repair_all_documents(docs: list[Document]) -> list[Document]:
    """Applique la réparation d'encodement à tous les documents."""
    repaired = []
    for doc in docs:
        original_len = len(doc.page_content)
        repaired_content = _repair_text(doc.page_content)
        if repaired_content != doc.page_content:
            chars_fixed = abs(len(repaired_content) - original_len)
            logger.info(
                "Réparation d'encodage : %d caractères corrigés pour %s",
                chars_fixed, doc.metadata.get("source", "?"),
            )
        repaired.append(Document(
            page_content=repaired_content,
            metadata=doc.metadata,
        ))
    return repaired


def _is_supported_file(filename: str) -> bool:
    """Vérifie si un fichier a une extension supportée.

    Args:
        filename: Nom du fichier (avec extension).

    Returns:
        True si l'extension est supportée.
    """
    return Path(filename).suffix.lower() in SUPPORTED_EXTENSIONS


def scan_directory(directory: str) -> list[Document]:
    """Parcourt récursivement un répertoire et charge tous les documents supportés.

    Args:
        directory: Chemin du répertoire à scanner.

    Returns:
        Liste de tous les documents chargés.

    Raises:
        FileNotFoundError: Si le répertoire n'existe pas.
        ValueError: Si aucun document valide n'est trouvé.
    """
    if not os.path.isdir(directory):
        raise FileNotFoundError(f"Répertoire introuvable : {directory}")

    all_docs: list[Document] = []
    errors: list[tuple[str, str]] = []
    
    for root, _dirs, files in os.walk(directory):
        for filename in files:
            if not _is_supported_file(filename):
                continue
            filepath = os.path.join(root, filename)
            try:
                all_docs.extend(load_document(filepath))
            except (DocumentLoadError, FileNotFoundError) as exc:
                error_msg = str(exc)
                errors.append((filename, error_msg))
                logger.warning("Ignoré %s : %s", filename, error_msg)

    logger.info("Scan terminé : %d documents chargés depuis %s", len(all_docs), directory)
    
    # Afficher un résumé des erreurs s'il y en a
    if errors:
        logger.warning("%d fichier(s) ignoré(s) sur %d au total :", len(errors), len(errors) + len(all_docs))
        for filename, error in errors[:5]:  # Limiter à 5 erreurs affichées
            logger.warning("  - %s : %s", filename, error[:80])
        if len(errors) > 5:
            logger.warning("  ... et %d autres", len(errors) - 5)
    
    if not all_docs:
        raise ValueError(
            f"Aucun document valide trouvé dans '{directory}'. "
            f"Vérifiez que le dossier contient des fichiers PDF ou DOCX."
        )
    
    return all_docs


def split_documents(
    documents: list[Document],
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
) -> list[Document]:
    """Découpe une liste de documents en chunks.

    Args:
        documents: Documents source à découper.
        chunk_size: Taille maximale d'un chunk en caractères.
        chunk_overlap: Chevauchement entre chunks consécutifs.

    Returns:
        Liste de chunks (documents découpés).

    Raises:
        ValueError: Si la liste de documents est vide.
    """
    if not documents:
        raise ValueError("Aucun document à découper.")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )
    chunks = splitter.split_documents(documents)
    logger.info(
        "%d documents → %d chunks (taille=%d, overlap=%d)",
        len(documents),
        len(chunks),
        chunk_size,
        chunk_overlap,
    )
    return chunks


DOMAIN_KEYWORDS: set[str] = {
    "robinet", "r0", "r1", "r2", "r3", "r4", "détente", "gaz",
    "gazfio", "francel", "vs_gazfio", "vanne", "pression",
    "consignation", "déconsignation", "bypass", "by-pass",
    "sécurité", "epi", "poste", "sectionnement",
}


def check_document_quality(docs: list[Document], min_chars: int = 200) -> dict:
    """Vérifie la qualité des documents chargés.

    Args:
        docs: Documents à vérifier.
        min_chars: Nombre minimum de caractères total attendu.

    Returns:
        Dictionnaire avec les résultats de qualité:
        - total_chars: nombre total de caractères
        - domain_score: ratio de mots-clés domaine trouvés (0.0-1.0)
        - is_adequate: True si le document est suffisant
        - details: liste de messages d'avertissement
    """
    details: list[str] = []
    total_chars = sum(len(d.page_content) for d in docs)

    if total_chars < min_chars:
        details.append(
            f"Document trop court : {total_chars} car. (minimum {min_chars})."
        )

    all_text = " ".join(d.page_content.lower() for d in docs)
    found_keywords = {kw for kw in DOMAIN_KEYWORDS if kw in all_text}
    domain_score = len(found_keywords) / max(len(DOMAIN_KEYWORDS), 1)

    if domain_score < 0.1:
        details.append(
            f"Score domaine faible : {domain_score:.2f} "
            f"({len(found_keywords)}/{len(DOMAIN_KEYWORDS)} mots-clés trouvés). "
            "Le document peut ne pas concerner le secteur gazier."
        )

    return {
        "total_chars": total_chars,
        "domain_score": domain_score,
        "keywords_found": sorted(found_keywords),
        "is_adequate": total_chars >= min_chars and domain_score >= 0.05,
        "details": details,
    }