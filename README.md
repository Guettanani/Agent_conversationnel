# VR Scenario Library

> **Générateur de scénarios de formation VR pour le secteur gazier**
> Version 1.0.0 — Python 3.10+

---

## Table des matières

1. [Description du projet](#1-description-du-projet)
2. [Prérequis techniques](#2-prérequis-techniques)
3. [Installation](#3-installation)
4. [Utilisation](#4-utilisation)
5. [Architecture](#5-architecture)
6. [Tests](#6-tests)
7. [Dépannage](#7-dépannage)
8. [Licence](#8-licence)

---

## 1. Description du projet

### 1.1 Objectif

**VR Scenario Library** est une bibliothèque Python conçue pour générer automatiquement des scénarios de formation en réalité virtuelle destinés aux opérateurs de postes de détente gaz. Elle s'appuie sur une architecture **RAG (Retrieval-Augmented Generation)** pour produire des scénarios pédagogiques structurés, validés et prêts à être intégrés dans un moteur Unity VR.

### 1.2 Contexte

Les procédures de consignation/déconsignation et de bypass sur les postes de détente gaz (GAZFIO, FRANCEL) nécessitent une formation rigoureuse et répétitive. La génération manuelle de scénarios VR est chronophage et sujette aux incohérences. Cette bibliothèque automatise la création de scénarios à partir de documents techniques (procédures GRDF, fiches de sécurité), garantissant :

- La **conformité** aux procédures opérationnelles réelles
- La **traçabilité** des informations sources
- La **reproductibilité** des scénarios
- L'**absence d'hallucinations** (toutes les consignes sont étayées par les documents)

### 1.3 Fonctionnalités principales

| Fonctionnalité | Description |
|----------------|-------------|
| **Chargement documentaire** | Support PDF et DOCX avec réparation automatique de l'encodage et fallback OCR pour les PDF scannés |
| **Indexation vectorielle** | Construction d'un index FAISS (ou fallback numpy) pour la recherche sémantique |
| **Retrieval MMR** | Recherche par pertinence maximale marginale (Maximal Marginal Relevance) |
| **Génération RAG** | Production de scénarios textuels structurés via LLM (OpenRouter/HuggingFace) |
| **Conversion JSON** | Transformation automatique en schéma JSON compatible Unity VR |
| **Validation structurelle** | Vérification de la conformité du JSON généré avant export |
| **Persistance de sessions** | Sauvegarde des scénarios et historique de discussion |
| **Mode batch** | Génération directe depuis la ligne de commande |
| **Mode interactif vocal** | Interface complète STT/TTS pour formation immersive |
| **Mode interactif texte** | Discussion multi-tours avec le formateur VR |

### 1.4 Flux global

```
Documents (PDF/DOCX)
       │
       ▼
┌──────────────────┐
│ scan_directory() │ → Chargement + réparation encodage
│ split_documents()│ → Découpage en chunks
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│build_vectorstore │ → Indexation FAISS / numpy
│create_retriever  │ → Configuration MMR
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│generate_scenario │ → Retrieval + Prompt + LLM → Scénario texte
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│convert_scenario  │ → Conversion JSON + Validation schéma
│  _to_json        │
└────────┬─────────┘
         │
         ▼
    scenario_output.json
```

---

## 2. Prérequis techniques

### 2.1 Environnement

| Composant | Version | Remarque |
|-----------|---------|----------|
| **Python** | 3.10, 3.11 ou 3.12 | 3.12 recommandé |
| **Système d'exploitation** | Windows 10/11, Linux, macOS | Testé sur Windows 10 |
| **pip** | 23.0+ | Pour l'installation des dépendances |
| **Espace disque** | ~2 Go | Modèles LLM + index FAISS |
| **RAM** | 8 Go minimum | 16 Go recommandé pour gros corpus |

### 2.2 Dépendances principales

| Package | Version | Usage |
|---------|---------|-------|
| `langchain-core` | 1.4.x | Classes de base RAG |
| `langchain-community` | 0.4.x | Loaders PDF/DOCX, FAISS |
| `langchain-text-splitters` | 1.1.x | Découpage de documents |
| `langchain-huggingface` | 1.2.x | Embeddings HuggingFace |
| `sentence-transformers` | 5.5.x | Modèle d'embedding par défaut |
| `openai` | — | Compatibilité API OpenRouter |
| `python-dotenv` | 1.2.x | Variables d'environnement |
| `numpy` | 2.4.x | Fallback vectorstore |
| `requests` | 2.34.x | Appels API HTTP |
| `pydantic` | 2.13.x | Validation des données |

### 2.3 Dépendances optionnelles

| Package | Version | Usage | Mode |
|---------|---------|-------|------|
| `faiss-cpu` | 1.14.x | Vectorstore performant | Recommandé |
| `faiss-gpu` | 1.7.x | Vectorstore GPU | Optionnel |
| `faster-whisper` | 1.2.x | Reconnaissance vocale | Mode vocal |
| `SpeechRecognition` | 3.16.x | Capture audio | Mode vocal |
| `pyttsx3` | — | Synthèse vocale | Mode vocal |
| `gTTS` | 2.5.x | Synthèse vocale Google | Mode vocal |
| `pygame` | 2.6.x | Lecture audio | Mode vocal |
| `torch` | 2.12.x | Modèles transformers | Mode vocal |
| `pdf2image` | — | Conversion PDF → image | Fallback OCR |
| `pytesseract` | — | OCR pour PDF scannés | Fallback OCR |
| `pytest` | 9.0.x | Tests unitaires | Développement |

### 2.4 Services externes

| Service | Usage | Clé API requise |
|---------|-------|-----------------|
| **OpenRouter** | LLM + Embeddings | `OPENROUTER_API_KEY` |
| **HuggingFace** | LLM + Embeddings (alternatif) | `HF_TOKEN` ou `HUGGINGFACE_API_KEY` |

> **Note** : Au moins un fournisseur LLM doit être configuré. OpenRouter est recommandé car il supporte les deux endpoints (chat + embeddings) avec une seule clé.

---

## 3. Installation

### 3.1 Cloner le dépôt

```bash
git clone https://github.com/example/vr-scenario-lib.git
cd vr_scenario_lib
```

### 3.2 Créer un environnement virtuel

```bash
# Création
python -m venv venv

# Activation — Windows
venv\Scripts\activate

# Activation — Linux/macOS
source venv/bin/activate
```

### 3.3 Installer les dépendances

```bash
# Installation de base
pip install -r requirements_vocal_fixed.txt

# Installation du package en mode développement
pip install -e .

# Installation des outils de développement (optionnel)
pip install -e ".[dev]"

# Installation du support GPU (optionnel, nécessite CUDA)
pip install -e ".[gpu]"
```

### 3.4 Configurer les variables d'environnement

Créez un fichier `.env` à la racine du projet :

```env
# === Configuration LLM (au moins un requis) ===

# Option 1 : OpenRouter (recommandé)
OPENROUTER_API_KEY=sk-or-v1-votre-cle-ici
OPENROUTER_API_URL=https://openrouter.ai/api/v1/chat/completions
LLM_MODEL=meta-llama/llama-3.3-70b-instruct:free

# Option 2 : HuggingFace (alternatif)
# HF_TOKEN=hf_votre-token-ici
# HUGGINGFACE_API_URL=https://api-inference.hf.co

# === Configuration optionnelle ===

# Modèle d'embeddings (défaut: sentence-transformers/all-MiniLM-L6-v2)
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

# Périphérique embedding (cpu ou cuda)
DEVICE=cpu

# Niveau de log (DEBUG, INFO, WARNING, ERROR)
LOG_LEVEL=INFO
```

### 3.5 Vérifier l'installation

```bash
# Vérifier que le package est importable
python -c "from vr_scenario_lib import build_llm_config; print('OK')"

# Vérifier la CLI
python -m vr_scenario_lib.main --help
```

### 3.6 Préparer les documents source

Placez vos documents (PDF ou DOCX) dans le répertoire `./documents/` :

```bash
# Structure attendue
documents/
├── procedure_consignation.pdf
├── procedure_deconsignation.docx
└── ...
```

> **Important** : Les documents doivent contenir des informations sur les procédures gazières (postes GAZFIO/FRANCEL, vannes R0-R4, VS_GAZFIO, etc.) pour que les scénarios générés soient pertinents.

---

## 4. Utilisation

### 4.1 Mode batch (génération directe)

Le mode batch génère un scénario à partir d'un thème et sauvegarde le résultat en JSON.

```bash
python -m vr_scenario_lib.main \
    --docs-dir ./documents \
    --topic "bypass gaz poste GAZFIO" \
    --output scenario_output.json \
    --scenarios-dir ./scenarios \
    --log-level INFO
```

**Paramètres disponibles :**

```bash
python -m vr_scenario_lib.main \
    --docs-dir ./documents \       # Répertoire des documents source
    --topic "consignation gaz" \   # Thème du scénario
    --output result.json \         # Chemin du fichier JSON de sortie
    --scenarios-dir ./scenarios \  # Répertoire de persistance
    --faiss-index-dir ./faiss_index \  # Répertoire index FAISS
    --log-level DEBUG \            # Niveau de verbosité
    --chunk-size 1200 \            # Taille des chunks
    --chunk-overlap 150 \          # Chevauchement des chunks
    --retriever-k 5                # Nombre de documents à récupérer
```

### 4.2 Mode texte interactif

Lance une session interactive avec discussion multi-tours :

```bash
python -m vr_scenario_lib.main --text
```

### 4.3 Mode vocal interactif

Lance une session complète avec reconnaissance vocale et synthèse vocale :

```bash
python -m vr_scenario_lib.main --voice \
    --stt-backend whisper \
    --tts-backend pyttsx3 \
    --whisper-model base
```

### 4.4 Reprendre une session existante

```bash
python -m vr_scenario_lib.main --continue mon-scenario-id
```

### 4.5 Utilisation en tant que bibliothèque Python

```python
from vr_scenario_lib.config import build_llm_config
from vr_scenario_lib.documents import scan_directory, split_documents
from vr_scenario_lib.vectorstore import (
    create_embeddings, build_vectorstore, create_retriever,
    load_vectorstore, save_vectorstore
)
from vr_scenario_lib.pipeline import run_pipeline

# 1. Configuration
llm_config = build_llm_config()  # Lit depuis .env

# 2. Chargement des documents
raw_docs = scan_directory("./documents")
chunks = split_documents(raw_docs, chunk_size=1200, chunk_overlap=150)

# 3. Création de l'index vectoriel
embeddings = create_embeddings()
vectorstore = build_vectorstore(chunks, embeddings)
save_vectorstore(vectorstore, "./faiss_index")

# 4. Ou chargement d'un index existant
# vectorstore = load_vectorstore("./faiss_index", embeddings)

# 5. Création du retriever
retriever = create_retriever(vectorstore, k=5)

# 6. Génération du scénario
result = run_pipeline(
    topic="bypass gaz poste GAZFIO",
    retriever=retriever,
    llm_config=llm_config,
    output_path="scenario_output.json",
    store_dir="./scenarios",
)

print(f"Scénario généré : {result['titre']}")
print(f"Nombre d'étapes : {len(result['etapes'])}")
```

### 4.6 Mode narrate (annonce narrative)

Génère un scénario avec annonce vocale/textuelle fluide :

```bash
python -m vr_scenario_lib.main --narrate
```

---

## 5. Architecture

### 5.1 Structure du projet

```
vr_scenario_lib/
├── documents/                    # Documents source (PDF/DOCX)
├── faiss_index/                  # Index vectoriel persisté
├── scenarios/                    # Sessions de scénarios sauvegardées
├── vr_scenario_lib/              # Package principal
│   ├── __init__.py
│   ├── main.py                   # Point d'entrée CLI
│   ├── config.py                 # Configuration, prompts, schémas
│   ├── documents.py              # Chargement + réparation + OCR
│   ├── vectorstore.py            # Embeddings + FAISS/numpy + retriever
│   ├── llm.py                    # Appels LLM avec fallback
│   ├── scenario.py               # Génération de scénarios
│   ├── prompts.py                # Templates de prompts
│   ├── pipeline.py               # Orchestration complète
│   ├── json_converter.py         # Conversion JSON Unity
│   ├── scenario_store.py         # Persistance des sessions
│   └── conversational_agent.py   # Agent interactif (voix/texte)
├── tests_validation.py           # Tests unitaires existants
├── tests_regression.py           # Tests de régression
├── setup.py                      # Configuration package
├── requirements_vocal_fixed.txt  # Dépendances
├── .env                          # Variables d'environnement (à créer)
└── .env.example                  # Template d'environnement
```

### 5.2 Schéma d'architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        CLI (main.py)                         │
│              --topic / --voice / --text / --narrate          │
└──────────────────────────┬──────────────────────────────────┘
                           │
          ┌────────────────┼────────────────┐
          ▼                ▼                ▼
   ┌────────────┐  ┌─────────────┐  ┌─────────────┐
   │  DOCUMENTS │  │ VECTORSTORE │  │    LLM      │
   │            │  │             │  │             │
   │ PDF/DOCX   │  │ FAISS/numpy │  │ OpenRouter/ │
   │ → repair   │  │ → MMR       │  │ HuggingFace │
   │ → chunks   │  │   retriever │  │ → fallback  │
   └─────┬──────┘  └──────┬──────┘  └──────┬──────┘
         │                │                │
         └────────────────┼────────────────┘
                          ▼
                  ┌───────────────┐
                  │   PIPELINE    │
                  │               │
                  │ 1. generate   │
                  │ 2. convert    │
                  │ 3. validate   │
                  └───────┬───────┘
                          ▼
                  scenario_output.json
```

---

## 6. Tests

### 6.1 Lancer tous les tests

```bash
# Tests unitaires existants
python -m pytest tests_validation.py -v

# Tests de régression (anti-refusal, encodage, vectorstore)
python -m pytest tests_regression.py -v

# Tous les tests avec couverture
python -m pytest tests_validation.py tests_regression.py -v --tb=short
```

### 6.2 Lancer un test spécifique

```bash
python -m pytest tests_regression.py::TestAntiRefusal -v
python -m pytest tests_regression.py::TestF_Extraction -v
python -m pytest tests_regression.py::TestNumpyVectorStore -v
```

### 6.3 Exécuter les tests sans pytest

```bash
python tests_regression.py
python tests_validation.py
```

### 6.4 Couverture de tests

```bash
python -m pytest tests_validation.py tests_regression.py --cov=vr_scenario_lib --cov-report=html
```

---

## 7. Dépannage

### 7.1 Erreur `ModuleNotFoundError: No module named 'faiss'`

**Cause** : FAISS n'est pas installé. Le système utilise automatiquement le fallback numpy, mais si vous voulez FAISS :

```bash
pip install faiss-cpu
```

### 7.2 Erreur `402 Payment Required` (OpenRouter)

**Cause** : Crédits insuffisants sur votre compte OpenRouter.

**Solution** :
1. Vérifiez vos crédits sur https://openrouter.ai/settings/credits
2. Rechargez votre compte
3. Ou passez à HuggingFace en configurant `HF_TOKEN`

### 7.3 Erreur `UnboundLocalError: cannot access local variable 'cleaned'`

**Cause** : Bug dans une version antérieure de `_repair_text()`.

**Solution** : Assurez-vous d'avoir la dernière version de `documents.py` (la variable `cleaned` est initialisée avec `text.replace("�", "é")` avant les substitutions).

### 7.4 PDF scanné ne retourne aucun texte

**Cause** : PDF image-based sans OCR.

**Solution** : Installez les dépendances OCR :

```bash
pip install pdf2image pytesseract
# Installez également Tesseract-OCR sur votre système
# Windows : https://github.com/UB-Mannheim/tesseract/wiki
# Linux : sudo apt install tesseract-ocr-fra
```

### 7.5 `NotImplementedError: max_marginal_relevance_search`

**Cause** : Version incompatible de langchain-core avec le fallback numpy.

**Solution** : La version actuelle de `vectorstore.py` implémente `max_marginal_relevance_search()`. Mettez à jour le package :

```bash
pip install -e . --force-reinstall
```

---

## 8. Licence

Ce projet est distribué sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

---

## Contact

- **Auteur** : VR Scenario Library Team
- **Email** : contact@example.com
- **Repository** : https://github.com/example/vr-scenario-lib

---

*Dernière mise à jour : Juin 2026*
