# # # # # #!/usr/bin/env python3
# # # # # """
# # # # # Application vocale de conversation avec scénarios VR.

# # # # # Cette application permet de :
# # # # # 1. Générer un scénario VR textuelle en spécifiant un thème (parole ou texte)
# # # # # 2. Discuter avec le scénario généré de manière entièrement vocale (TTS et reconnaissance vocale)

# # # # # Usage:
# # # # #     python scenario_conversation_app_vocal_only_fixed.py
# # # # # """

# # # # # import os
# # # # # import sys
# # # # # import logging
# # # # # import uuid
# # # # # import threading
# # # # # import time
# # # # # from typing import Optional, List, Dict, Any

# # # # # # Configuration du logging
# # # # # logging.basicConfig(
# # # # #     level=logging.INFO,
# # # # #     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
# # # # # )
# # # # # logger = logging.getLogger(__name__)

# # # # # # Ajout du répertoire parent au chemin pour les imports
# # # # # sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# # # # # from vr_scenario_lib.scenario import generate_scenario
# # # # # from vr_scenario_lib.scenario_store import ScenarioSession
# # # # # from vr_scenario_lib.config import LLMConfig, build_llm_config
# # # # # from langchain_core.documents import Document

# # # # # # Import pour le TTS et la reconnaissance vocale
# # # # # TTS_AVAILABLE = True  # Toujours vrai pour forcer le mode vocal
# # # # # try:
# # # # #     import torch
# # # # #     import sounddevice as sd
# # # # #     import soundfile as sf
# # # # #     from faster_whisper import WhisperModel
# # # # #     from TTS.api import TTS
# # # # #     logger.info("Bibliothèques TTS et STT importées avec succès")
# # # # # except ImportError as e:
# # # # #     TTS_AVAILABLE = False
# # # # #     logger.error(f"Erreur lors de l'import des bibliothèques : {e}")
# # # # #     print("Attention : Les bibliothèques pour le TTS et la reconnaissance vocale ne sont pas installées.")
# # # # #     print("Le mode vocal sera désactivé.")
# # # # #     print("Pour installer les dépendances nécessaires :")
# # # # #     print("pip install faster-whisper TTS torch sounddevice soundfile")

# # # # # # Initialisation du modèle Whisper
# # # # # whisper_model = None
# # # # # if TTS_AVAILABLE:
# # # # #     try:
# # # # #         logger.info("Initialisation du modèle Whisper...")
# # # # #         # Utiliser le petit modèle pour une reconnaissance rapide
# # # # #         whisper_model = WhisperModel("tiny", device="cpu", compute_type="int8")
# # # # #         logger.info("Modèle Whisper initialisé avec succès")
# # # # #     except Exception as e:
# # # # #         logger.error(f"Erreur lors de l'initialisation de Whisper : {e}")
# # # # #         TTS_AVAILABLE = False

# # # # # # Initialisation du TTS
# # # # # tts_model = None
# # # # # if TTS_AVAILABLE:
# # # # #     try:
# # # # #         logger.info("Initialisation du modèle TTS...")
# # # # #         # Initialiser le modèle TTS
# # # # #         tts_model = TTS(model_name="tts_models/fr/css10/vits", progress_bar=False)
# # # # #         logger.info("Modèle TTS initialisé avec succès")
# # # # #     except Exception as e:
# # # # #         logger.error(f"Erreur lors de l'initialisation du TTS : {e}")
# # # # #         TTS_AVAILABLE = False


# # # # # def speak(text: str) -> None:
# # # # #     """
# # # # #     Fonction pour faire parler le système avec le TTS.

# # # # #     Args:
# # # # #         text: Le texte à convertir en parole
# # # # #     """
# # # # #     if not TTS_AVAILABLE or not tts_model:
# # # # #         print(f"[TTS] {text}")
# # # # #         return

# # # # #     def _speak():
# # # # #         try:
# # # # #             logger.info(f"Génération audio pour : {text[:50]}...")

# # # # #             # Générer un fichier audio temporaire
# # # # #             output_file = f"temp_audio_{uuid.uuid4().hex[:8]}.wav"

# # # # #             # Générer l'audio avec le modèle TTS
# # # # #             tts_model.tts_to_file(
# # # # #                 text=text, 
# # # # #                 file_path=output_file, 
# # # # #                 speaker=tts_model.speakers[0], 
# # # # #                 language="fr"
# # # # #             )

# # # # #             logger.info(f"Fichier audio généré : {output_file}")

# # # # #             # Jouer le fichier audio
# # # # #             data, samplerate = sf.read(output_file)
# # # # #             sd.play(data, samplerate)
# # # # #             logger.info("Lecture audio en cours...")
# # # # #             sd.wait()  # Attendre la fin de la lecture

# # # # #             # Supprimer le fichier temporaire
# # # # #             os.remove(output_file)
# # # # #             logger.info("Fichier audio temporaire supprimé")

# # # # #         except Exception as e:
# # # # #             logger.error(f"Erreur lors de la synthèse vocale : {e}")
# # # # #             print(f"[TTS] {text}")

# # # # #     # Exécuter dans un thread pour ne pas bloquer
# # # # #     thread = threading.Thread(target=_speak)
# # # # #     thread.start()


# # # # # def ask_question(question: str) -> Optional[str]:
# # # # #     """
# # # # #     Fonction pour poser une question et attendre une réponse vocale.
# # # # #     Ne passe jamais en mode texte.

# # # # #     Args:
# # # # #         question: La question à poser

# # # # #     Returns:
# # # # #         La réponse de l'utilisateur ou None
# # # # #     """
# # # # #     # Toujours utiliser le TTS pour poser la question
# # # # #     logger.info(f"Posing question: {question}")
# # # # #     speak(question)
# # # # #     print(f"Question : {question}")
# # # # #     speak("Je vous écoute...")

# # # # #     # Tentatives de reconnaissance vocale
# # # # #     attempts = 0
# # # # #     max_attempts = 3

# # # # #     while attempts < max_attempts:
# # # # #         user_response = listen(timeout=10, phrase_time_limit=15)

# # # # #         if user_response:
# # # # #             return user_response

# # # # #         attempts += 1
# # # # #         if attempts < max_attempts:
# # # # #             speak("Je n'ai pas bien compris. Veuillez répéter votre réponse.")
# # # # #             logger.info(f"Reconnaissance vocale échouée, tentative {attempts}/{max_attempts}")

# # # # #     # Après 3 tentatives, redemander la question
# # # # #     logger.info("3 tentatives de reconnaissance vocale échouées, redemandage de la question")
# # # # #     speak("Je n'arrive pas à vous comprendre. Je vais redemander ma question.")
# # # # #     return ask_question(question)


# # # # # def listen(timeout: int = 5, phrase_time_limit: int = 10) -> Optional[str]:
# # # # #     """
# # # # #     Fonction pour écouter et reconnaître la parole de l'utilisateur.

# # # # #     Args:
# # # # #         timeout: Temps d'attente maximal en secondes
# # # # #         phrase_time_limit: Durée maximale de la phrase à reconnaître

# # # # #     Returns:
# # # # #         Le texte reconnu ou None en cas d'erreur
# # # # #     """
# # # # #     if not TTS_AVAILABLE or not whisper_model:
# # # # #         logger.warning("Mode vocal non disponible")
# # # # #         return None

# # # # #     try:
# # # # #         logger.info("Début de l'enregistrement audio...")

# # # # #         # Enregistrer l'audio
# # # # #         sample_rate = 16000
# # # # #         duration = timeout  # secondes

# # # # #         print("Écoute...")
# # # # #         logger.info(f"Enregistrement audio ({timeout}s)...")

# # # # #         # Enregistrer l'audio
# # # # #         audio_data = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype='float32')
# # # # #         sd.wait()  # Attendre la fin de l'enregistrement

# # # # #         logger.info("Enregistrement terminé, traitement en cours...")

# # # # #         # Sauvegarder temporairement
# # # # #         temp_file = f"temp_audio_{uuid.uuid4().hex[:8]}.wav"
# # # # #         sf.write(temp_file, audio_data, sample_rate)

# # # # #         logger.info(f"Fichier temporaire créé : {temp_file}")

# # # # #         # Transcrire avec Whisper
# # # # #         logger.info("Transcription avec Whisper...")
# # # # #         segments, info = whisper_model.transcribe(temp_file, language="fr", beam_size=5)
# # # # #         text = " ".join([segment.text for segment in segments])

# # # # #         logger.info(f"Texte transcrit : {text}")

# # # # #         # Supprimer le fichier temporaire
# # # # #         os.remove(temp_file)
# # # # #         logger.info("Fichier audio temporaire supprimé")

# # # # #         print(f"Reconnu : {text}")
# # # # #         return text

# # # # #     except Exception as e:
# # # # #         logger.error(f"Erreur lors de l'écoute : {e}")
# # # # #         speak("Désolé, une erreur est survenue lors de l'écoute.")
# # # # #         return None


# # # # # def setup_llm_config() -> LLMConfig:
# # # # #     """Configure le LLM avec des paramètres par défaut ou à partir de variables d'environnement."""
# # # # #     try:
# # # # #         config = build_llm_config()
# # # # #     except ValueError:
# # # # #         # Si aucun token n'est trouvé, utiliser une configuration de base
# # # # #         config = build_llm_config(
# # # # #             token="dummy_token",
# # # # #             api_url="https://openrouter.ai/api/v1/chat/completions",
# # # # #             model="openai/gpt-3.5-turbo"
# # # # #         )

# # # # #     return config


# # # # # def create_sample_documents(topic: str) -> List[Any]:
# # # # #     """Crée des documents d'exemple pour un sujet donné."""
# # # # #     # Exemple de documents pour différents thèmes
# # # # #     sample_documents = {
# # # # #         "sécurité incendie": [
# # # # #             "La sécurité incendie en milieu professionnel comprend la prévention, la détection et l'évacuation.",
# # # # #             "Les extincteurs doivent être vérifiés mensuellement et entretenus annuellement.",
# # # # #             "Les exercices d'évacuation doivent avoir lieu au moins une fois par an."
# # # # #         ],
# # # # #         "premiers secours": [
# # # # #             "En cas de blessure, évaluez d'abord la scène pour vous assurer qu'elle est sûre.",
# # # # #             "Appelez les secours en cas de blessure grave ou d'urgence.",
# # # # #             "L'ordre des priorités est : Danger, Réponse, Respiration, Circulation (DRRC)."
# # # # #         ],
# # # # #         "procédures de laboratoire": [
# # # # #             "Portez toujours des équipements de protection individuelle (EPI) appropriés.",
# # # # #             "Lavez-vous les mains avant et après les manipulations.",
# # # # #             "Conservez les produits chimiques dans des armoires spécifiques avec étiquettes claires."
# # # # #         ],
# # # # #         "gaz": [
# # # # #             "La manipulation des gaz requiert des précautions spéciales pour éviter les fuites et les explosions.",
# # # # #             "Chaque gaz a ses propres propriétés et dangers spécifiques.",
# # # # #             "Les équipements de protection individuelle adaptés sont indispensables lors de la manipulation des gaz.",
# # # # #             "En cas de fuite de gaz, aérer immédiatement la zone et évacuer si nécessaire."
# # # # #         ]
# # # # #     }

# # # # #     # Utiliser les documents correspondants au sujet ou des documents par défaut
# # # # #     documents = sample_documents.get(topic.lower(), [
# # # # #         "Cette section contient des informations générales sur le sujet sélectionné.",
# # # # #         "Pour une meilleure expérience, veuillez fournir des documents spécifiques au sujet."
# # # # #     ])

# # # # #     # Créer des objets Document
# # # # #     return [Document(page_content=doc, metadata={"source": f"sample_{topic}_{i}"})
# # # # #             for i, doc in enumerate(documents)]


# # # # # def generate_scenario_text(topic: str, config: LLMConfig) -> str:
# # # # #     """Génère un scénario textuel à partir d'un thème."""
# # # # #     logger.info(f"Génération du scénario VR pour le thème : {topic}")

# # # # #     speak("Génération du scénario VR...")
# # # # #     print("\n" + "="*60)
# # # # #     print("GÉNÉRATION DE SCÉNARIO VR")
# # # # #     print("="*60)

# # # # #     # Créer des documents d'exemple
# # # # #     speak(f"Préparation du contexte pour le thème : {topic}")
# # # # #     print(f"Préparation du contexte pour le thème : {topic}")
# # # # #     documents = create_sample_documents(topic)

# # # # #     # Demander des consignes supplémentaires
# # # # #     speak("Voulez-vous ajouter des consignes supplémentaires pour le scénario ?")
# # # # #     custom_prompt = ""
# # # # #     if TTS_AVAILABLE:
# # # # #         speak("Dites-moi vos consignes ou attendez quelques secondes pour continuer.")
# # # # #         user_input = ask_question("Vos consignes supplémentaires :")
# # # # #         if user_input:
# # # # #             custom_prompt = user_input
# # # # #     else:
# # # # #         custom_prompt = input("\nAjoutez des consignes supplémentaires pour le scénario (laisser vide pour utiliser les paramètres par défaut) : ")

# # # # #     # Générer le scénario
# # # # #     print("\nGénération du scénario VR...")
# # # # #     scenario_text = f"""
# # # # # # SCÉNARIO VR SUR LE THÈME : {topic.upper()}

# # # # # ## Contexte
# # # # # Vous êtes un expert en formation professionnelle spécialisé dans le domaine du {topic}. 
# # # # # Vous devez créer un scénario de formation en réalité virtuelle qui simule une situation réaliste et instructive.

# # # # # ## Objectifs de formation
# # # # # - Comprendre les principes fondamentaux du {topic}
# # # # # - Maîtriser les procédures de base
# # # # # - Réagir correctement aux situations d'urgence
# # # # # - Appliquer les bonnes pratiques

# # # # # ## Scénario détaillé
# # # # # {" ".join(doc.page_content for doc in documents)}

# # # # # ## Consignes personnalisées
# # # # # {custom_prompt if custom_prompt else "Aucune consigne personnalisée ajoutée."}

# # # # # ## Évaluation des compétences
# # # # # À la fin de ce scénario, les apprenants seront évalués sur :
# # # # # 1. Leur compréhension des concepts clés
# # # # # 2. Leur application correcte des procédures
# # # # # 3. Leur réaction aux situations imprévues
# # # # # 4. Leur respect des protocoles de sécurité
# # # # # """

# # # # #     logger.info("Scénario VR généré avec succès")
# # # # #     return scenario_text


# # # # # def discuss_scenario(scenario_text: str, config: LLMConfig, topic: str) -> None:
# # # # #     """
# # # # #     Permet à l'utilisateur de discuter avec le scénario généré de manière vocale.

# # # # #     Args:
# # # # #         scenario_text: Le scénario VR généré
# # # # #         config: Configuration du LLM
# # # # #         topic: Le thème du scénario
# # # # #     """
# # # # #     logger.info("Début de la discussion avec le scénario VR")
# # # # #     speak("Maintenant, nous allons discuter du scénario que nous venons de générer.")
# # # # #     speak(f"Voici quelques questions sur le thème : {topic}")

# # # # #     # Créer une session pour la discussion
# # # # #     session = ScenarioSession(scenario_text)

# # # # #     # Questions ciblées
# # # # #     questions = [
# # # # #         f"Quels sont les principes de base de {topic} ?",
# # # # #         f"Quelles sont les procédures de sécurité essentielles en {topic} ?",
# # # # #         f"Comment réagir en cas d'urgence liée à {topic} ?"
# # # # #     ]

# # # # #     # Poser chaque question et attendre la réponse
# # # # #     for question in questions:
# # # # #         logger.info(f"Question posée : {question}")
# # # # #         user_response = ask_question(question)

# # # # #         if not user_response:
# # # # #             logger.info("Aucune réponse reçue, passage à la question suivante")
# # # # #             continue

# # # # #         # Vérifier si l'utilisateur veut poser sa propre question
# # # # #         if "oui" in user_response.lower() or "détail" in user_response.lower() or "expliquer" in user_response.lower():
# # # # #             logger.info("L'utilisateur souhaite plus de détails")
# # # # #             speak("Parlez-moi de ce qui vous intéresse.")
# # # # #             user_message = listen(timeout=10, phrase_time_limit=15)

# # # # #             if not user_message:
# # # # #                 logger.info("Aucun message de l'utilisateur, passage à la question suivante")
# # # # #                 continue

# # # # #             if user_message.lower() in ['quitter', 'exit', 'quit', 'au revoir']:
# # # # #                 logger.info("L'utilisateur souhaite quitter")
# # # # #                 speak("Au revoir !")
# # # # #                 print("Fin de la conversation.")
# # # # #                 return

# # # # #             # Obtenir une réponse du LLM
# # # # #             logger.info(f"Traitement de la question de l'utilisateur: {user_message}")
# # # # #             speak("Je réfléchis à votre question...")
# # # # #             print("\nScénario VR : ", end="")
# # # # #             try:
# # # # #                 from vr_scenario_lib.scenario import discuss_scenario
# # # # #                 reply = discuss_scenario(
# # # # #                     session=session,
# # # # #                     user_message=user_message,
# # # # #                     llm_config=config
# # # # #                 )
# # # # #                 print(reply)
# # # # #                 speak(reply)
# # # # #                 logger.info("Réponse du LLM générée et lue à voix haute")
# # # # #             except Exception as e:
# # # # #                 logger.error(f"Erreur lors de la discussion : {e}")
# # # # #                 error_msg = "Désolé, une erreur est survenue. Veuillez réessayer."
# # # # #                 print(error_msg)
# # # # #                 speak(error_msg)

# # # # #     # Passer en mode de questions libres
# # # # #     logger.info("Passage en mode de questions libres")
# # # # #     speak("Maintenant, vous pouvez poser toutes les questions que vous souhaitez sur le scénario.")
# # # # #     speak("Pour quitter, dites 'quitter' ou 'au revoir'.")
# # # # #     print("Pour quitter, dites 'quitter' ou 'au revoir'.")

# # # # #     while True:
# # # # #         # Demander une question à l'utilisateur
# # # # #         speak("Quelle est votre question ?")
# # # # #         user_message = listen()

# # # # #         if not user_message:
# # # # #             speak("Veuillez poser une question.")
# # # # #             continue

# # # # #         if user_message.lower() in ['quitter', 'exit', 'quit', 'au revoir']:
# # # # #             logger.info("L'utilisateur souhaite quitter")
# # # # #             speak("Au revoir !")
# # # # #             print("Fin de la conversation.")
# # # # #             break

# # # # #         # Obtenir une réponse du LLM
# # # # #         speak("Je réfléchis à votre question...")
# # # # #         print("\nScénario VR : ", end="")
# # # # #         try:
# # # # #             from vr_scenario_lib.scenario import discuss_scenario
# # # # #             reply = discuss_scenario(
# # # # #                 session=session,
# # # # #                 user_message=user_message,
# # # # #                 llm_config=config
# # # # #             )
# # # # #             print(reply)

# # # # #             # Lire la réponse à voix haute
# # # # #             speak(reply)
# # # # #             logger.info("Réponse du LLM générée et lue à voix haute")
# # # # #         except Exception as e:
# # # # #             logger.error(f"Erreur lors de la discussion : {e}")
# # # # #             error_msg = "Désolé, une erreur est survenue. Veuillez réessayer."
# # # # #             print(error_msg)
# # # # #             speak(error_msg)


# # # # # def main():
# # # # #     """Fonction principale de l'application."""
# # # # #     logger.info("Démarrage de l'application vocale de conversation avec scénarios VR")

# # # # #     print("\nBienvenue dans l'application vocale de conversation avec scénarios VR !")
# # # # #     speak("Bienvenue dans l'application vocale de conversation avec scénarios VR !")
# # # # #     print("Cette application vous permet de générer un scénario VR textuelle et d'en discuter de manière entièrement vocale.")
# # # # #     speak("Cette application vous permet de générer un scénario VR textuelle et d'en discuter de manière entièrement vocale.")

# # # # #     # Vérifier si le mode vocal est disponible
# # # # #     if not TTS_AVAILABLE:
# # # # #         logger.warning("Mode vocal non disponible, utilisation du mode texte")
# # # # #         print("\nAttention : Le mode vocal n'est pas disponible. Le fonctionnement sera en mode texte.")
# # # # #         speak("Attention : Le mode vocal n'est pas disponible. Le fonctionnement sera en mode texte.")

# # # # #     # Demander le thème du scénario
# # # # #     speak("Quel est le thème du scénario VR que vous souhaitez générer ?")
# # # # #     print("\nQuel est le thème du scénario VR que vous souhaitez générer ?")

# # # # #     if TTS_AVAILABLE:
# # # # #         speak("Dites-moi le thème ou attendez quelques secondes pour utiliser le thème par défaut.")
# # # # #         topic = listen(timeout=5, phrase_time_limit=10)
# # # # #         if not topic:
# # # # #             topic = "sécurité"
# # # # #             speak(f"Utilisation du thème par défaut : {topic}")
# # # # #     else:
# # # # #         topic = input("\nEntrez le thème du scénario (laisser vide pour 'sécurité') : ") or "sécurité"

# # # # #     # Configurer le LLM
# # # # #     config = setup_llm_config()

# # # # #     # Générer le scénario
# # # # #     scenario_text = generate_scenario_text(topic, config)

# # # # #     # Discuter avec le scénario
# # # # #     discuss_scenario(scenario_text, config, topic)

# # # # #     logger.info("Application terminée avec succès")


# # # # # if __name__ == "__main__":
# # # # #     main()
# # # # #!/usr/bin/env python3
# # # # """
# # # # Application vocale de conversation avec scenarios VR.
# # # # Version enterprise -- standards industriels.

# # # # Architecture
# # # # ------------
# # # # VoiceIO      : STT (faster-whisper + SpeechRecognition VAD) + TTS (pyttsx3/gTTS).
# # # # ask_voice()  : pose une question, 3 tentatives STT, fallback clavier garanti.
# # # # VRScenarioApp: orchestration metier (generation + discussion scenario).

# # # # Corrections vs version precedente
# # # # -----------------------------------
# # # # - Race condition TTS/STT eliminee : speak() est TOUJOURS bloquant avant listen().
# # # # - Recursion infinie supprimee     : boucle for bornee + fallback clavier reel.
# # # # - VAD reelle                      : SpeechRecognition detecte la fin de parole.
# # # # - Globals supprimes               : encapsulation dans VoiceIO.
# # # # - Thread TTS jointe               : pas d'audio orphelin a la sortie.
# # # # - Logging sans f-string           : lazy %s formatting partout.

# # # # Usage:
# # # #     python app_vocal.py
# # # #     python app_vocal.py --stt-backend google
# # # #     python app_vocal.py --tts-backend gtts
# # # #     python app_vocal.py --whisper-model small
# # # # """

# # # # from __future__ import annotations

# # # # import argparse
# # # # import logging
# # # # import os
# # # # import sys
# # # # import tempfile
# # # # import threading
# # # # import time
# # # # from dataclasses import dataclass
# # # # from typing import Optional

# # # # # ---------------------------------------------------------------------------
# # # # # Logging
# # # # # ---------------------------------------------------------------------------
# # # # logging.basicConfig(
# # # #     level=logging.INFO,
# # # #     format="%(asctime)s | %(name)-36s | %(levelname)-8s | %(message)s",
# # # #     datefmt="%H:%M:%S",
# # # # )
# # # # logger = logging.getLogger(__name__)

# # # # sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# # # # # ============================================================================
# # # # # Constantes
# # # # # ============================================================================

# # # # STT_MAX_ATTEMPTS      = 3
# # # # STT_LISTEN_TIMEOUT    = 8
# # # # STT_PHRASE_TIME_LIMIT = 20
# # # # STT_PROMPT_TIME_LIMIT = 120
# # # # STT_SILENCE_TIMEOUT   = 2.0
# # # # STT_PROMPT_SILENCE    = 3.5
# # # # STT_AMBIENT_DURATION  = 0.5
# # # # TTS_SPEECH_RATE       = 145
# # # # TTS_VOLUME            = 0.92
# # # # WHISPER_DEFAULT_MODEL = "base"
# # # # WHISPER_BEAM_SIZE     = 5
# # # # KEYBOARD_PROMPT       = "Saisissez votre reponse (ENTREE pour passer) : "
# # # # EXIT_WORDS            = {"quitter", "exit", "quit", "au revoir", "stop", "fin"}


# # # # # ============================================================================
# # # # # InputResult
# # # # # ============================================================================

# # # # @dataclass
# # # # class InputResult:
# # # #     """Resultat d'une interaction utilisateur."""
# # # #     text:     str = ""
# # # #     source:   str = "skipped"   # "stt" | "keyboard" | "skipped"
# # # #     attempts: int = 0

# # # #     def __bool__(self) -> bool:
# # # #         return bool(self.text)

# # # #     def is_exit(self) -> bool:
# # # #         return any(w in self.text.lower() for w in EXIT_WORDS)


# # # # # ============================================================================
# # # # # VoiceIO
# # # # # ============================================================================

# # # # class VoiceIO:
# # # #     """Couche bas-niveau STT + TTS.

# # # #     Regles fondamentales
# # # #     --------------------
# # # #     1. speak() est TOUJOURS bloquant dans le flux principal.
# # # #        Un TTS non-bloquant avant listen() = echo capture par Whisper.
# # # #     2. Le micro n'est jamais ouvert pendant la synthese vocale.
# # # #     3. L'enregistrement utilise la VAD (SpeechRecognition), pas une duree fixe.
# # # #     """

# # # #     def __init__(
# # # #         self,
# # # #         stt_backend:   str = "whisper",
# # # #         tts_backend:   str = "pyttsx3",
# # # #         language:      str = "fr",
# # # #         whisper_model: str = WHISPER_DEFAULT_MODEL,
# # # #     ) -> None:
# # # #         self.stt_backend      = stt_backend
# # # #         self.tts_backend      = tts_backend
# # # #         self.language         = language
# # # #         self.whisper_model_id = whisper_model

# # # #         self._recognizer    = None
# # # #         self._whisper_model = None
# # # #         self._tts_engine    = None
# # # #         self._lock_tts      = threading.Lock()

# # # #         self._init()

# # # #     # ------------------------------------------------------------------
# # # #     # Init
# # # #     # ------------------------------------------------------------------

# # # #     def _init(self) -> None:
# # # #         self._init_stt()
# # # #         self._init_tts()
# # # #         logger.info(
# # # #             "VoiceIO pret -- STT: %s | TTS: %s | Langue: %s",
# # # #             self.stt_backend, self.tts_backend, self.language,
# # # #         )

# # # #     def _init_stt(self) -> None:
# # # #         try:
# # # #             import speech_recognition as sr
# # # #             self._recognizer = sr.Recognizer()
# # # #             self._recognizer.energy_threshold        = 4000
# # # #             self._recognizer.pause_threshold         = STT_SILENCE_TIMEOUT
# # # #             self._recognizer.dynamic_energy_threshold = True
# # # #         except ImportError:
# # # #             raise RuntimeError(
# # # #                 "SpeechRecognition manquant. pip install SpeechRecognition PyAudio"
# # # #             )

# # # #         if self.stt_backend == "whisper":
# # # #             self._whisper_model = self._load_whisper()

# # # #     def _load_whisper(self) -> object:
# # # #         try:
# # # #             from faster_whisper import WhisperModel
# # # #             logger.info("Chargement faster-whisper '%s'...", self.whisper_model_id)
# # # #             model = WhisperModel(
# # # #                 self.whisper_model_id,
# # # #                 device="cpu",
# # # #                 compute_type="int8",
# # # #             )
# # # #             logger.info("faster-whisper pret")
# # # #             return model
# # # #         except ImportError:
# # # #             raise RuntimeError("faster-whisper manquant. pip install faster-whisper")

# # # #     def _init_tts(self) -> None:
# # # #         if self.tts_backend == "pyttsx3":
# # # #             self._init_pyttsx3()
# # # #         elif self.tts_backend == "gtts":
# # # #             self._check_gtts()
# # # #         else:
# # # #             raise ValueError("tts_backend doit etre 'pyttsx3' ou 'gtts'")

# # # #     def _init_pyttsx3(self) -> None:
# # # #         try:
# # # #             import pyttsx3
# # # #             engine = pyttsx3.init()
# # # #             engine.setProperty("rate",   TTS_SPEECH_RATE)
# # # #             engine.setProperty("volume", TTS_VOLUME)
# # # #             for v in engine.getProperty("voices"):
# # # #                 if "french" in v.name.lower() or "fr" in v.id.lower():
# # # #                     engine.setProperty("voice", v.id)
# # # #                     logger.info("Voix TTS : %s", v.name)
# # # #                     break
# # # #             self._tts_engine = engine
# # # #             logger.info("pyttsx3 initialise")
# # # #         except ImportError:
# # # #             logger.warning("pyttsx3 absent -- fallback gTTS")
# # # #             self.tts_backend = "gtts"
# # # #             self._check_gtts()

# # # #     def _check_gtts(self) -> None:
# # # #         try:
# # # #             import gtts    # noqa: F401
# # # #             import pygame  # noqa: F401
# # # #         except ImportError:
# # # #             raise RuntimeError("gTTS/pygame manquants. pip install gTTS pygame")

# # # #     # ------------------------------------------------------------------
# # # #     # TTS -- TOUJOURS bloquant dans le flux principal
# # # #     # ------------------------------------------------------------------

# # # #     def speak(self, text: str, *, blocking: bool = True) -> None:
# # # #         """Synthese vocale.

# # # #         blocking=True (defaut) : retourne apres la fin de la lecture.
# # # #         blocking=False          : usage exceptionnel (annonces non-critiques).
# # # #         Ne JAMAIS appeler avec blocking=False avant listen().
# # # #         """
# # # #         if not text or not text.strip():
# # # #             return
# # # #         logger.info("TTS: '%s'", text[:80])
# # # #         if self.tts_backend == "pyttsx3":
# # # #             self._speak_pyttsx3(text, blocking)
# # # #         else:
# # # #             self._speak_gtts(text, blocking)

# # # #     def _speak_pyttsx3(self, text: str, blocking: bool) -> None:
# # # #         with self._lock_tts:
# # # #             try:
# # # #                 self._tts_engine.say(text)
# # # #                 if blocking:
# # # #                     self._tts_engine.runAndWait()
# # # #                 else:
# # # #                     t = threading.Thread(
# # # #                         target=self._tts_engine.runAndWait, daemon=True
# # # #                     )
# # # #                     t.start()
# # # #             except Exception as exc:
# # # #                 logger.error("pyttsx3 erreur: %s", exc)
# # # #                 print("[TTS] " + text)

# # # #     def _speak_gtts(self, text: str, blocking: bool) -> None:
# # # #         tmp_path: Optional[str] = None
# # # #         try:
# # # #             from gtts import gTTS
# # # #             import pygame
# # # #             tts = gTTS(text=text, lang=self.language, slow=False)
# # # #             with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
# # # #                 tmp_path = f.name
# # # #                 tts.save(tmp_path)
# # # #             pygame.mixer.init()
# # # #             pygame.mixer.music.load(tmp_path)
# # # #             pygame.mixer.music.play()
# # # #             if blocking:
# # # #                 while pygame.mixer.music.get_busy():
# # # #                     time.sleep(0.05)
# # # #                 pygame.mixer.quit()
# # # #         except Exception as exc:
# # # #             logger.error("gTTS erreur: %s", exc)
# # # #             print("[TTS] " + text)
# # # #         finally:
# # # #             if tmp_path and os.path.exists(tmp_path):
# # # #                 try:
# # # #                     os.unlink(tmp_path)
# # # #                 except OSError:
# # # #                     pass

# # # #     # ------------------------------------------------------------------
# # # #     # STT -- VAD reelle
# # # #     # ------------------------------------------------------------------

# # # #     def listen(
# # # #         self,
# # # #         *,
# # # #         pause_threshold:   float = STT_SILENCE_TIMEOUT,
# # # #         phrase_time_limit: int   = STT_PHRASE_TIME_LIMIT,
# # # #         listen_timeout:    float = STT_LISTEN_TIMEOUT,
# # # #     ) -> str:
# # # #         """Capture parole (VAD) et transcrit.

# # # #         Returns:
# # # #             Texte transcrit non-vide.

# # # #         Raises:
# # # #             RuntimeError: Capture ou transcription impossible.
# # # #         """
# # # #         import speech_recognition as sr

# # # #         original = self._recognizer.pause_threshold
# # # #         self._recognizer.pause_threshold = pause_threshold
# # # #         tmp_path: Optional[str] = None

# # # #         try:
# # # #             # 1. Capture VAD
# # # #             try:
# # # #                 with sr.Microphone() as src:
# # # #                     logger.info(
# # # #                         "Ecoute (silence=%.1fs, max=%ds)...",
# # # #                         pause_threshold, phrase_time_limit,
# # # #                     )
# # # #                     self._recognizer.adjust_for_ambient_noise(
# # # #                         src, duration=STT_AMBIENT_DURATION
# # # #                     )
# # # #                     audio = self._recognizer.listen(
# # # #                         src,
# # # #                         timeout=listen_timeout,
# # # #                         phrase_time_limit=phrase_time_limit,
# # # #                     )
# # # #             except sr.WaitTimeoutError:
# # # #                 raise RuntimeError("Timeout -- aucun son detecte")

# # # #             # 2. Sauvegarde WAV
# # # #             with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
# # # #                 tmp_path = f.name
# # # #                 f.write(audio.get_wav_data())

# # # #             # 3. Transcription
# # # #             if self.stt_backend == "whisper":
# # # #                 return self._transcribe_whisper(tmp_path)
# # # #             else:
# # # #                 return self._transcribe_google(audio)

# # # #         finally:
# # # #             self._recognizer.pause_threshold = original
# # # #             if tmp_path and os.path.exists(tmp_path):
# # # #                 try:
# # # #                     os.unlink(tmp_path)
# # # #                 except OSError:
# # # #                     pass

# # # #     def _transcribe_whisper(self, wav_path: str) -> str:
# # # #         segments_gen, info = self._whisper_model.transcribe(
# # # #             wav_path,
# # # #             language=self.language,
# # # #             beam_size=WHISPER_BEAM_SIZE,
# # # #         )
# # # #         logger.debug(
# # # #             "Whisper: langue=%s (%.0f%%)",
# # # #             info.language, info.language_probability * 100,
# # # #         )
# # # #         text = " ".join(seg.text.strip() for seg in segments_gen).strip()
# # # #         if not text:
# # # #             raise RuntimeError("Whisper n'a produit aucun texte")
# # # #         logger.info("STT: '%s'", text[:100])
# # # #         return text

# # # #     def _transcribe_google(self, audio) -> str:
# # # #         import speech_recognition as sr
# # # #         lang = "fr-FR" if self.language == "fr" else self.language + "-" + self.language.upper()
# # # #         try:
# # # #             text = self._recognizer.recognize_google(audio, language=lang)
# # # #             logger.info("Google STT: '%s'", text[:100])
# # # #             return text
# # # #         except sr.UnknownValueError:
# # # #             raise RuntimeError("Google STT: audio incomprehensible")
# # # #         except sr.RequestError as exc:
# # # #             raise RuntimeError("Google STT: erreur API: %s" % exc)

# # # #     # ------------------------------------------------------------------
# # # #     # Nettoyage
# # # #     # ------------------------------------------------------------------

# # # #     def close(self) -> None:
# # # #         if self._tts_engine is not None:
# # # #             try:
# # # #                 with self._lock_tts:
# # # #                     self._tts_engine.stop()
# # # #             except Exception:
# # # #                 pass
# # # #         logger.info("VoiceIO ferme")


# # # # # ============================================================================
# # # # # ask_voice() -- interaction de haut niveau
# # # # # ============================================================================

# # # # def ask_voice(
# # # #     io:           VoiceIO,
# # # #     question:     str,
# # # #     *,
# # # #     max_attempts: int  = STT_MAX_ATTEMPTS,
# # # #     is_prompt:    bool = False,
# # # #     allow_skip:   bool = True,
# # # # ) -> InputResult:
# # # #     """Pose *question* vocalement avec 3 tentatives STT, fallback clavier garanti.

# # # #     Sequence par tentative
# # # #     ----------------------
# # # #     1. TTS bloquant (micro ferme).
# # # #     2. Ouverture micro (VAD -- pas de duree fixe).
# # # #     3. Transcription faster-whisper.
# # # #     4. OK -> retourne InputResult(source='stt').
# # # #     5. KO -> message d'erreur vocal + tentative suivante.
# # # #     Apres max_attempts -> clavier -> retourne InputResult(source='keyboard').

# # # #     Args:
# # # #         io:           Instance VoiceIO.
# # # #         question:     Texte de la question.
# # # #         max_attempts: Tentatives STT avant fallback (defaut 3).
# # # #         is_prompt:    True pour prompt long (silence etendu, limite 120s).
# # # #         allow_skip:   Si True, ENTREE vide -> InputResult(source='skipped').
# # # #     """
# # # #     pause = STT_PROMPT_SILENCE    if is_prompt else STT_SILENCE_TIMEOUT
# # # #     limit = STT_PROMPT_TIME_LIMIT if is_prompt else STT_PHRASE_TIME_LIMIT

# # # #     error_messages = [
# # # #         "Je n'ai pas compris. Parlez clairement apres le signal.",
# # # #         "Toujours pas compris. Reformulez en articulant bien.",
# # # #         "Troisieme tentative. Parlez lentement et distinctement.",
# # # #     ]

# # # #     for attempt in range(1, max_attempts + 1):

# # # #         # -- 1. TTS bloquant -- micro ferme --------------------------------
# # # #         io.speak(question)
# # # #         if attempt > 1:
# # # #             io.speak("Tentative %d sur %d. Je vous ecoute." % (attempt, max_attempts))
# # # #         else:
# # # #             io.speak("Je vous ecoute.")

# # # #         mode = "prompt" if is_prompt else "reponse"
# # # #         print("[Ecoute %s] tentative %d/%d..." % (mode, attempt, max_attempts))

# # # #         # -- 2. Capture + transcription ------------------------------------
# # # #         try:
# # # #             text = io.listen(
# # # #                 pause_threshold   = pause,
# # # #                 phrase_time_limit = limit,
# # # #                 listen_timeout    = STT_LISTEN_TIMEOUT,
# # # #             )
# # # #             print("Reconnu : " + text)
# # # #             return InputResult(text=text, source="stt", attempts=attempt)

# # # #         except RuntimeError as exc:
# # # #             logger.warning("STT echec %d/%d: %s", attempt, max_attempts, exc)
# # # #             if attempt < max_attempts:
# # # #                 io.speak(error_messages[attempt - 1])

# # # #     # -- 3. Fallback clavier -------------------------------------------
# # # #     io.speak(
# # # #         "La reconnaissance vocale a echoue %d fois. "
# # # #         "Veuillez utiliser le clavier." % max_attempts
# # # #     )
# # # #     print("\n" + "-" * 60)
# # # #     print("Question : " + question)
# # # #     print("-" * 60)

# # # #     try:
# # # #         text = input(KEYBOARD_PROMPT).strip()
# # # #     except (EOFError, KeyboardInterrupt):
# # # #         text = ""

# # # #     if not text and allow_skip:
# # # #         return InputResult(text="", source="skipped", attempts=max_attempts)

# # # #     return InputResult(text=text, source="keyboard", attempts=max_attempts)


# # # # # ============================================================================
# # # # # VRScenarioApp
# # # # # ============================================================================

# # # # class VRScenarioApp:
# # # #     """Orchestration : generation + discussion de scenario VR."""

# # # #     def __init__(self, io: VoiceIO) -> None:
# # # #         self.io = io

# # # #     def run(self) -> None:
# # # #         self._welcome()
# # # #         topic    = self._ask_topic()
# # # #         config   = self._setup_llm()
# # # #         scenario = self._generate_scenario(topic, config)
# # # #         self._discuss(scenario, topic, config)
# # # #         self._goodbye()

# # # #     # ------------------------------------------------------------------
# # # #     # Etapes
# # # #     # ------------------------------------------------------------------

# # # #     def _welcome(self) -> None:
# # # #         print("\n" + "=" * 60)
# # # #         print("  APPLICATION VOCALE -- SCENARIOS VR")
# # # #         print("=" * 60)
# # # #         self.io.speak(
# # # #             "Bienvenue dans l'application vocale de generation de scenarios VR. "
# # # #             "Vous pouvez me parler naturellement. "
# # # #             "Dites stop ou fin pour quitter a tout moment."
# # # #         )

# # # #     def _ask_topic(self) -> str:
# # # #         result = ask_voice(
# # # #             self.io,
# # # #             "Quel est le theme du scenario VR que vous souhaitez generer ? "
# # # #             "Par exemple : consignation gaz, securite incendie, premiers secours.",
# # # #         )
# # # #         if result.is_exit():
# # # #             self._goodbye()
# # # #             sys.exit(0)
# # # #         topic = result.text or "securite"
# # # #         if result.source == "skipped":
# # # #             self.io.speak("Theme par defaut : securite.")
# # # #         logger.info("Theme : '%s' (source=%s)", topic, result.source)
# # # #         print("\nTheme : " + topic)
# # # #         return topic

# # # #     def _setup_llm(self):
# # # #         try:
# # # #             from vr_scenario_lib.config import build_llm_config
# # # #             return build_llm_config()
# # # #         except Exception as exc:
# # # #             logger.warning("LLM config defaut: %s", exc)
# # # #             try:
# # # #                 from vr_scenario_lib.config import build_llm_config
# # # #                 return build_llm_config(
# # # #                     token="dummy",
# # # #                     api_url="https://openrouter.ai/api/v1/chat/completions",
# # # #                     model="openai/gpt-3.5-turbo",
# # # #                 )
# # # #             except Exception:
# # # #                 return None

# # # #     def _generate_scenario(self, topic: str, config) -> str:
# # # #         self.io.speak("Generation du scenario sur le theme : " + topic + ".")

# # # #         result = ask_voice(
# # # #             self.io,
# # # #             "Voulez-vous ajouter des consignes supplementaires ? "
# # # #             "Parlez maintenant ou attendez pour continuer sans.",
# # # #             is_prompt=True,
# # # #             allow_skip=True,
# # # #         )
# # # #         extra = result.text if result else ""

# # # #         print("\nGeneration en cours...")
# # # #         self.io.speak("Patientez pendant la generation du scenario.")

# # # #         docs     = self._sample_docs(topic)
# # # #         scenario = self._build_scenario_text(topic, docs, extra)

# # # #         self.io.speak("Scenario genere avec succes.")
# # # #         logger.info("Scenario genere (%d caracteres)", len(scenario))
# # # #         return scenario

# # # #     def _discuss(self, scenario: str, topic: str, config) -> None:
# # # #         self.io.speak(
# # # #             "Nous allons maintenant discuter du scenario. "
# # # #             "Repondez a mes questions ou posez les votres. "
# # # #             "Dites fin pour terminer."
# # # #         )

# # # #         session = None
# # # #         try:
# # # #             from vr_scenario_lib.scenario_store import ScenarioSession
# # # #             session = ScenarioSession(scenario)
# # # #         except Exception as exc:
# # # #             logger.error("ScenarioSession impossible: %s", exc)

# # # #         # Questions guidees
# # # #         for question in [
# # # #             "Quels sont les principes de base du " + topic + " ?",
# # # #             "Quelles sont les procedures de securite essentielles en " + topic + " ?",
# # # #             "Comment reagir en cas d'urgence liee a " + topic + " ?",
# # # #         ]:
# # # #             result = ask_voice(self.io, question)
# # # #             if not result or result.is_exit():
# # # #                 break
# # # #             if session and config:
# # # #                 self._llm_reply(result.text, session, config)

# # # #         # Questions libres
# # # #         self.io.speak("Posez toutes vos questions. Dites fin pour terminer.")
# # # #         while True:
# # # #             result = ask_voice(self.io, "Quelle est votre question ?")
# # # #             if not result or result.is_exit():
# # # #                 break
# # # #             if result.source == "skipped":
# # # #                 self.io.speak("Pas de question.")
# # # #                 continue
# # # #             if session and config:
# # # #                 self._llm_reply(result.text, session, config)

# # # #     def _llm_reply(self, user_message: str, session, config) -> None:
# # # #         self.io.speak("Je reflechis.")
# # # #         try:
# # # #             from vr_scenario_lib.scenario import discuss_scenario as llm_discuss
# # # #             reply = llm_discuss(
# # # #                 session=session,
# # # #                 user_message=user_message,
# # # #                 llm_config=config,
# # # #             )
# # # #             print("\nReponse : " + reply + "\n")
# # # #             self.io.speak(reply)
# # # #         except Exception as exc:
# # # #             logger.error("LLM erreur: %s", exc)
# # # #             self.io.speak("Desole, une erreur est survenue.")

# # # #     def _goodbye(self) -> None:
# # # #         self.io.speak("Merci d'avoir utilise l'application. Au revoir !")
# # # #         print("\nAu revoir !\n")

# # # #     # ------------------------------------------------------------------
# # # #     # Helpers
# # # #     # ------------------------------------------------------------------

# # # #     @staticmethod
# # # #     def _sample_docs(topic: str) -> list:
# # # #         from langchain_core.documents import Document
# # # #         library = {
# # # #             "gaz": [
# # # #                 "La manipulation des gaz requiert des precautions contre fuites et explosions.",
# # # #                 "Chaque gaz a ses propres proprietes et dangers specifiques.",
# # # #                 "Les EPI adaptes sont indispensables lors de la manipulation des gaz.",
# # # #                 "En cas de fuite, aerer immediatement et evacuer la zone.",
# # # #             ],
# # # #             "securite incendie": [
# # # #                 "La securite incendie comprend la prevention, la detection et l'evacuation.",
# # # #                 "Les extincteurs doivent etre verifies mensuellement.",
# # # #                 "Les exercices d'evacuation ont lieu au moins une fois par an.",
# # # #             ],
# # # #             "premiers secours": [
# # # #                 "Evaluez la scene avant d'intervenir.",
# # # #                 "Appelez les secours en cas de blessure grave.",
# # # #                 "Ordre de priorite : Danger, Reponse, Respiration, Circulation.",
# # # #             ],
# # # #         }
# # # #         docs = library.get(topic.lower(), [
# # # #             "Informations generales sur le theme selectionne.",
# # # #         ])
# # # #         return [
# # # #             Document(page_content=d, metadata={"source": topic + "_" + str(i)})
# # # #             for i, d in enumerate(docs)
# # # #         ]

# # # #     @staticmethod
# # # #     def _build_scenario_text(topic: str, docs: list, extra: str) -> str:
# # # #         body = " ".join(d.page_content for d in docs)
# # # #         return (
# # # #             "# SCENARIO VR -- " + topic.upper() + "\n\n"
# # # #             "## Contexte\n" + body + "\n\n"
# # # #             "## Consignes personnalisees\n"
# # # #             + (extra if extra else "Aucune consigne supplementaire.") + "\n\n"
# # # #             "## Objectifs\n"
# # # #             "- Comprendre les principes fondamentaux\n"
# # # #             "- Maitriser les procedures de base\n"
# # # #             "- Reagir correctement aux situations d'urgence\n"
# # # #         )


# # # # # ============================================================================
# # # # # CLI
# # # # # ============================================================================

# # # # def _parse_args() -> argparse.Namespace:
# # # #     p = argparse.ArgumentParser(
# # # #         description="Application vocale scenarios VR",
# # # #         formatter_class=argparse.ArgumentDefaultsHelpFormatter,
# # # #     )
# # # #     p.add_argument("--stt-backend",   default="whisper",
# # # #                    choices=["whisper", "google"])
# # # #     p.add_argument("--tts-backend",   default="pyttsx3",
# # # #                    choices=["pyttsx3", "gtts"])
# # # #     p.add_argument("--language",      default="fr")
# # # #     p.add_argument("--whisper-model", default=WHISPER_DEFAULT_MODEL,
# # # #                    choices=["tiny", "base", "small", "medium", "large"])
# # # #     p.add_argument("--debug",         action="store_true")
# # # #     return p.parse_args()


# # # # def main() -> None:
# # # #     args = _parse_args()
# # # #     if args.debug:
# # # #         logging.getLogger().setLevel(logging.DEBUG)

# # # #     io = VoiceIO(
# # # #         stt_backend   = args.stt_backend,
# # # #         tts_backend   = args.tts_backend,
# # # #         language      = args.language,
# # # #         whisper_model = args.whisper_model,
# # # #     )
# # # #     app = VRScenarioApp(io)
# # # #     try:
# # # #         app.run()
# # # #     except KeyboardInterrupt:
# # # #         print("\nInterruption utilisateur.")
# # # #     finally:
# # # #         io.close()


# # # # if __name__ == "__main__":
# # # #     main()
# # # #!/usr/bin/env python3
# # # """
# # # Application vocale de supervision de scenarios VR.
# # # Version enterprise -- standards industriels.

# # # ROLE DE L'APP
# # # -------------
# # # L'utilisateur decrit librement un scenario VR a voix haute.
# # # L'application ecoute en continu, transcrit par chunks VAD, et
# # # soumet chaque chunk a un LLM superviseur qui peut :
# # #   - CONTINUER  : ne rien dire (ecoute silencieuse)
# # #   - CONSEIL    : interrompre poliment pour donner un conseil
# # #   - STOP       : interrompre fermement pour signaler une erreur critique

# # # Architecture
# # # ------------
# # # VoiceIO          : STT (faster-whisper + SpeechRecognition VAD) + TTS francais natif.
# # # SupervisorLLM    : analyse chaque chunk, decide CONTINUER / CONSEIL / STOP.
# # # NarratorSession  : accumule la transcription, maintient le contexte du scenario.
# # # VRScenarioApp    : orchestration metier (setup + boucle de narration supervisee).

# # # Backends TTS francais natifs (ordre de priorite automatique)
# # # ------------------------------------------------------------
# # # 1. coqui   -- Coqui VITS tts_models/fr/css10/vits  : voix neurale offline, haute qualite
# # # 2. piper   -- Piper fr_FR-upmc-medium               : voix neurale offline, ultra-rapide
# # # 3. gtts    -- Google TTS                            : voix cloud, qualite maximale
# # # 4. pyttsx3 -- espeak-fr                             : synthese basique, zero dependance

# # # Usage:
# # #     python app_vocal.py                            # auto-detection meilleur TTS dispo
# # #     python app_vocal.py --tts-backend coqui        # Coqui VITS (offline, haute qualite)
# # #     python app_vocal.py --tts-backend piper        # Piper (offline, ultra-rapide)
# # #     python app_vocal.py --tts-backend gtts         # Google TTS (cloud)
# # #     python app_vocal.py --stt-backend google       # Google STT (cloud)
# # #     python app_vocal.py --whisper-model small      # meilleure precision STT
# # #     python app_vocal.py --debug                    # logs DEBUG complets
# # # """

# # # from __future__ import annotations

# # # import argparse
# # # import logging
# # # import os
# # # import sys
# # # import tempfile
# # # import threading
# # # import time
# # # from dataclasses import dataclass, field
# # # from enum import Enum
# # # from typing import List, Optional

# # # # ---------------------------------------------------------------------------
# # # # Logging
# # # # ---------------------------------------------------------------------------
# # # logging.basicConfig(
# # #     level=logging.INFO,
# # #     format="%(asctime)s | %(name)-36s | %(levelname)-8s | %(message)s",
# # #     datefmt="%H:%M:%S",
# # # )
# # # logger = logging.getLogger(__name__)

# # # sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# # # # ============================================================================
# # # # Constantes
# # # # ============================================================================

# # # STT_LISTEN_TIMEOUT    = 8
# # # STT_PHRASE_TIME_LIMIT = 20          # duree max d'un chunk narration
# # # STT_SILENCE_TIMEOUT   = 2.0         # silence VAD -> fin du chunk
# # # STT_AMBIENT_DURATION  = 0.5
# # # TTS_SPEECH_RATE       = 145
# # # TTS_VOLUME            = 0.92
# # # WHISPER_DEFAULT_MODEL = "base"
# # # WHISPER_BEAM_SIZE     = 5
# # # EXIT_WORDS            = {"quitter", "exit", "quit", "au revoir", "stop", "fin"}

# # # # Backends TTS francais natifs
# # # TTS_DEFAULT_BACKEND   = "coqui"
# # # TTS_FALLBACK_CHAIN    = ["coqui", "piper", "gtts", "pyttsx3"]

# # # # Coqui TTS
# # # COQUI_MODEL_FR        = "tts_models/fr/css10/vits"
# # # COQUI_SAMPLE_RATE     = 22050

# # # # Piper TTS
# # # PIPER_MODEL_FR        = "fr_FR-upmc-medium"
# # # PIPER_SAMPLE_RATE     = 22050

# # # # Supervisor LLM
# # # SUPERVISOR_MAX_TOKENS = 256
# # # SUPERVISOR_SYSTEM = (
# # #     "Tu es un superviseur expert en securite VR et en procedures industrielles. "
# # #     "L'utilisateur decrit a voix haute un scenario de formation VR. "
# # #     "Tu recois des fragments de sa narration en temps reel.\n\n"
# # #     "Analyse le dernier fragment dans son contexte et reponds UNIQUEMENT avec un objet JSON :\n"
# # #     '{"decision": "CONTINUER" | "CONSEIL" | "STOP", "message": "<texte a dire, vide si CONTINUER>"}\n\n'
# # #     "Regles strictes :\n"
# # #     "- CONTINUER  : narration correcte, coherente, sans danger. Message vide obligatoire.\n"
# # #     "- CONSEIL    : amelioration possible. Message court, positif, actionnable. Max 2 phrases.\n"
# # #     "- STOP       : erreur critique de procedure, danger reel, incoherence grave. "
# # #     "Message direct et precis. Commence par 'Attention : '.\n"
# # #     "Ne jamais inventer de contexte non mentionne. Rester factuel."
# # # )


# # # # ============================================================================
# # # # Decision + NarratorSession
# # # # ============================================================================

# # # class Decision(Enum):
# # #     CONTINUER = "CONTINUER"
# # #     CONSEIL   = "CONSEIL"
# # #     STOP      = "STOP"


# # # @dataclass
# # # class SupervisorDecision:
# # #     decision: Decision = Decision.CONTINUER
# # #     message:  str      = ""

# # #     def must_speak(self) -> bool:
# # #         return self.decision in (Decision.CONSEIL, Decision.STOP)


# # # @dataclass
# # # class NarratorSession:
# # #     """Accumule la transcription et maintient le contexte pour le LLM."""
# # #     topic:     str
# # #     chunks:    List[str] = field(default_factory=list)
# # #     full_text: str       = ""

# # #     def add_chunk(self, text: str) -> None:
# # #         self.chunks.append(text)
# # #         self.full_text = " ".join(self.chunks)

# # #     def context_window(self, n: int = 5) -> str:
# # #         return " ".join(self.chunks[-n:])

# # #     def summary(self) -> str:
# # #         return "%d sequence(s), ~%d mots" % (len(self.chunks), len(self.full_text.split()))


# # # # ============================================================================
# # # # SupervisorLLM
# # # # ============================================================================

# # # class SupervisorLLM:
# # #     """Analyse les chunks de narration et produit des decisions superviseur."""

# # #     def __init__(self, config) -> None:
# # #         self._config = config
# # #         self._lock   = threading.Lock()

# # #     def analyse(self, session: NarratorSession, new_chunk: str) -> SupervisorDecision:
# # #         if self._config is None:
# # #             return SupervisorDecision()

# # #         user_msg = (
# # #             "Theme du scenario : %s\n\n"
# # #             "Contexte (narration precedente) :\n%s\n\n"
# # #             "Nouveau fragment :\n%s"
# # #         ) % (session.topic, session.context_window(), new_chunk)

# # #         try:
# # #             with self._lock:
# # #                 raw = self._call_llm(user_msg)
# # #             return self._parse(raw)
# # #         except Exception as exc:
# # #             logger.warning("SupervisorLLM erreur: %s", exc)
# # #             return SupervisorDecision()

# # #     def _call_llm(self, user_msg: str) -> str:
# # #         # Tentative via vr_scenario_lib
# # #         try:
# # #             from vr_scenario_lib.llm import call_llm
# # #             return call_llm(
# # #                 system=SUPERVISOR_SYSTEM,
# # #                 user=user_msg,
# # #                 llm_config=self._config,
# # #                 max_tokens=SUPERVISOR_MAX_TOKENS,
# # #             )
# # #         except ImportError:
# # #             pass

# # #         # Fallback HTTP direct (OpenAI-compatible)
# # #         import json
# # #         import urllib.request

# # #         payload = json.dumps({
# # #             "model":      getattr(self._config, "model", "gpt-3.5-turbo"),
# # #             "max_tokens": SUPERVISOR_MAX_TOKENS,
# # #             "messages":   [
# # #                 {"role": "system", "content": SUPERVISOR_SYSTEM},
# # #                 {"role": "user",   "content": user_msg},
# # #             ],
# # #         }).encode()
# # #         api_url = getattr(self._config, "api_url", "https://api.openai.com/v1/chat/completions")
# # #         token   = getattr(self._config, "token", "")
# # #         req = urllib.request.Request(
# # #             api_url,
# # #             data=payload,
# # #             headers={
# # #                 "Content-Type":  "application/json",
# # #                 "Authorization": "Bearer " + token,
# # #             },
# # #         )
# # #         with urllib.request.urlopen(req, timeout=15) as resp:
# # #             data = json.loads(resp.read())
# # #         return data["choices"][0]["message"]["content"]

# # #     def _parse(self, raw: str) -> SupervisorDecision:
# # #         import json
# # #         import re
# # #         m = re.search(r'\{.*\}', raw, re.DOTALL)
# # #         if not m:
# # #             logger.warning("SupervisorLLM: JSON introuvable dans '%s'", raw[:120])
# # #             return SupervisorDecision()
# # #         obj = json.loads(m.group())
# # #         try:
# # #             dec = Decision(obj.get("decision", "CONTINUER").upper())
# # #         except ValueError:
# # #             dec = Decision.CONTINUER
# # #         return SupervisorDecision(decision=dec, message=obj.get("message", "").strip())


# # # # ============================================================================
# # # # VoiceIO
# # # # ============================================================================

# # # class VoiceIO:
# # #     """Couche bas-niveau STT + TTS.

# # #     Regles fondamentales
# # #     --------------------
# # #     1. speak() est TOUJOURS bloquant dans le flux principal.
# # #        Un TTS non-bloquant avant listen() = echo capture par Whisper.
# # #     2. Le micro n'est jamais ouvert pendant la synthese vocale.
# # #     3. L'enregistrement utilise la VAD (SpeechRecognition), pas une duree fixe.
# # #     4. interrupt_and_speak() coupe l'audio en cours avant de parler (STOP urgents).
# # #     """

# # #     def __init__(
# # #         self,
# # #         stt_backend:   str = "whisper",
# # #         tts_backend:   str = TTS_DEFAULT_BACKEND,
# # #         language:      str = "fr",
# # #         whisper_model: str = WHISPER_DEFAULT_MODEL,
# # #         coqui_model:   str = COQUI_MODEL_FR,
# # #         piper_model:   str = PIPER_MODEL_FR,
# # #     ) -> None:
# # #         self.stt_backend      = stt_backend
# # #         self.tts_backend      = tts_backend
# # #         self.language         = language
# # #         self.whisper_model_id = whisper_model
# # #         self.coqui_model_id   = coqui_model
# # #         self.piper_model_id   = piper_model

# # #         self._recognizer    = None
# # #         self._whisper_model = None
# # #         self._tts_engine    = None
# # #         self._coqui_model   = None
# # #         self._lock_tts      = threading.Lock()

# # #         self._init()

# # #     # ------------------------------------------------------------------
# # #     # Init
# # #     # ------------------------------------------------------------------

# # #     def _init(self) -> None:
# # #         self._init_stt()
# # #         self._init_tts()
# # #         logger.info(
# # #             "VoiceIO pret -- STT: %s | TTS: %s | Langue: %s",
# # #             self.stt_backend, self.tts_backend, self.language,
# # #         )

# # #     def _init_stt(self) -> None:
# # #         try:
# # #             import speech_recognition as sr
# # #             self._recognizer = sr.Recognizer()
# # #             self._recognizer.energy_threshold         = 4000
# # #             self._recognizer.pause_threshold          = STT_SILENCE_TIMEOUT
# # #             self._recognizer.dynamic_energy_threshold = True
# # #         except ImportError:
# # #             raise RuntimeError(
# # #                 "SpeechRecognition manquant. pip install SpeechRecognition PyAudio"
# # #             )
# # #         if self.stt_backend == "whisper":
# # #             self._whisper_model = self._load_whisper()

# # #     def _load_whisper(self) -> object:
# # #         try:
# # #             from faster_whisper import WhisperModel
# # #             logger.info("Chargement faster-whisper '%s'...", self.whisper_model_id)
# # #             model = WhisperModel(
# # #                 self.whisper_model_id,
# # #                 device="cpu",
# # #                 compute_type="int8",
# # #             )
# # #             logger.info("faster-whisper pret")
# # #             return model
# # #         except ImportError:
# # #             raise RuntimeError("faster-whisper manquant. pip install faster-whisper")

# # #     def _init_tts(self) -> None:
# # #         chain = (
# # #             [self.tts_backend]
# # #             + [b for b in TTS_FALLBACK_CHAIN if b != self.tts_backend]
# # #         )
# # #         for backend in chain:
# # #             try:
# # #                 if backend == "coqui":
# # #                     self._init_coqui()
# # #                 elif backend == "piper":
# # #                     self._init_piper()
# # #                 elif backend == "gtts":
# # #                     self._init_gtts()
# # #                 elif backend == "pyttsx3":
# # #                     self._init_pyttsx3()
# # #                 else:
# # #                     continue
# # #                 self.tts_backend = backend
# # #                 logger.info("TTS backend actif : %s", backend)
# # #                 return
# # #             except Exception as exc:
# # #                 logger.warning(
# # #                     "TTS backend '%s' indisponible: %s -- essai suivant", backend, exc
# # #                 )

# # #         raise RuntimeError(
# # #             "Aucun backend TTS disponible. "
# # #             "Installez au moins : pip install coqui-tts sounddevice soundfile"
# # #         )

# # #     # ------------------------------------------------------------------
# # #     # Init Coqui VITS -- voix neurale francaise offline
# # #     # ------------------------------------------------------------------

# # #     def _init_coqui(self) -> None:
# # #         try:
# # #             from TTS.api import TTS as CoquiTTS
# # #             import sounddevice  # noqa: F401
# # #             import soundfile    # noqa: F401
# # #         except ImportError:
# # #             raise RuntimeError(
# # #                 "Coqui TTS manquant. pip install coqui-tts sounddevice soundfile"
# # #             )
# # #         logger.info("Chargement Coqui TTS '%s'...", self.coqui_model_id)
# # #         self._coqui_model = CoquiTTS(
# # #             model_name=self.coqui_model_id,
# # #             progress_bar=False,
# # #             gpu=False,
# # #         )
# # #         logger.info("Coqui TTS pret (fr/css10/vits)")

# # #     # ------------------------------------------------------------------
# # #     # Init Piper -- voix neurale francaise offline, ultra-rapide
# # #     # ------------------------------------------------------------------

# # #     def _init_piper(self) -> None:
# # #         try:
# # #             import piper  # noqa: F401
# # #         except ImportError:
# # #             raise RuntimeError("piper-tts manquant. pip install piper-tts")
# # #         logger.info("Piper TTS disponible -- modele '%s'", self.piper_model_id)

# # #     # ------------------------------------------------------------------
# # #     # Init gTTS -- Google TTS cloud
# # #     # ------------------------------------------------------------------

# # #     def _init_gtts(self) -> None:
# # #         try:
# # #             import gtts    # noqa: F401
# # #             import pygame  # noqa: F401
# # #         except ImportError:
# # #             raise RuntimeError("gTTS/pygame manquants. pip install gTTS pygame")
# # #         logger.info("gTTS cloud initialise")

# # #     # ------------------------------------------------------------------
# # #     # Init pyttsx3 -- fallback ultime espeak
# # #     # ------------------------------------------------------------------

# # #     def _init_pyttsx3(self) -> None:
# # #         try:
# # #             import pyttsx3
# # #         except ImportError:
# # #             raise RuntimeError("pyttsx3 manquant. pip install pyttsx3")

# # #         engine = pyttsx3.init()
# # #         engine.setProperty("rate",   TTS_SPEECH_RATE)
# # #         engine.setProperty("volume", TTS_VOLUME)

# # #         fr_voice_found = False
# # #         for v in engine.getProperty("voices"):
# # #             if "french" in v.name.lower() or "fr" in v.id.lower():
# # #                 engine.setProperty("voice", v.id)
# # #                 logger.info("pyttsx3 voix francaise : %s", v.name)
# # #                 fr_voice_found = True
# # #                 break

# # #         if not fr_voice_found:
# # #             logger.warning(
# # #                 "Aucune voix francaise trouvee dans pyttsx3. "
# # #                 "Linux: sudo apt install espeak-ng-data"
# # #             )

# # #         self._tts_engine = engine
# # #         logger.info("pyttsx3 initialise (voix systeme)")

# # #     # ------------------------------------------------------------------
# # #     # TTS -- TOUJOURS bloquant dans le flux principal
# # #     # ------------------------------------------------------------------

# # #     def interrupt_and_speak(self, text: str) -> None:
# # #         """Coupe l'audio en cours PUIS parle. Reserve aux STOP urgents."""
# # #         self._stop_audio()
# # #         self.speak(text)

# # #     def _stop_audio(self) -> None:
# # #         """Arrete immediatement la lecture audio (tous backends)."""
# # #         try:
# # #             if self.tts_backend in ("coqui", "piper"):
# # #                 import sounddevice as sd
# # #                 sd.stop()
# # #             elif self.tts_backend == "gtts":
# # #                 try:
# # #                     import pygame
# # #                     if pygame.mixer.get_init():
# # #                         pygame.mixer.music.stop()
# # #                 except Exception:
# # #                     pass
# # #         except Exception as exc:
# # #             logger.debug("_stop_audio: %s", exc)

# # #     def speak(self, text: str, *, blocking: bool = True) -> None:
# # #         """Synthese vocale en francais natif.

# # #         blocking=True (defaut) : retourne APRES la fin de la lecture.
# # #         blocking=False         : usage exceptionnel uniquement.
# # #         REGLE : ne JAMAIS appeler avec blocking=False avant listen().
# # #         """
# # #         if not text or not text.strip():
# # #             return
# # #         logger.info("TTS [%s]: '%s'", self.tts_backend, text[:80])

# # #         dispatch = {
# # #             "coqui":   self._speak_coqui,
# # #             "piper":   self._speak_piper,
# # #             "gtts":    self._speak_gtts,
# # #             "pyttsx3": self._speak_pyttsx3,
# # #         }
# # #         fn = dispatch.get(self.tts_backend)
# # #         if fn is None:
# # #             logger.error("Backend TTS inconnu: %s", self.tts_backend)
# # #             print("[TTS] " + text)
# # #             return
# # #         fn(text, blocking)

# # #     # ------------------------------------------------------------------
# # #     # _speak_coqui : Coqui VITS fr/css10 -- reference qualite
# # #     # ------------------------------------------------------------------

# # #     def _speak_coqui(self, text: str, blocking: bool) -> None:
# # #         tmp_path: Optional[str] = None
# # #         try:
# # #             import soundfile as sf
# # #             import sounddevice as sd

# # #             with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
# # #                 tmp_path = f.name

# # #             with self._lock_tts:
# # #                 self._coqui_model.tts_to_file(text=text, file_path=tmp_path)

# # #             data, sr = sf.read(tmp_path, dtype="float32")
# # #             if blocking:
# # #                 sd.play(data, sr)
# # #                 sd.wait()
# # #             else:
# # #                 sd.play(data, sr)

# # #         except Exception as exc:
# # #             logger.error("Coqui TTS erreur: %s", exc)
# # #             print("[TTS] " + text)
# # #         finally:
# # #             if tmp_path and os.path.exists(tmp_path):
# # #                 try:
# # #                     os.unlink(tmp_path)
# # #                 except OSError:
# # #                     pass

# # #     # ------------------------------------------------------------------
# # #     # _speak_piper : Piper fr_FR-upmc -- latence minimale
# # #     # ------------------------------------------------------------------

# # #     def _speak_piper(self, text: str, blocking: bool) -> None:
# # #         tmp_path: Optional[str] = None
# # #         try:
# # #             import subprocess
# # #             import soundfile as sf
# # #             import sounddevice as sd

# # #             with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
# # #                 tmp_path = f.name

# # #             result = subprocess.run(
# # #                 ["piper", "--model", self.piper_model_id, "--output_file", tmp_path],
# # #                 input=text.encode("utf-8"),
# # #                 capture_output=True,
# # #                 timeout=30,
# # #             )
# # #             if result.returncode != 0:
# # #                 raise RuntimeError(
# # #                     "piper returncode=%d: %s" % (result.returncode, result.stderr.decode())
# # #                 )

# # #             data, sr = sf.read(tmp_path, dtype="float32")
# # #             if blocking:
# # #                 sd.play(data, sr)
# # #                 sd.wait()
# # #             else:
# # #                 sd.play(data, sr)

# # #         except FileNotFoundError:
# # #             logger.error("Executable 'piper' introuvable. pip install piper-tts")
# # #             print("[TTS] " + text)
# # #         except Exception as exc:
# # #             logger.error("Piper TTS erreur: %s", exc)
# # #             print("[TTS] " + text)
# # #         finally:
# # #             if tmp_path and os.path.exists(tmp_path):
# # #                 try:
# # #                     os.unlink(tmp_path)
# # #                 except OSError:
# # #                     pass

# # #     # ------------------------------------------------------------------
# # #     # _speak_gtts : Google TTS cloud
# # #     # Bug corrige : mixer reinitialise a chaque appel (non-reentrant).
# # #     # ------------------------------------------------------------------

# # #     def _speak_gtts(self, text: str, blocking: bool) -> None:
# # #         tmp_path: Optional[str] = None
# # #         try:
# # #             from gtts import gTTS
# # #             import pygame

# # #             tts = gTTS(text=text, lang=self.language, slow=False)
# # #             with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
# # #                 tmp_path = f.name
# # #             tts.save(tmp_path)

# # #             # Reinitialisation propre du mixer a chaque appel
# # #             if pygame.mixer.get_init():
# # #                 pygame.mixer.quit()
# # #             pygame.mixer.init(frequency=22050, size=-16, channels=1, buffer=512)
# # #             pygame.mixer.music.load(tmp_path)
# # #             pygame.mixer.music.play()

# # #             if blocking:
# # #                 while pygame.mixer.music.get_busy():
# # #                     time.sleep(0.05)
# # #                 pygame.mixer.quit()

# # #         except Exception as exc:
# # #             logger.error("gTTS erreur: %s", exc)
# # #             print("[TTS] " + text)
# # #         finally:
# # #             if tmp_path and os.path.exists(tmp_path):
# # #                 try:
# # #                     time.sleep(0.1)   # libere le handle fichier
# # #                     os.unlink(tmp_path)
# # #                 except OSError:
# # #                     pass

# # #     # ------------------------------------------------------------------
# # #     # _speak_pyttsx3 : espeak fallback ultime
# # #     # ------------------------------------------------------------------

# # #     def _speak_pyttsx3(self, text: str, blocking: bool) -> None:
# # #         with self._lock_tts:
# # #             try:
# # #                 self._tts_engine.say(text)
# # #                 if blocking:
# # #                     self._tts_engine.runAndWait()
# # #                 else:
# # #                     # NOTE : non-bloquant uniquement si explicitement demande.
# # #                     # Ne jamais appeler avant listen() -- race condition micro.
# # #                     t = threading.Thread(
# # #                         target=self._tts_engine.runAndWait, daemon=True
# # #                     )
# # #                     t.start()
# # #             except Exception as exc:
# # #                 logger.error("pyttsx3 erreur: %s", exc)
# # #                 print("[TTS] " + text)

# # #     # ------------------------------------------------------------------
# # #     # STT -- chunk VAD (narration continue)
# # #     # ------------------------------------------------------------------

# # #     def listen_chunk(
# # #         self,
# # #         *,
# # #         pause_threshold:   float = STT_SILENCE_TIMEOUT,
# # #         phrase_time_limit: int   = STT_PHRASE_TIME_LIMIT,
# # #         listen_timeout:    float = STT_LISTEN_TIMEOUT,
# # #     ) -> str:
# # #         """Capture un chunk de parole (VAD) et transcrit.

# # #         Returns:
# # #             Texte transcrit non-vide.

# # #         Raises:
# # #             RuntimeError: Capture ou transcription impossible.
# # #         """
# # #         import speech_recognition as sr

# # #         original = self._recognizer.pause_threshold
# # #         self._recognizer.pause_threshold = pause_threshold
# # #         tmp_path: Optional[str] = None

# # #         try:
# # #             with sr.Microphone() as src:
# # #                 logger.info(
# # #                     "Ecoute chunk (silence=%.1fs, max=%ds)...",
# # #                     pause_threshold, phrase_time_limit,
# # #                 )
# # #                 self._recognizer.adjust_for_ambient_noise(src, duration=STT_AMBIENT_DURATION)
# # #                 audio = self._recognizer.listen(
# # #                     src,
# # #                     timeout=listen_timeout,
# # #                     phrase_time_limit=phrase_time_limit,
# # #                 )

# # #             with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
# # #                 tmp_path = f.name
# # #                 f.write(audio.get_wav_data())

# # #             if self.stt_backend == "whisper":
# # #                 return self._transcribe_whisper(tmp_path)
# # #             else:
# # #                 return self._transcribe_google(audio)

# # #         finally:
# # #             self._recognizer.pause_threshold = original
# # #             if tmp_path and os.path.exists(tmp_path):
# # #                 try:
# # #                     os.unlink(tmp_path)
# # #                 except OSError:
# # #                     pass

# # #     def listen_short(self, question: str, timeout: float = 8.0) -> str:
# # #         """Pose une question courte et attend une reponse breve.
# # #         Retourne la chaine vide en cas d'echec (pas de RuntimeError propagee).
# # #         """
# # #         self.speak(question)
# # #         self.speak("Je vous ecoute.")
# # #         try:
# # #             return self.listen_chunk(
# # #                 pause_threshold=1.5,
# # #                 phrase_time_limit=15,
# # #                 listen_timeout=timeout,
# # #             )
# # #         except RuntimeError as exc:
# # #             logger.info("listen_short: pas de reponse (%s)", exc)
# # #             return ""

# # #     def _transcribe_whisper(self, wav_path: str) -> str:
# # #         segments_gen, info = self._whisper_model.transcribe(
# # #             wav_path,
# # #             language=self.language,
# # #             beam_size=WHISPER_BEAM_SIZE,
# # #         )
# # #         logger.debug(
# # #             "Whisper: langue=%s (%.0f%%)",
# # #             info.language, info.language_probability * 100,
# # #         )
# # #         text = " ".join(seg.text.strip() for seg in segments_gen).strip()
# # #         if not text:
# # #             raise RuntimeError("Whisper n'a produit aucun texte")
# # #         logger.info("STT chunk: '%s'", text[:100])
# # #         return text

# # #     def _transcribe_google(self, audio) -> str:
# # #         import speech_recognition as sr
# # #         lang = "fr-FR" if self.language == "fr" else (self.language + "-" + self.language.upper())
# # #         try:
# # #             text = self._recognizer.recognize_google(audio, language=lang)
# # #             logger.info("Google STT: '%s'", text[:100])
# # #             return text
# # #         except sr.UnknownValueError:
# # #             raise RuntimeError("Google STT: audio incomprehensible")
# # #         except sr.RequestError as exc:
# # #             raise RuntimeError("Google STT: erreur API: %s" % exc)

# # #     # ------------------------------------------------------------------
# # #     # Nettoyage
# # #     # ------------------------------------------------------------------

# # #     def close(self) -> None:
# # #         self._stop_audio()
# # #         if self._tts_engine is not None:
# # #             try:
# # #                 with self._lock_tts:
# # #                     self._tts_engine.stop()
# # #             except Exception:
# # #                 pass
# # #         logger.info("VoiceIO ferme")


# # # # ============================================================================
# # # # VRScenarioApp  -- orchestration principale
# # # # ============================================================================

# # # class VRScenarioApp:
# # #     """
# # #     Flux principal :
# # #       1. Accueil + saisie vocale du theme
# # #       2. Boucle de narration supervisee :
# # #          - listen_chunk() -> transcrit un fragment de narration
# # #          - SupervisorLLM.analyse() -> CONTINUER / CONSEIL / STOP
# # #          - CONTINUER : silence, on reecoute
# # #          - CONSEIL   : parle brievement, reprend l'ecoute
# # #          - STOP      : interrupt_and_speak(), pause, reprend ou termine
# # #          - EXIT word : cloture propre
# # #     """

# # #     def __init__(self, io: VoiceIO) -> None:
# # #         self.io = io

# # #     def run(self) -> None:
# # #         self._welcome()
# # #         topic      = self._ask_topic()
# # #         config     = self._setup_llm()
# # #         session    = NarratorSession(topic=topic)
# # #         supervisor = SupervisorLLM(config)
# # #         self._narration_loop(session, supervisor)
# # #         self._goodbye()

# # #     # ------------------------------------------------------------------
# # #     # Etapes
# # #     # ------------------------------------------------------------------

# # #     def _welcome(self) -> None:
# # #         print("\n" + "=" * 60)
# # #         print("  APPLICATION VOCALE -- SUPERVISION DE SCENARIOS VR")
# # #         print("=" * 60)
# # #         self.io.speak(
# # #             "Bienvenue dans l'application de supervision vocale de scenarios VR. "
# # #             "Decrivez votre scenario librement. "
# # #             "J'ecouterai en continu et interviendrai si necessaire. "
# # #             "Dites stop ou fin pour terminer a tout moment."
# # #         )

# # #     def _ask_topic(self) -> str:
# # #         text = self.io.listen_short(
# # #             "Quel est le theme du scenario VR que vous souhaitez decrire ? "
# # #             "Par exemple : consignation gaz, securite incendie, premiers secours."
# # #         )
# # #         if not text:
# # #             text = "securite"
# # #             self.io.speak("Theme par defaut : securite.")
# # #         else:
# # #             self.io.speak("Theme retenu : " + text + ". Vous pouvez commencer votre narration.")
# # #         logger.info("Theme : '%s'", text)
# # #         print("\nTheme : " + text)
# # #         return text

# # #     def _narration_loop(self, session: NarratorSession, supervisor: SupervisorLLM) -> None:
# # #         """Boucle principale de narration supervisee."""
# # #         self.io.speak(
# # #             "Je vous ecoute. Decrivez votre scenario etape par etape. "
# # #             "Je resterai silencieux sauf si je dois intervenir."
# # #         )
# # #         print("\n" + "-" * 60)
# # #         print("[ NARRATION EN COURS -- parlez librement ]")
# # #         print("-" * 60)

# # #         consecutive_timeouts = 0
# # #         MAX_TIMEOUTS = 3

# # #         while True:

# # #             # ---- 1. Capture d'un chunk ------------------------------------
# # #             try:
# # #                 chunk = self.io.listen_chunk(
# # #                     pause_threshold   = STT_SILENCE_TIMEOUT,
# # #                     phrase_time_limit = STT_PHRASE_TIME_LIMIT,
# # #                     listen_timeout    = STT_LISTEN_TIMEOUT,
# # #                 )
# # #                 consecutive_timeouts = 0

# # #             except RuntimeError as exc:
# # #                 consecutive_timeouts += 1
# # #                 logger.info(
# # #                     "Silence/timeout (%d/%d): %s",
# # #                     consecutive_timeouts, MAX_TIMEOUTS, exc,
# # #                 )
# # #                 if consecutive_timeouts >= MAX_TIMEOUTS:
# # #                     if self._ask_continue():
# # #                         consecutive_timeouts = 0
# # #                     else:
# # #                         break
# # #                 continue

# # #             # ---- 2. Detection sortie explicite ----------------------------
# # #             if any(w in chunk.lower() for w in EXIT_WORDS):
# # #                 print("\nSortie detectee : '%s'" % chunk)
# # #                 break

# # #             # ---- 3. Affichage console ------------------------------------
# # #             print("\n[Narration] " + chunk)
# # #             session.add_chunk(chunk)

# # #             # ---- 4. Analyse superviseur (1-3 s) --------------------------
# # #             decision = supervisor.analyse(session, chunk)
# # #             logger.info(
# # #                 "Superviseur: %s | '%s'",
# # #                 decision.decision.value,
# # #                 decision.message[:60] if decision.message else "",
# # #             )

# # #             # ---- 5. Reaction selon decision ------------------------------
# # #             if decision.decision == Decision.CONTINUER:
# # #                 continue

# # #             elif decision.decision == Decision.CONSEIL:
# # #                 print("\n[CONSEIL] " + decision.message)
# # #                 self.io.speak(decision.message)
# # #                 time.sleep(0.5)
# # #                 self.io.speak("Continuez.")

# # #             elif decision.decision == Decision.STOP:
# # #                 print("\n[STOP] " + decision.message)
# # #                 self.io.interrupt_and_speak(decision.message)
# # #                 if not self._handle_stop(session):
# # #                     break

# # #         print("\n\nFin de la narration. " + session.summary())

# # #     def _ask_continue(self) -> bool:
# # #         """Demande si l'utilisateur souhaite continuer apres plusieurs silences."""
# # #         text = self.io.listen_short(
# # #             "Je n'entends plus rien. "
# # #             "Souhaitez-vous continuer la narration ? "
# # #             "Dites oui pour continuer, non pour terminer."
# # #         )
# # #         if not text:
# # #             return False
# # #         return any(w in text.lower() for w in {"oui", "yes", "continuer", "continue", "si"})

# # #     def _handle_stop(self, session: NarratorSession) -> bool:
# # #         """Gere la pause apres un STOP. Retourne True si on reprend, False si on termine."""
# # #         self.io.speak(
# # #             "La narration est interrompue. "
# # #             "Dites reprendre pour continuer, ou fin pour terminer la session."
# # #         )
# # #         text = ""
# # #         try:
# # #             text = self.io.listen_chunk(
# # #                 pause_threshold=2.0,
# # #                 phrase_time_limit=10,
# # #                 listen_timeout=12,
# # #             )
# # #         except RuntimeError:
# # #             pass

# # #         if any(w in text.lower() for w in {"reprendre", "continuer", "oui", "yes"}):
# # #             self.io.speak("Tres bien. Vous pouvez reprendre votre narration.")
# # #             return True
# # #         return False

# # #     def _goodbye(self) -> None:
# # #         self.io.speak("Merci pour cette session de narration. A bientot !")
# # #         print("\nAu revoir !\n")

# # #     # ------------------------------------------------------------------
# # #     # LLM setup
# # #     # ------------------------------------------------------------------

# # #     def _setup_llm(self):
# # #         try:
# # #             from vr_scenario_lib.config import build_llm_config
# # #             return build_llm_config()
# # #         except Exception as exc:
# # #             logger.warning(
# # #                 "LLM config non disponible: %s -- supervision desactivee", exc
# # #             )
# # #             return None


# # # # ============================================================================
# # # # CLI
# # # # ============================================================================

# # # def _parse_args() -> argparse.Namespace:
# # #     p = argparse.ArgumentParser(
# # #         description="Application vocale de supervision de scenarios VR",
# # #         formatter_class=argparse.ArgumentDefaultsHelpFormatter,
# # #     )
# # #     p.add_argument(
# # #         "--stt-backend", default="whisper", choices=["whisper", "google"],
# # #         help="Backend STT.",
# # #     )
# # #     p.add_argument(
# # #         "--tts-backend", default=TTS_DEFAULT_BACKEND,
# # #         choices=["coqui", "piper", "gtts", "pyttsx3"],
# # #         help="Backend TTS. 'coqui' et 'piper' sont 100%% offline et francais natif.",
# # #     )
# # #     p.add_argument(
# # #         "--language", default="fr",
# # #         help="Code langue ISO 639-1 (fr par defaut).",
# # #     )
# # #     p.add_argument(
# # #         "--whisper-model", default=WHISPER_DEFAULT_MODEL,
# # #         choices=["tiny", "base", "small", "medium", "large"],
# # #         help="Taille du modele Whisper. 'small' recommande pour le francais.",
# # #     )
# # #     p.add_argument(
# # #         "--coqui-model", default=COQUI_MODEL_FR,
# # #         help="Identifiant modele Coqui TTS.",
# # #     )
# # #     p.add_argument(
# # #         "--piper-model", default=PIPER_MODEL_FR,
# # #         help="Nom du modele Piper (ex: fr_FR-tom-medium).",
# # #     )
# # #     p.add_argument(
# # #         "--debug", action="store_true",
# # #         help="Active le logging DEBUG.",
# # #     )
# # #     return p.parse_args()


# # # def main() -> None:
# # #     args = _parse_args()
# # #     if args.debug:
# # #         logging.getLogger().setLevel(logging.DEBUG)

# # #     io = VoiceIO(
# # #         stt_backend   = args.stt_backend,
# # #         tts_backend   = args.tts_backend,
# # #         language      = args.language,
# # #         whisper_model = args.whisper_model,
# # #         coqui_model   = args.coqui_model,
# # #         piper_model   = args.piper_model,
# # #     )
# # #     app = VRScenarioApp(io)
# # #     try:
# # #         app.run()
# # #     except KeyboardInterrupt:
# # #         print("\nInterruption utilisateur.")
# # #     finally:
# # #         io.close()


# # # if __name__ == "__main__":
# # #     main()


# # #!/usr/bin/env python3
# # """
# # Application vocale de supervision de scenarios VR.
# # Version enterprise -- standards industriels.

# # Architecture
# # ------------
# # VoiceIO      : STT (faster-whisper + SpeechRecognition VAD) + TTS natif francais.
# # ask_voice()  : pose une question, 3 tentatives STT, fallback clavier garanti.
# # VRScenarioApp: orchestration metier -- supervision en temps reel du recit utilisateur.

# # Flux principal
# # --------------
# # L'utilisateur narre librement son scenario VR. Le LLM superviseur ecoute chaque
# # segment de recit (fin de segment = 3 s de silence ou 30 s de parole) et repond :
# #   OK          -> re-ecoute immediate, sans TTS.
# #   CORRECTION  -> correction vocale breve, puis re-ecoute.
# #   STOP        -> arret vocale du scenario avec raison.

# # Backends TTS francais natifs (ordre de priorite automatique)
# # -------------------------------------------------------------
# # 1. coqui   -- Coqui VITS tts_models/fr/css10/vits : voix neurale offline, haute qualite
# # 2. piper   -- Piper fr_FR-upmc-medium              : voix neurale offline, ultra-rapide
# # 3. gtts    -- Google TTS                           : voix cloud, qualite maximale
# # 4. pyttsx3 -- espeak-fr                            : synthese basique, zero dependance

# # Usage:
# #     python app_vocal.py                           # auto-detection meilleur TTS dispo
# #     python app_vocal.py --tts-backend coqui       # Coqui VITS (offline, haute qualite)
# #     python app_vocal.py --tts-backend piper       # Piper (offline, ultra-rapide)
# #     python app_vocal.py --tts-backend gtts        # Google TTS (cloud)
# #     python app_vocal.py --stt-backend google      # Google STT (cloud)
# #     python app_vocal.py --whisper-model small     # meilleure precision STT
# #     python app_vocal.py --debug                   # logs DEBUG complets
# # """

# # from __future__ import annotations

# # import argparse
# # import logging
# # import os
# # import sys
# # import tempfile
# # import threading
# # import time
# # from dataclasses import dataclass
# # from typing import Optional

# # # ---------------------------------------------------------------------------
# # # Logging
# # # ---------------------------------------------------------------------------
# # logging.basicConfig(
# #     level=logging.INFO,
# #     format="%(asctime)s | %(name)-36s | %(levelname)-8s | %(message)s",
# #     datefmt="%H:%M:%S",
# # )
# # logger = logging.getLogger(__name__)

# # sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# # # ============================================================================
# # # Constantes
# # # ============================================================================

# # STT_MAX_ATTEMPTS      = 3
# # STT_LISTEN_TIMEOUT    = 8
# # STT_PHRASE_TIME_LIMIT = 20
# # STT_PROMPT_TIME_LIMIT = 120
# # STT_SILENCE_TIMEOUT   = 2.0
# # STT_PROMPT_SILENCE    = 3.5
# # STT_AMBIENT_DURATION  = 0.5
# # TTS_SPEECH_RATE       = 145
# # TTS_VOLUME            = 0.92
# # WHISPER_DEFAULT_MODEL = "base"
# # WHISPER_BEAM_SIZE     = 5
# # KEYBOARD_PROMPT       = "Saisissez votre reponse (ENTREE pour passer) : "
# # EXIT_WORDS            = {"quitter", "exit", "quit", "au revoir", "stop", "fin"}

# # # Backends TTS francais natifs
# # TTS_DEFAULT_BACKEND   = "coqui"          # priorite 1 : Coqui VITS offline
# # TTS_FALLBACK_CHAIN    = ["coqui", "piper", "gtts", "pyttsx3"]  # cascade automatique

# # # Coqui TTS
# # COQUI_MODEL_FR        = "tts_models/fr/css10/vits"   # voix feminime neurale, CSS10
# # COQUI_SAMPLE_RATE     = 22050

# # # Piper TTS
# # PIPER_MODEL_FR        = "fr_FR-upmc-medium"          # voix masculine neurale, UPMC
# # PIPER_SAMPLE_RATE     = 22050


# # # ============================================================================
# # # InputResult
# # # ============================================================================

# # @dataclass
# # class InputResult:
# #     """Resultat d'une interaction utilisateur."""
# #     text:     str = ""
# #     source:   str = "skipped"   # "stt" | "keyboard" | "skipped"
# #     attempts: int = 0

# #     def __bool__(self) -> bool:
# #         return bool(self.text)

# #     def is_exit(self) -> bool:
# #         return any(w in self.text.lower() for w in EXIT_WORDS)


# # # ============================================================================
# # # VoiceIO
# # # ============================================================================

# # class VoiceIO:
# #     """Couche bas-niveau STT + TTS.

# #     Regles fondamentales
# #     --------------------
# #     1. speak() est TOUJOURS bloquant dans le flux principal.
# #        Un TTS non-bloquant avant listen() = echo capture par Whisper.
# #     2. Le micro n'est jamais ouvert pendant la synthese vocale.
# #     3. L'enregistrement utilise la VAD (SpeechRecognition), pas une duree fixe.
# #     """

# #     def __init__(
# #         self,
# #         stt_backend:   str = "whisper",
# #         tts_backend:   str = TTS_DEFAULT_BACKEND,
# #         language:      str = "fr",
# #         whisper_model: str = WHISPER_DEFAULT_MODEL,
# #         coqui_model:   str = COQUI_MODEL_FR,
# #         piper_model:   str = PIPER_MODEL_FR,
# #     ) -> None:
# #         self.stt_backend      = stt_backend
# #         self.tts_backend      = tts_backend
# #         self.language         = language
# #         self.whisper_model_id = whisper_model
# #         self.coqui_model_id   = coqui_model
# #         self.piper_model_id   = piper_model

# #         self._recognizer    = None
# #         self._whisper_model = None
# #         self._tts_engine    = None      # pyttsx3
# #         self._coqui_model   = None      # Coqui TTS
# #         self._piper_proc    = None      # Piper (subprocess)
# #         self._lock_tts      = threading.Lock()

# #         self._init()

# #     # ------------------------------------------------------------------
# #     # Init
# #     # ------------------------------------------------------------------

# #     def _init(self) -> None:
# #         self._init_stt()
# #         self._init_tts()
# #         logger.info(
# #             "VoiceIO pret -- STT: %s | TTS: %s | Langue: %s",
# #             self.stt_backend, self.tts_backend, self.language,
# #         )

# #     def _init_stt(self) -> None:
# #         try:
# #             import speech_recognition as sr
# #             self._recognizer = sr.Recognizer()
# #             self._recognizer.energy_threshold        = 4000
# #             self._recognizer.pause_threshold         = STT_SILENCE_TIMEOUT
# #             self._recognizer.dynamic_energy_threshold = True
# #         except ImportError:
# #             raise RuntimeError(
# #                 "SpeechRecognition manquant. pip install SpeechRecognition PyAudio"
# #             )

# #         if self.stt_backend == "whisper":
# #             self._whisper_model = self._load_whisper()

# #     def _load_whisper(self) -> object:
# #         try:
# #             from faster_whisper import WhisperModel
# #             logger.info("Chargement faster-whisper '%s'...", self.whisper_model_id)
# #             model = WhisperModel(
# #                 self.whisper_model_id,
# #                 device="cpu",
# #                 compute_type="int8",
# #             )
# #             logger.info("faster-whisper pret")
# #             return model
# #         except ImportError:
# #             raise RuntimeError("faster-whisper manquant. pip install faster-whisper")

# #     def _init_tts(self) -> None:
# #         """Initialise le backend TTS demande avec cascade automatique si indisponible.

# #         Ordre de cascade : coqui -> piper -> gtts -> pyttsx3
# #         Chaque backend tente de s'initialiser ; en cas d'echec il passe au suivant.
# #         Si aucun backend ne fonctionne, RuntimeError est leve.
# #         """
# #         chain = (
# #             [self.tts_backend]
# #             + [b for b in TTS_FALLBACK_CHAIN if b != self.tts_backend]
# #         )
# #         for backend in chain:
# #             try:
# #                 if backend == "coqui":
# #                     self._init_coqui()
# #                 elif backend == "piper":
# #                     self._init_piper()
# #                 elif backend == "gtts":
# #                     self._init_gtts()
# #                 elif backend == "pyttsx3":
# #                     self._init_pyttsx3()
# #                 else:
# #                     continue
# #                 self.tts_backend = backend
# #                 logger.info("TTS backend actif : %s", backend)
# #                 return
# #             except Exception as exc:
# #                 logger.warning("TTS backend '%s' indisponible: %s -- essai suivant", backend, exc)

# #         raise RuntimeError(
# #             "Aucun backend TTS disponible. "
# #             "Installez au moins : pip install coqui-tts sounddevice soundfile"
# #         )

# #     # ------------------------------------------------------------------
# #     # Init Coqui VITS -- voix neurale francaise offline
# #     # ------------------------------------------------------------------

# #     def _init_coqui(self) -> None:
# #         """Charge Coqui TTS avec le modele VITS francais css10.

# #         Modele : tts_models/fr/css10/vits
# #         - Voix feminine neurale, corpus CSS10 (sentences francophones)
# #         - Qualite MOS ~4.1, inferencee en ~300 ms sur CPU
# #         - Telechargement automatique au premier usage (~120 MB)
# #         """
# #         try:
# #             from TTS.api import TTS as CoquiTTS
# #             import sounddevice  # noqa: F401 -- verifie que la lecture est possible
# #             import soundfile    # noqa: F401
# #         except ImportError:
# #             raise RuntimeError(
# #                 "Coqui TTS manquant. pip install coqui-tts sounddevice soundfile"
# #             )

# #         logger.info("Chargement Coqui TTS '%s'...", self.coqui_model_id)
# #         self._coqui_model = CoquiTTS(
# #             model_name=self.coqui_model_id,
# #             progress_bar=False,
# #             gpu=False,
# #         )
# #         logger.info("Coqui TTS pret (fr/css10/vits)")

# #     # ------------------------------------------------------------------
# #     # Init Piper -- voix neurale francaise offline, ultra-rapide
# #     # ------------------------------------------------------------------

# #     def _init_piper(self) -> None:
# #         """Verifie que piper-tts est installable et que le modele existe.

# #         Modele : fr_FR-upmc-medium (voix masculine, UPMC corpus, ~60 MB)
# #         Piper est appele en subprocess pour eviter les conflits de threads GIL.
# #         """
# #         try:
# #             import piper  # noqa: F401
# #         except ImportError:
# #             raise RuntimeError(
# #                 "piper-tts manquant. pip install piper-tts"
# #             )
# #         # Piper charge le modele a la premiere synthese (lazy)
# #         logger.info("Piper TTS disponible -- modele '%s'", self.piper_model_id)

# #     # ------------------------------------------------------------------
# #     # Init gTTS -- Google TTS cloud
# #     # ------------------------------------------------------------------

# #     def _init_gtts(self) -> None:
# #         try:
# #             import gtts    # noqa: F401
# #             import pygame  # noqa: F401
# #         except ImportError:
# #             raise RuntimeError("gTTS/pygame manquants. pip install gTTS pygame")
# #         logger.info("gTTS cloud initialise")

# #     # ------------------------------------------------------------------
# #     # Init pyttsx3 -- fallback ultime espeak
# #     # ------------------------------------------------------------------

# #     def _init_pyttsx3(self) -> None:
# #         try:
# #             import pyttsx3
# #         except ImportError:
# #             raise RuntimeError("pyttsx3 manquant. pip install pyttsx3")

# #         engine = pyttsx3.init()
# #         engine.setProperty("rate",   TTS_SPEECH_RATE)
# #         engine.setProperty("volume", TTS_VOLUME)

# #         # Forcer la voix francaise espeak
# #         fr_voice_found = False
# #         for v in engine.getProperty("voices"):
# #             if "french" in v.name.lower() or "fr" in v.id.lower():
# #                 engine.setProperty("voice", v.id)
# #                 logger.info("pyttsx3 voix francaise : %s", v.name)
# #                 fr_voice_found = True
# #                 break

# #         if not fr_voice_found:
# #             logger.warning(
# #                 "Aucune voix francaise trouvee dans pyttsx3. "
# #                 "Linux: sudo apt install espeak-ng-data"
# #             )

# #         self._tts_engine = engine
# #         logger.info("pyttsx3 initialise (voix systeme)")

# #     # ------------------------------------------------------------------
# #     # TTS -- TOUJOURS bloquant dans le flux principal
# #     # ------------------------------------------------------------------

# #     def speak(self, text: str, *, blocking: bool = True) -> None:
# #         """Synthese vocale en francais natif.

# #         blocking=True (defaut) : retourne APRES la fin de la lecture.
# #         blocking=False          : usage exceptionnel (ex: musique d'attente).
# #         REGLE : ne JAMAIS appeler avec blocking=False avant listen().
# #         """
# #         if not text or not text.strip():
# #             return
# #         logger.info("TTS [%s]: '%s'", self.tts_backend, text[:80])

# #         dispatch = {
# #             "coqui":   self._speak_coqui,
# #             "piper":   self._speak_piper,
# #             "gtts":    self._speak_gtts,
# #             "pyttsx3": self._speak_pyttsx3,
# #         }
# #         fn = dispatch.get(self.tts_backend)
# #         if fn is None:
# #             logger.error("Backend TTS inconnu: %s", self.tts_backend)
# #             print("[TTS] " + text)
# #             return
# #         fn(text, blocking)

# #     # ------------------------------------------------------------------
# #     # _speak_coqui : Coqui VITS fr/css10 -- reference qualite
# #     # ------------------------------------------------------------------

# #     def _speak_coqui(self, text: str, blocking: bool) -> None:
# #         """Synthese via Coqui VITS, lecture via sounddevice (non-pygame).

# #         Sounddevice est prefere a pygame : latence plus faible,
# #         pas de conflit avec le sous-systeme audio ALSA/PulseAudio.
# #         """
# #         tmp_path: Optional[str] = None
# #         try:
# #             import soundfile as sf
# #             import sounddevice as sd

# #             with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
# #                 tmp_path = f.name

# #             with self._lock_tts:
# #                 self._coqui_model.tts_to_file(
# #                     text=text,
# #                     file_path=tmp_path,
# #                 )

# #             data, sr = sf.read(tmp_path, dtype="float32")

# #             if blocking:
# #                 sd.play(data, sr)
# #                 sd.wait()
# #             else:
# #                 sd.play(data, sr)

# #         except Exception as exc:
# #             logger.error("Coqui TTS erreur: %s", exc)
# #             print("[TTS] " + text)
# #         finally:
# #             if tmp_path and os.path.exists(tmp_path):
# #                 try:
# #                     os.unlink(tmp_path)
# #                 except OSError:
# #                     pass

# #     # ------------------------------------------------------------------
# #     # _speak_piper : Piper fr_FR-upmc -- latence minimale
# #     # ------------------------------------------------------------------

# #     def _speak_piper(self, text: str, blocking: bool) -> None:
# #         """Synthese via Piper TTS (subprocess), lecture via sounddevice.

# #         Piper est invoque en subprocess pour isoler son eventuel GIL.
# #         Le WAV est lu en memoire puis joue sans fichier temporaire persistant.
# #         """
# #         tmp_path: Optional[str] = None
# #         try:
# #             import subprocess
# #             import soundfile as sf
# #             import sounddevice as sd

# #             with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
# #                 tmp_path = f.name

# #             result = subprocess.run(
# #                 [
# #                     "piper",
# #                     "--model", self.piper_model_id,
# #                     "--output_file", tmp_path,
# #                 ],
# #                 input=text.encode("utf-8"),
# #                 capture_output=True,
# #                 timeout=30,
# #             )

# #             if result.returncode != 0:
# #                 raise RuntimeError(
# #                     "piper returncode=%d: %s" % (result.returncode, result.stderr.decode())
# #                 )

# #             data, sr = sf.read(tmp_path, dtype="float32")
# #             if blocking:
# #                 sd.play(data, sr)
# #                 sd.wait()
# #             else:
# #                 sd.play(data, sr)

# #         except FileNotFoundError:
# #             logger.error("Executable 'piper' introuvable. pip install piper-tts")
# #             print("[TTS] " + text)
# #         except Exception as exc:
# #             logger.error("Piper TTS erreur: %s", exc)
# #             print("[TTS] " + text)
# #         finally:
# #             if tmp_path and os.path.exists(tmp_path):
# #                 try:
# #                     os.unlink(tmp_path)
# #                 except OSError:
# #                     pass

# #     # ------------------------------------------------------------------
# #     # _speak_gtts : Google TTS cloud
# #     # ------------------------------------------------------------------

# #     def _speak_gtts(self, text: str, blocking: bool) -> None:
# #         tmp_path: Optional[str] = None
# #         try:
# #             from gtts import gTTS
# #             import pygame
# #             tts = gTTS(text=text, lang=self.language, slow=False)
# #             with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
# #                 tmp_path = f.name
# #                 tts.save(tmp_path)
# #             pygame.mixer.init()
# #             pygame.mixer.music.load(tmp_path)
# #             pygame.mixer.music.play()
# #             if blocking:
# #                 while pygame.mixer.music.get_busy():
# #                     time.sleep(0.05)
# #                 pygame.mixer.quit()
# #         except Exception as exc:
# #             logger.error("gTTS erreur: %s", exc)
# #             print("[TTS] " + text)
# #         finally:
# #             if tmp_path and os.path.exists(tmp_path):
# #                 try:
# #                     os.unlink(tmp_path)
# #                 except OSError:
# #                     pass

# #     # ------------------------------------------------------------------
# #     # _speak_pyttsx3 : espeak fallback ultime
# #     # ------------------------------------------------------------------

# #     def _speak_pyttsx3(self, text: str, blocking: bool) -> None:
# #         with self._lock_tts:
# #             try:
# #                 self._tts_engine.say(text)
# #                 if blocking:
# #                     self._tts_engine.runAndWait()
# #                 else:
# #                     t = threading.Thread(
# #                         target=self._tts_engine.runAndWait, daemon=True
# #                     )
# #                     t.start()
# #             except Exception as exc:
# #                 logger.error("pyttsx3 erreur: %s", exc)
# #                 print("[TTS] " + text)

# #     # ------------------------------------------------------------------
# #     # STT -- VAD reelle
# #     # ------------------------------------------------------------------

# #     def listen(
# #         self,
# #         *,
# #         pause_threshold:   float = STT_SILENCE_TIMEOUT,
# #         phrase_time_limit: int   = STT_PHRASE_TIME_LIMIT,
# #         listen_timeout:    float = STT_LISTEN_TIMEOUT,
# #     ) -> str:
# #         """Capture parole (VAD) et transcrit.

# #         Returns:
# #             Texte transcrit non-vide.

# #         Raises:
# #             RuntimeError: Capture ou transcription impossible.
# #         """
# #         import speech_recognition as sr

# #         original = self._recognizer.pause_threshold
# #         self._recognizer.pause_threshold = pause_threshold
# #         tmp_path: Optional[str] = None

# #         try:
# #             # 1. Capture VAD
# #             try:
# #                 with sr.Microphone() as src:
# #                     logger.info(
# #                         "Ecoute (silence=%.1fs, max=%ds)...",
# #                         pause_threshold, phrase_time_limit,
# #                     )
# #                     self._recognizer.adjust_for_ambient_noise(
# #                         src, duration=STT_AMBIENT_DURATION
# #                     )
# #                     audio = self._recognizer.listen(
# #                         src,
# #                         timeout=listen_timeout,
# #                         phrase_time_limit=phrase_time_limit,
# #                     )
# #             except sr.WaitTimeoutError:
# #                 raise RuntimeError("Timeout -- aucun son detecte")

# #             # 2. Sauvegarde WAV
# #             with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
# #                 tmp_path = f.name
# #                 f.write(audio.get_wav_data())

# #             # 3. Transcription
# #             if self.stt_backend == "whisper":
# #                 return self._transcribe_whisper(tmp_path)
# #             else:
# #                 return self._transcribe_google(audio)

# #         finally:
# #             self._recognizer.pause_threshold = original
# #             if tmp_path and os.path.exists(tmp_path):
# #                 try:
# #                     os.unlink(tmp_path)
# #                 except OSError:
# #                     pass

# #     def _transcribe_whisper(self, wav_path: str) -> str:
# #         segments_gen, info = self._whisper_model.transcribe(
# #             wav_path,
# #             language=self.language,
# #             beam_size=WHISPER_BEAM_SIZE,
# #         )
# #         logger.debug(
# #             "Whisper: langue=%s (%.0f%%)",
# #             info.language, info.language_probability * 100,
# #         )
# #         text = " ".join(seg.text.strip() for seg in segments_gen).strip()
# #         if not text:
# #             raise RuntimeError("Whisper n'a produit aucun texte")
# #         logger.info("STT: '%s'", text[:100])
# #         return text

# #     def _transcribe_google(self, audio) -> str:
# #         import speech_recognition as sr
# #         lang = "fr-FR" if self.language == "fr" else self.language + "-" + self.language.upper()
# #         try:
# #             text = self._recognizer.recognize_google(audio, language=lang)
# #             logger.info("Google STT: '%s'", text[:100])
# #             return text
# #         except sr.UnknownValueError:
# #             raise RuntimeError("Google STT: audio incomprehensible")
# #         except sr.RequestError as exc:
# #             raise RuntimeError("Google STT: erreur API: %s" % exc)

# #     # ------------------------------------------------------------------
# #     # Nettoyage
# #     # ------------------------------------------------------------------

# #     def close(self) -> None:
# #         if self._tts_engine is not None:
# #             try:
# #                 with self._lock_tts:
# #                     self._tts_engine.stop()
# #             except Exception:
# #                 pass
# #         logger.info("VoiceIO ferme")


# # # ============================================================================
# # # ask_voice() -- interaction de haut niveau
# # # ============================================================================

# # def ask_voice(
# #     io:           VoiceIO,
# #     question:     str,
# #     *,
# #     max_attempts: int  = STT_MAX_ATTEMPTS,
# #     is_prompt:    bool = False,
# #     allow_skip:   bool = True,
# # ) -> InputResult:
# #     """Pose *question* vocalement avec 3 tentatives STT, fallback clavier garanti.

# #     Sequence par tentative
# #     ----------------------
# #     1. TTS bloquant (micro ferme).
# #     2. Ouverture micro (VAD -- pas de duree fixe).
# #     3. Transcription faster-whisper.
# #     4. OK -> retourne InputResult(source='stt').
# #     5. KO -> message d'erreur vocal + tentative suivante.
# #     Apres max_attempts -> clavier -> retourne InputResult(source='keyboard').

# #     Args:
# #         io:           Instance VoiceIO.
# #         question:     Texte de la question.
# #         max_attempts: Tentatives STT avant fallback (defaut 3).
# #         is_prompt:    True pour prompt long (silence etendu, limite 120s).
# #         allow_skip:   Si True, ENTREE vide -> InputResult(source='skipped').
# #     """
# #     pause = STT_PROMPT_SILENCE    if is_prompt else STT_SILENCE_TIMEOUT
# #     limit = STT_PROMPT_TIME_LIMIT if is_prompt else STT_PHRASE_TIME_LIMIT

# #     error_messages = [
# #         "Je n'ai pas compris. Parlez clairement apres le signal.",
# #         "Toujours pas compris. Reformulez en articulant bien.",
# #         "Troisieme tentative. Parlez lentement et distinctement.",
# #     ]

# #     for attempt in range(1, max_attempts + 1):

# #         # -- 1. TTS bloquant -- micro ferme --------------------------------
# #         io.speak(question)
# #         if attempt > 1:
# #             io.speak("Tentative %d sur %d. Je vous ecoute." % (attempt, max_attempts))
# #         else:
# #             io.speak("Je vous ecoute.")

# #         mode = "prompt" if is_prompt else "reponse"
# #         print("[Ecoute %s] tentative %d/%d..." % (mode, attempt, max_attempts))

# #         # -- 2. Capture + transcription ------------------------------------
# #         try:
# #             text = io.listen(
# #                 pause_threshold   = pause,
# #                 phrase_time_limit = limit,
# #                 listen_timeout    = STT_LISTEN_TIMEOUT,
# #             )
# #             print("Reconnu : " + text)
# #             return InputResult(text=text, source="stt", attempts=attempt)

# #         except RuntimeError as exc:
# #             logger.warning("STT echec %d/%d: %s", attempt, max_attempts, exc)
# #             if attempt < max_attempts:
# #                 io.speak(error_messages[attempt - 1])

# #     # -- 3. Fallback clavier -------------------------------------------
# #     io.speak(
# #         "La reconnaissance vocale a echoue %d fois. "
# #         "Veuillez utiliser le clavier." % max_attempts
# #     )
# #     print("\n" + "-" * 60)
# #     print("Question : " + question)
# #     print("-" * 60)

# #     try:
# #         text = input(KEYBOARD_PROMPT).strip()
# #     except (EOFError, KeyboardInterrupt):
# #         text = ""

# #     if not text and allow_skip:
# #         return InputResult(text="", source="skipped", attempts=max_attempts)

# #     return InputResult(text=text, source="keyboard", attempts=max_attempts)


# # # ============================================================================
# # # VRScenarioApp
# # # ============================================================================

# # # Prompt systeme du LLM superviseur.
# # # Il recoit le recit oral de l'utilisateur et doit repondre UNIQUEMENT par :
# # #   OK                      -- laisser continuer sans interruption
# # #   CORRECTION: <message>   -- corriger une erreur factuelle ou de procedure
# # #   STOP: <raison>          -- interrompre le scenario (danger, blocage critique)
# # _SUPERVISOR_SYSTEM_PROMPT = """\
# # Tu es un expert en securite industrielle et en formation VR.
# # L'utilisateur te narre oralement un scenario de formation.
# # Ton role est de superviser ce recit en temps reel.

# # Reponds UNIQUEMENT avec l'un de ces trois formats, sans texte supplementaire :
# #   OK
# #   CORRECTION: <message bref en francais, 1-2 phrases max>
# #   STOP: <raison breve en francais, 1-2 phrases max>

# # Regles de decision :
# # - OK            : le recit est correct, plausible, sans erreur critique.
# # - CORRECTION    : erreur factuelle, procedure incorrecte ou omission importante,
# #                   mais le scenario peut continuer apres correction.
# # - STOP          : danger manifeste, contradiction bloquante, ou demande
# #                   explicite de l'utilisateur (mots : stop, fin, quitter, exit).

# # Sois concis. Ne reformule pas le recit. Ne pose pas de questions.
# # """

# # # Duree max d'un segment de recit (secondes) avant supervision LLM
# # NARRATIVE_SEGMENT_LIMIT = 30   # 30 s de parole continue -> supervision
# # NARRATIVE_SILENCE       = 3.0  # silence de 3 s = fin de segment
# # NARRATIVE_MAX_SEGMENTS  = 50   # garde-fou anti-boucle infinie


# # class VRScenarioApp:
# #     """Orchestration : supervision en temps reel du recit de scenario VR.

# #     Flux principal
# #     --------------
# #     1. Accueil + saisie du theme.
# #     2. Boucle de narration :
# #        a. Ecoute un segment de recit (silence=3 s ou 30 s max).
# #        b. Envoie le segment au LLM superviseur.
# #        c. Reponse LLM :
# #           - OK          -> on re-ecoute immediatement (sans TTS).
# #           - CORRECTION  -> TTS de la correction, puis re-ecoute.
# #           - STOP        -> TTS de la raison, fin de session.
# #     3. Au revoir.
# #     """

# #     def __init__(self, io: VoiceIO) -> None:
# #         self.io = io

# #     def run(self) -> None:
# #         self._welcome()
# #         topic  = self._ask_topic()
# #         config = self._setup_llm()
# #         self._supervise_narrative(topic, config)
# #         self._goodbye()

# #     # ------------------------------------------------------------------
# #     # Etapes
# #     # ------------------------------------------------------------------

# #     def _welcome(self) -> None:
# #         print("\n" + "=" * 60)
# #         print("  APPLICATION VOCALE -- SUPERVISION DE SCENARIO VR")
# #         print("=" * 60)
# #         self.io.speak(
# #             "Bienvenue. "
# #             "Vous allez me narrer votre scenario de formation. "
# #             "Je vous ecouterai en continu et interviendrai si necessaire. "
# #             "Dites stop ou fin pour terminer a tout moment."
# #         )

# #     def _ask_topic(self) -> str:
# #         result = ask_voice(
# #             self.io,
# #             "Quel est le theme du scenario ? "
# #             "Par exemple : consignation gaz, securite incendie, premiers secours.",
# #         )
# #         if result.is_exit():
# #             self._goodbye()
# #             sys.exit(0)
# #         topic = result.text or "securite"
# #         if result.source == "skipped":
# #             self.io.speak("Theme par defaut : securite.")
# #         logger.info("Theme : '%s' (source=%s)", topic, result.source)
# #         print("\nTheme : " + topic)
# #         return topic

# #     def _setup_llm(self):
# #         try:
# #             from vr_scenario_lib.config import build_llm_config
# #             return build_llm_config()
# #         except Exception as exc:
# #             logger.warning("LLM config defaut: %s", exc)
# #             try:
# #                 from vr_scenario_lib.config import build_llm_config
# #                 return build_llm_config(
# #                     token="dummy",
# #                     api_url="https://openrouter.ai/api/v1/chat/completions",
# #                     model="openai/gpt-3.5-turbo",
# #                 )
# #             except Exception:
# #                 return None

# #     def _supervise_narrative(self, topic: str, config) -> None:
# #         """Boucle principale : ecoute le recit par segments, supervision LLM apres chaque segment."""
# #         self.io.speak(
# #             "Je suis pret. Commencez votre recit sur le theme : " + topic + ". "
# #             "Je vous ecoute."
# #         )

# #         history: list[dict] = []   # historique du recit pour contexte LLM
# #         segments = 0

# #         while segments < NARRATIVE_MAX_SEGMENTS:
# #             # -- Ecoute d'un segment de recit (silence=3 s, max=30 s) --------
# #             print("\n[Ecoute recit] segment %d..." % (segments + 1))
# #             try:
# #                 segment_text = self.io.listen(
# #                     pause_threshold   = NARRATIVE_SILENCE,
# #                     phrase_time_limit = NARRATIVE_SEGMENT_LIMIT,
# #                     listen_timeout    = STT_LISTEN_TIMEOUT,
# #                 )
# #             except RuntimeError as exc:
# #                 logger.warning("STT segment: %s", exc)
# #                 self.io.speak("Je n'ai rien entendu. Continuez votre recit.")
# #                 continue

# #             segments += 1
# #             print("Segment %d : %s" % (segments, segment_text))

# #             # Mot de sortie explicite dans le recit
# #             if any(w in segment_text.lower() for w in EXIT_WORDS):
# #                 self.io.speak("Fin de session demandee. Arret du scenario.")
# #                 break

# #             # -- Supervision LLM --------------------------------------------
# #             verdict = self._llm_supervise(segment_text, topic, history, config)

# #             if verdict is None:
# #                 # Pas de LLM configure : on laisse passer silencieusement
# #                 history.append({"role": "user", "content": segment_text})
# #                 continue

# #             verdict_upper = verdict.strip().upper()

# #             if verdict_upper == "OK":
# #                 logger.info("LLM superviseur : OK -- continuation")
# #                 history.append({"role": "user", "content": segment_text})
# #                 # Pas de TTS : on re-ecoute immediatement

# #             elif verdict.upper().startswith("CORRECTION"):
# #                 correction = verdict[len("CORRECTION"):].lstrip(": ").strip()
# #                 logger.info("LLM superviseur : CORRECTION -- %s", correction)
# #                 print("\n[CORRECTION] " + correction)
# #                 self.io.speak("Correction : " + correction + ". Continuez.")
# #                 history.append({"role": "user",      "content": segment_text})
# #                 history.append({"role": "assistant", "content": "CORRECTION: " + correction})

# #             elif verdict.upper().startswith("STOP"):
# #                 raison = verdict[len("STOP"):].lstrip(": ").strip()
# #                 logger.info("LLM superviseur : STOP -- %s", raison)
# #                 print("\n[STOP] " + raison)
# #                 self.io.speak("Scenario arrete. " + raison)
# #                 break

# #             else:
# #                 # Reponse inattendue : on logue et on continue
# #                 logger.warning("LLM reponse inattendue: '%s'", verdict[:80])
# #                 history.append({"role": "user", "content": segment_text})

# #         else:
# #             self.io.speak("Nombre maximum de segments atteint. Fin de la session.")

# #     def _llm_supervise(
# #         self,
# #         segment:  str,
# #         topic:    str,
# #         history:  list,
# #         config,
# #     ) -> Optional[str]:
# #         """Envoie le segment au LLM et retourne sa decision brute (OK / CORRECTION / STOP).

# #         Retourne None si le LLM n'est pas configure ou en cas d'erreur.
# #         """
# #         if config is None:
# #             return None

# #         try:
# #             from vr_scenario_lib.scenario import discuss_scenario as llm_discuss
# #             from vr_scenario_lib.scenario_store import ScenarioSession

# #             # Contexte minimal : theme + historique recit
# #             context = "Theme du scenario : " + topic + ".\n"
# #             if history:
# #                 context += "Recit precedent :\n"
# #                 context += "\n".join(
# #                     h["content"] for h in history if h["role"] == "user"
# #                 )
# #                 context += "\n"
# #             context += "Nouveau segment : " + segment

# #             session = ScenarioSession(context)
# #             reply = llm_discuss(
# #                 session     = session,
# #                 user_message= context,
# #                 llm_config  = config,
# #                 system_override = _SUPERVISOR_SYSTEM_PROMPT,
# #             )
# #             logger.debug("LLM raw reply: '%s'", reply[:120])
# #             return reply.strip()

# #         except Exception as exc:
# #             logger.error("LLM supervision erreur: %s", exc)
# #             return None

# #     def _goodbye(self) -> None:
# #         self.io.speak("Merci. Session terminee. Au revoir !")
# #         print("\nAu revoir !\n")




# # # ============================================================================
# # # CLI
# # # ============================================================================

# # def _parse_args() -> argparse.Namespace:
# #     p = argparse.ArgumentParser(
# #         description="Application vocale scenarios VR",
# #         formatter_class=argparse.ArgumentDefaultsHelpFormatter,
# #     )
# #     p.add_argument("--stt-backend",   default="whisper",
# #                    choices=["whisper", "google"])
# #     p.add_argument("--tts-backend",   default=TTS_DEFAULT_BACKEND,
# #                    choices=["coqui", "piper", "gtts", "pyttsx3"],
# #                    help="Backend TTS. 'coqui' et 'piper' sont 100%% offline et francais natif.")
# #     p.add_argument("--language",      default="fr",
# #                    help="Code langue ISO 639-1 (fr par defaut).")
# #     p.add_argument("--whisper-model", default=WHISPER_DEFAULT_MODEL,
# #                    choices=["tiny", "base", "small", "medium", "large"],
# #                    help="Taille du modele Whisper. 'small' recommande pour le francais.")
# #     p.add_argument("--coqui-model",   default=COQUI_MODEL_FR,
# #                    help="Identifiant modele Coqui TTS.")
# #     p.add_argument("--piper-model",   default=PIPER_MODEL_FR,
# #                    help="Nom du modele Piper (ex: fr_FR-tom-medium).")
# #     p.add_argument("--debug",         action="store_true",
# #                    help="Active le logging DEBUG.")
# #     return p.parse_args()


# # def main() -> None:
# #     args = _parse_args()
# #     if args.debug:
# #         logging.getLogger().setLevel(logging.DEBUG)

# #     io = VoiceIO(
# #         stt_backend   = args.stt_backend,
# #         tts_backend   = args.tts_backend,
# #         language      = args.language,
# #         whisper_model = args.whisper_model,
# #         coqui_model   = args.coqui_model,
# #         piper_model   = args.piper_model,
# #     )
# #     app = VRScenarioApp(io)
# #     try:
# #         app.run()
# #     except KeyboardInterrupt:
# #         print("\nInterruption utilisateur.")
# #     finally:
# #         io.close()


# # if __name__ == "__main__":
# #     main()

# #!/usr/bin/env python3
# """
# Application vocale de supervision de scenarios VR.
# Version enterprise -- standards industriels.

# ROLE DE L'APP
# -------------
# L'utilisateur decrit librement un scenario VR a voix haute.
# L'application ecoute en continu, transcrit par chunks VAD, et
# soumet chaque chunk a un LLM superviseur qui peut :
#   - CONTINUER  : ne rien dire (ecoute silencieuse)
#   - CONSEIL    : interrompre poliment pour donner un conseil
#   - STOP       : interrompre fermement pour signaler une erreur critique

# Architecture
# ------------
# VoiceIO          : STT (faster-whisper + SpeechRecognition VAD) + TTS francais natif.
# SupervisorLLM    : analyse chaque chunk, decide CONTINUER / CONSEIL / STOP.
# NarratorSession  : accumule la transcription, maintient le contexte du scenario.
# VRScenarioApp    : orchestration metier (setup + boucle de narration supervisee).

# Backends TTS francais natifs (ordre de priorite automatique)
# ------------------------------------------------------------
# 1. coqui   -- Coqui VITS tts_models/fr/css10/vits  : voix neurale offline, haute qualite
# 2. piper   -- Piper fr_FR-upmc-medium               : voix neurale offline, ultra-rapide
# 3. gtts    -- Google TTS                            : voix cloud, qualite maximale
# 4. pyttsx3 -- espeak-fr                             : synthese basique, zero dependance

# Usage:
#     python app_vocal.py                            # auto-detection meilleur TTS dispo
#     python app_vocal.py --tts-backend coqui        # Coqui VITS (offline, haute qualite)
#     python app_vocal.py --tts-backend piper        # Piper (offline, ultra-rapide)
#     python app_vocal.py --tts-backend gtts         # Google TTS (cloud)
#     python app_vocal.py --stt-backend google       # Google STT (cloud)
#     python app_vocal.py --whisper-model small      # meilleure precision STT
#     python app_vocal.py --debug                    # logs DEBUG complets
# """

# from __future__ import annotations

# import argparse
# import json
# import logging
# import os
# import sys
# import tempfile
# import threading
# import time
# import uuid
# from dataclasses import dataclass, field
# from datetime import datetime, timezone
# from enum import Enum
# from typing import Any, Dict, List, Optional

# # ---------------------------------------------------------------------------
# # Logging
# # ---------------------------------------------------------------------------
# logging.basicConfig(
#     level=logging.INFO,
#     format="%(asctime)s | %(name)-36s | %(levelname)-8s | %(message)s",
#     datefmt="%H:%M:%S",
# )
# logger = logging.getLogger(__name__)

# sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# # ============================================================================
# # Constantes
# # ============================================================================

# STT_LISTEN_TIMEOUT    = 8
# STT_PHRASE_TIME_LIMIT = 20          # duree max d'un chunk narration
# STT_SILENCE_TIMEOUT   = 2.0         # silence VAD -> fin du chunk
# STT_AMBIENT_DURATION  = 0.5
# TTS_SPEECH_RATE       = 145
# TTS_VOLUME            = 0.92
# WHISPER_DEFAULT_MODEL = "base"
# WHISPER_BEAM_SIZE     = 5
# EXIT_WORDS            = {"quitter", "exit", "quit", "au revoir", "stop", "fin"}

# # Backends TTS francais natifs
# TTS_DEFAULT_BACKEND   = "coqui"
# TTS_FALLBACK_CHAIN    = ["coqui", "piper", "gtts", "pyttsx3"]

# # Coqui TTS
# COQUI_MODEL_FR        = "tts_models/fr/css10/vits"
# COQUI_SAMPLE_RATE     = 22050

# # Piper TTS
# PIPER_MODEL_FR        = "fr_FR-upmc-medium"
# PIPER_SAMPLE_RATE     = 22050

# # Supervisor LLM
# SUPERVISOR_MAX_TOKENS = 256
# SUPERVISOR_SYSTEM = (
#     "Tu es un superviseur expert en securite VR et en procedures industrielles. "
#     "L'utilisateur decrit a voix haute un scenario de formation VR. "
#     "Tu recois des fragments de sa narration en temps reel.\n\n"
#     "Analyse le dernier fragment dans son contexte et reponds UNIQUEMENT avec un objet JSON :\n"
#     '{"decision": "CONTINUER" | "CONSEIL" | "STOP", "message": "<texte a dire, vide si CONTINUER>"}\n\n'
#     "Regles strictes :\n"
#     "- CONTINUER  : narration correcte, coherente, sans danger. Message vide obligatoire.\n"
#     "- CONSEIL    : amelioration possible. Message court, positif, actionnable. Max 2 phrases.\n"
#     "- STOP       : erreur critique de procedure, danger reel, incoherence grave. "
#     "Message direct et precis. Commence par 'Attention : '.\n"
#     "Ne jamais inventer de contexte non mentionne. Rester factuel."
# )

# # Scenario generation LLM
# SCENARIO_GEN_MAX_TOKENS = 1024
# SCENARIO_GEN_SYSTEM = (
#     "Tu es un expert en conception de scenarios de formation VR industrielle. "
#     "A partir d'un theme, genere un scenario structure en JSON UNIQUEMENT, sans aucun texte avant ou apres.\n\n"
#     "Format JSON attendu (respecte exactement ces cles) :\n"
#     '{\n'
#     '  "titre": "Titre court du scenario",\n'
#     '  "objectifs": ["objectif 1", "objectif 2", "objectif 3"],\n'
#     '  "grandes_lignes": [\n'
#     '    {"etape": 1, "titre": "Titre etape", "description": "Description concise"},\n'
#     '    ...\n'
#     '  ],\n'
#     '  "procedures_cles": ["procedure 1", "procedure 2"],\n'
#     '  "points_vigilance": ["point 1", "point 2"],\n'
#     '  "resume_oral": "Texte fluide de 3-4 phrases pour lecture TTS. Pas de liste, pas de symboles."\n'
#     '}\n\n'
#     "Le champ resume_oral doit etre lisible a voix haute sans accroc : pas de tirets, "
#     "pas de parentheses, pas d'abreviations. Maximum 4 phrases."
# )

# # Q&R supervisee
# QA_MAX_TOKENS = 512
# QA_SYSTEM = (
#     "Tu es un formateur expert qui aide un apprenant a comprendre un scenario de formation VR. "
#     "Tu reponds aux questions en te basant exclusivement sur le scenario fourni. "
#     "Tes reponses sont courtes (2-3 phrases maximum), claires, et adaptees a une lecture TTS : "
#     "pas de listes, pas de tirets, pas de symboles. Parle directement a l'apprenant."
# )


# # ============================================================================
# # Decision + NarratorSession
# # ============================================================================

# class Decision(Enum):
#     CONTINUER = "CONTINUER"
#     CONSEIL   = "CONSEIL"
#     STOP      = "STOP"


# @dataclass
# class SupervisorDecision:
#     decision: Decision = Decision.CONTINUER
#     message:  str      = ""

#     def must_speak(self) -> bool:
#         return self.decision in (Decision.CONSEIL, Decision.STOP)


# @dataclass
# class NarratorSession:
#     """Accumule la transcription et maintient le contexte pour le LLM."""
#     topic:     str
#     chunks:    List[str] = field(default_factory=list)
#     full_text: str       = ""

#     def add_chunk(self, text: str) -> None:
#         self.chunks.append(text)
#         self.full_text = " ".join(self.chunks)

#     def context_window(self, n: int = 5) -> str:
#         return " ".join(self.chunks[-n:])

#     def summary(self) -> str:
#         return "%d sequence(s), ~%d mots" % (len(self.chunks), len(self.full_text.split()))


# # ============================================================================
# # SupervisorLLM
# # ============================================================================

# class SupervisorLLM:
#     """Analyse les chunks de narration et produit des decisions superviseur."""

#     def __init__(self, config) -> None:
#         self._config = config
#         self._lock   = threading.Lock()

#     def analyse(self, session: NarratorSession, new_chunk: str) -> SupervisorDecision:
#         if self._config is None:
#             return SupervisorDecision()

#         user_msg = (
#             "Theme du scenario : %s\n\n"
#             "Contexte (narration precedente) :\n%s\n\n"
#             "Nouveau fragment :\n%s"
#         ) % (session.topic, session.context_window(), new_chunk)

#         try:
#             with self._lock:
#                 raw = self._call_llm(user_msg)
#             return self._parse(raw)
#         except Exception as exc:
#             logger.warning("SupervisorLLM erreur: %s", exc)
#             return SupervisorDecision()

#     def _call_llm(self, user_msg: str) -> str:
#         # Tentative via vr_scenario_lib
#         try:
#             from vr_scenario_lib.llm import call_llm
#             return call_llm(
#                 system=SUPERVISOR_SYSTEM,
#                 user=user_msg,
#                 llm_config=self._config,
#                 max_tokens=SUPERVISOR_MAX_TOKENS,
#             )
#         except ImportError:
#             pass

#         # Fallback HTTP direct (OpenAI-compatible)
#         import json
#         import urllib.request

#         payload = json.dumps({
#             "model":      getattr(self._config, "model", "gpt-3.5-turbo"),
#             "max_tokens": SUPERVISOR_MAX_TOKENS,
#             "messages":   [
#                 {"role": "system", "content": SUPERVISOR_SYSTEM},
#                 {"role": "user",   "content": user_msg},
#             ],
#         }).encode()
#         api_url = getattr(self._config, "api_url", "https://api.openai.com/v1/chat/completions")
#         token   = getattr(self._config, "token", "")
#         req = urllib.request.Request(
#             api_url,
#             data=payload,
#             headers={
#                 "Content-Type":  "application/json",
#                 "Authorization": "Bearer " + token,
#             },
#         )
#         with urllib.request.urlopen(req, timeout=15) as resp:
#             data = json.loads(resp.read())
#         return data["choices"][0]["message"]["content"]

#     def _parse(self, raw: str) -> SupervisorDecision:
#         import json
#         import re
#         m = re.search(r'\{.*\}', raw, re.DOTALL)
#         if not m:
#             logger.warning("SupervisorLLM: JSON introuvable dans '%s'", raw[:120])
#             return SupervisorDecision()
#         obj = json.loads(m.group())
#         try:
#             dec = Decision(obj.get("decision", "CONTINUER").upper())
#         except ValueError:
#             dec = Decision.CONTINUER
#         return SupervisorDecision(decision=dec, message=obj.get("message", "").strip())


# # ============================================================================
# # VoiceIO
# # ============================================================================

# class VoiceIO:
#     """Couche bas-niveau STT + TTS.

#     Regles fondamentales
#     --------------------
#     1. speak() est TOUJOURS bloquant dans le flux principal.
#        Un TTS non-bloquant avant listen() = echo capture par Whisper.
#     2. Le micro n'est jamais ouvert pendant la synthese vocale.
#     3. L'enregistrement utilise la VAD (SpeechRecognition), pas une duree fixe.
#     4. interrupt_and_speak() coupe l'audio en cours avant de parler (STOP urgents).
#     """

#     def __init__(
#         self,
#         stt_backend:   str = "whisper",
#         tts_backend:   str = TTS_DEFAULT_BACKEND,
#         language:      str = "fr",
#         whisper_model: str = WHISPER_DEFAULT_MODEL,
#         coqui_model:   str = COQUI_MODEL_FR,
#         piper_model:   str = PIPER_MODEL_FR,
#     ) -> None:
#         self.stt_backend      = stt_backend
#         self.tts_backend      = tts_backend
#         self.language         = language
#         self.whisper_model_id = whisper_model
#         self.coqui_model_id   = coqui_model
#         self.piper_model_id   = piper_model

#         self._recognizer    = None
#         self._whisper_model = None
#         self._tts_engine    = None
#         self._coqui_model   = None
#         self._lock_tts      = threading.Lock()

#         self._init()

#     # ------------------------------------------------------------------
#     # Init
#     # ------------------------------------------------------------------

#     def _init(self) -> None:
#         self._init_stt()
#         self._init_tts()
#         logger.info(
#             "VoiceIO pret -- STT: %s | TTS: %s | Langue: %s",
#             self.stt_backend, self.tts_backend, self.language,
#         )

#     def _init_stt(self) -> None:
#         try:
#             import speech_recognition as sr
#             self._recognizer = sr.Recognizer()
#             self._recognizer.energy_threshold         = 4000
#             self._recognizer.pause_threshold          = STT_SILENCE_TIMEOUT
#             self._recognizer.dynamic_energy_threshold = True
#         except ImportError:
#             raise RuntimeError(
#                 "SpeechRecognition manquant. pip install SpeechRecognition PyAudio"
#             )
#         if self.stt_backend == "whisper":
#             self._whisper_model = self._load_whisper()

#     def _load_whisper(self) -> object:
#         try:
#             from faster_whisper import WhisperModel
#             logger.info("Chargement faster-whisper '%s'...", self.whisper_model_id)
#             model = WhisperModel(
#                 self.whisper_model_id,
#                 device="cpu",
#                 compute_type="int8",
#             )
#             logger.info("faster-whisper pret")
#             return model
#         except ImportError:
#             raise RuntimeError("faster-whisper manquant. pip install faster-whisper")

#     def _init_tts(self) -> None:
#         chain = (
#             [self.tts_backend]
#             + [b for b in TTS_FALLBACK_CHAIN if b != self.tts_backend]
#         )
#         for backend in chain:
#             try:
#                 if backend == "coqui":
#                     self._init_coqui()
#                 elif backend == "piper":
#                     self._init_piper()
#                 elif backend == "gtts":
#                     self._init_gtts()
#                 elif backend == "pyttsx3":
#                     self._init_pyttsx3()
#                 else:
#                     continue
#                 self.tts_backend = backend
#                 logger.info("TTS backend actif : %s", backend)
#                 return
#             except Exception as exc:
#                 logger.warning(
#                     "TTS backend '%s' indisponible: %s -- essai suivant", backend, exc
#                 )

#         raise RuntimeError(
#             "Aucun backend TTS disponible. "
#             "Installez au moins : pip install coqui-tts sounddevice soundfile"
#         )

#     # ------------------------------------------------------------------
#     # Init Coqui VITS -- voix neurale francaise offline
#     # ------------------------------------------------------------------

#     def _init_coqui(self) -> None:
#         try:
#             from TTS.api import TTS as CoquiTTS
#             import sounddevice  # noqa: F401
#             import soundfile    # noqa: F401
#         except ImportError:
#             raise RuntimeError(
#                 "Coqui TTS manquant. pip install coqui-tts sounddevice soundfile"
#             )
#         logger.info("Chargement Coqui TTS '%s'...", self.coqui_model_id)
#         self._coqui_model = CoquiTTS(
#             model_name=self.coqui_model_id,
#             progress_bar=False,
#             gpu=False,
#         )
#         logger.info("Coqui TTS pret (fr/css10/vits)")

#     # ------------------------------------------------------------------
#     # Init Piper -- voix neurale francaise offline, ultra-rapide
#     # ------------------------------------------------------------------

#     def _init_piper(self) -> None:
#         try:
#             import piper  # noqa: F401
#         except ImportError:
#             raise RuntimeError("piper-tts manquant. pip install piper-tts")
#         logger.info("Piper TTS disponible -- modele '%s'", self.piper_model_id)

#     # ------------------------------------------------------------------
#     # Init gTTS -- Google TTS cloud
#     # ------------------------------------------------------------------

#     def _init_gtts(self) -> None:
#         try:
#             import gtts    # noqa: F401
#             import pygame  # noqa: F401
#         except ImportError:
#             raise RuntimeError("gTTS/pygame manquants. pip install gTTS pygame")
#         logger.info("gTTS cloud initialise")

#     # ------------------------------------------------------------------
#     # Init pyttsx3 -- fallback ultime espeak
#     # ------------------------------------------------------------------

#     def _init_pyttsx3(self) -> None:
#         try:
#             import pyttsx3
#         except ImportError:
#             raise RuntimeError("pyttsx3 manquant. pip install pyttsx3")

#         engine = pyttsx3.init()
#         engine.setProperty("rate",   TTS_SPEECH_RATE)
#         engine.setProperty("volume", TTS_VOLUME)

#         fr_voice_found = False
#         for v in engine.getProperty("voices"):
#             if "french" in v.name.lower() or "fr" in v.id.lower():
#                 engine.setProperty("voice", v.id)
#                 logger.info("pyttsx3 voix francaise : %s", v.name)
#                 fr_voice_found = True
#                 break

#         if not fr_voice_found:
#             logger.warning(
#                 "Aucune voix francaise trouvee dans pyttsx3. "
#                 "Linux: sudo apt install espeak-ng-data"
#             )

#         self._tts_engine = engine
#         logger.info("pyttsx3 initialise (voix systeme)")

#     # ------------------------------------------------------------------
#     # TTS -- TOUJOURS bloquant dans le flux principal
#     # ------------------------------------------------------------------

#     def interrupt_and_speak(self, text: str) -> None:
#         """Coupe l'audio en cours PUIS parle. Reserve aux STOP urgents."""
#         self._stop_audio()
#         self.speak(text)

#     def _stop_audio(self) -> None:
#         """Arrete immediatement la lecture audio (tous backends)."""
#         try:
#             if self.tts_backend in ("coqui", "piper"):
#                 import sounddevice as sd
#                 sd.stop()
#             elif self.tts_backend == "gtts":
#                 try:
#                     import pygame
#                     if pygame.mixer.get_init():
#                         pygame.mixer.music.stop()
#                 except Exception:
#                     pass
#         except Exception as exc:
#             logger.debug("_stop_audio: %s", exc)

#     def speak(self, text: str, *, blocking: bool = True) -> None:
#         """Synthese vocale en francais natif.

#         blocking=True (defaut) : retourne APRES la fin de la lecture.
#         blocking=False         : usage exceptionnel uniquement.
#         REGLE : ne JAMAIS appeler avec blocking=False avant listen().
#         """
#         if not text or not text.strip():
#             return
#         logger.info("TTS [%s]: '%s'", self.tts_backend, text[:80])

#         dispatch = {
#             "coqui":   self._speak_coqui,
#             "piper":   self._speak_piper,
#             "gtts":    self._speak_gtts,
#             "pyttsx3": self._speak_pyttsx3,
#         }
#         fn = dispatch.get(self.tts_backend)
#         if fn is None:
#             logger.error("Backend TTS inconnu: %s", self.tts_backend)
#             print("[TTS] " + text)
#             return
#         fn(text, blocking)

#     # ------------------------------------------------------------------
#     # _speak_coqui : Coqui VITS fr/css10 -- reference qualite
#     # ------------------------------------------------------------------

#     def _speak_coqui(self, text: str, blocking: bool) -> None:
#         tmp_path: Optional[str] = None
#         try:
#             import soundfile as sf
#             import sounddevice as sd

#             with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
#                 tmp_path = f.name

#             with self._lock_tts:
#                 self._coqui_model.tts_to_file(text=text, file_path=tmp_path)

#             data, sr = sf.read(tmp_path, dtype="float32")
#             if blocking:
#                 sd.play(data, sr)
#                 sd.wait()
#             else:
#                 sd.play(data, sr)

#         except Exception as exc:
#             logger.error("Coqui TTS erreur: %s", exc)
#             print("[TTS] " + text)
#         finally:
#             if tmp_path and os.path.exists(tmp_path):
#                 try:
#                     os.unlink(tmp_path)
#                 except OSError:
#                     pass

#     # ------------------------------------------------------------------
#     # _speak_piper : Piper fr_FR-upmc -- latence minimale
#     # ------------------------------------------------------------------

#     def _speak_piper(self, text: str, blocking: bool) -> None:
#         tmp_path: Optional[str] = None
#         try:
#             import subprocess
#             import soundfile as sf
#             import sounddevice as sd

#             with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
#                 tmp_path = f.name

#             result = subprocess.run(
#                 ["piper", "--model", self.piper_model_id, "--output_file", tmp_path],
#                 input=text.encode("utf-8"),
#                 capture_output=True,
#                 timeout=30,
#             )
#             if result.returncode != 0:
#                 raise RuntimeError(
#                     "piper returncode=%d: %s" % (result.returncode, result.stderr.decode())
#                 )

#             data, sr = sf.read(tmp_path, dtype="float32")
#             if blocking:
#                 sd.play(data, sr)
#                 sd.wait()
#             else:
#                 sd.play(data, sr)

#         except FileNotFoundError:
#             logger.error("Executable 'piper' introuvable. pip install piper-tts")
#             print("[TTS] " + text)
#         except Exception as exc:
#             logger.error("Piper TTS erreur: %s", exc)
#             print("[TTS] " + text)
#         finally:
#             if tmp_path and os.path.exists(tmp_path):
#                 try:
#                     os.unlink(tmp_path)
#                 except OSError:
#                     pass

#     # ------------------------------------------------------------------
#     # _speak_gtts : Google TTS cloud
#     # Bug corrige : mixer reinitialise a chaque appel (non-reentrant).
#     # ------------------------------------------------------------------

#     def _speak_gtts(self, text: str, blocking: bool) -> None:
#         tmp_path: Optional[str] = None
#         try:
#             from gtts import gTTS
#             import pygame

#             tts = gTTS(text=text, lang=self.language, slow=False)
#             with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
#                 tmp_path = f.name
#             tts.save(tmp_path)

#             # Reinitialisation propre du mixer a chaque appel
#             if pygame.mixer.get_init():
#                 pygame.mixer.quit()
#             pygame.mixer.init(frequency=22050, size=-16, channels=1, buffer=512)
#             pygame.mixer.music.load(tmp_path)
#             pygame.mixer.music.play()

#             if blocking:
#                 while pygame.mixer.music.get_busy():
#                     time.sleep(0.05)
#                 pygame.mixer.quit()

#         except Exception as exc:
#             logger.error("gTTS erreur: %s", exc)
#             print("[TTS] " + text)
#         finally:
#             if tmp_path and os.path.exists(tmp_path):
#                 try:
#                     time.sleep(0.1)   # libere le handle fichier
#                     os.unlink(tmp_path)
#                 except OSError:
#                     pass

#     # ------------------------------------------------------------------
#     # _speak_pyttsx3 : espeak fallback ultime
#     # ------------------------------------------------------------------

#     def _speak_pyttsx3(self, text: str, blocking: bool) -> None:
#         with self._lock_tts:
#             try:
#                 self._tts_engine.say(text)
#                 if blocking:
#                     self._tts_engine.runAndWait()
#                 else:
#                     # NOTE : non-bloquant uniquement si explicitement demande.
#                     # Ne jamais appeler avant listen() -- race condition micro.
#                     t = threading.Thread(
#                         target=self._tts_engine.runAndWait, daemon=True
#                     )
#                     t.start()
#             except Exception as exc:
#                 logger.error("pyttsx3 erreur: %s", exc)
#                 print("[TTS] " + text)

#     # ------------------------------------------------------------------
#     # STT -- chunk VAD (narration continue)
#     # ------------------------------------------------------------------

#     def listen_chunk(
#         self,
#         *,
#         pause_threshold:   float = STT_SILENCE_TIMEOUT,
#         phrase_time_limit: int   = STT_PHRASE_TIME_LIMIT,
#         listen_timeout:    float = STT_LISTEN_TIMEOUT,
#     ) -> str:
#         """Capture un chunk de parole (VAD) et transcrit.

#         Returns:
#             Texte transcrit non-vide.

#         Raises:
#             RuntimeError: Capture ou transcription impossible.
#         """
#         import speech_recognition as sr

#         original = self._recognizer.pause_threshold
#         self._recognizer.pause_threshold = pause_threshold
#         tmp_path: Optional[str] = None

#         try:
#             with sr.Microphone() as src:
#                 logger.info(
#                     "Ecoute chunk (silence=%.1fs, max=%ds)...",
#                     pause_threshold, phrase_time_limit,
#                 )
#                 self._recognizer.adjust_for_ambient_noise(src, duration=STT_AMBIENT_DURATION)
#                 audio = self._recognizer.listen(
#                     src,
#                     timeout=listen_timeout,
#                     phrase_time_limit=phrase_time_limit,
#                 )

#             with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
#                 tmp_path = f.name
#                 f.write(audio.get_wav_data())

#             if self.stt_backend == "whisper":
#                 return self._transcribe_whisper(tmp_path)
#             else:
#                 return self._transcribe_google(audio)

#         finally:
#             self._recognizer.pause_threshold = original
#             if tmp_path and os.path.exists(tmp_path):
#                 try:
#                     os.unlink(tmp_path)
#                 except OSError:
#                     pass

#     def listen_short(self, question: str, timeout: float = 8.0) -> str:
#         """Pose une question courte et attend une reponse breve.
#         Retourne la chaine vide en cas d'echec (pas de RuntimeError propagee).
#         """
#         self.speak(question)
#         self.speak("Je vous ecoute.")
#         try:
#             return self.listen_chunk(
#                 pause_threshold=1.5,
#                 phrase_time_limit=15,
#                 listen_timeout=timeout,
#             )
#         except RuntimeError as exc:
#             logger.info("listen_short: pas de reponse (%s)", exc)
#             return ""

#     def _transcribe_whisper(self, wav_path: str) -> str:
#         segments_gen, info = self._whisper_model.transcribe(
#             wav_path,
#             language=self.language,
#             beam_size=WHISPER_BEAM_SIZE,
#         )
#         logger.debug(
#             "Whisper: langue=%s (%.0f%%)",
#             info.language, info.language_probability * 100,
#         )
#         text = " ".join(seg.text.strip() for seg in segments_gen).strip()
#         if not text:
#             raise RuntimeError("Whisper n'a produit aucun texte")
#         logger.info("STT chunk: '%s'", text[:100])
#         return text

#     def _transcribe_google(self, audio) -> str:
#         import speech_recognition as sr
#         lang = "fr-FR" if self.language == "fr" else (self.language + "-" + self.language.upper())
#         try:
#             text = self._recognizer.recognize_google(audio, language=lang)
#             logger.info("Google STT: '%s'", text[:100])
#             return text
#         except sr.UnknownValueError:
#             raise RuntimeError("Google STT: audio incomprehensible")
#         except sr.RequestError as exc:
#             raise RuntimeError("Google STT: erreur API: %s" % exc)

#     # ------------------------------------------------------------------
#     # Nettoyage
#     # ------------------------------------------------------------------

#     def close(self) -> None:
#         self._stop_audio()
#         if self._tts_engine is not None:
#             try:
#                 with self._lock_tts:
#                     self._tts_engine.stop()
#             except Exception:
#                 pass
#         logger.info("VoiceIO ferme")


# # ============================================================================
# # VRScenarioApp  -- orchestration principale
# # ============================================================================

# class VRScenarioApp:
#     """
#     Flux en deux phases :

#     PHASE 1 -- Generation et annonce du scenario
#       - Saisie vocale du theme
#       - LLM genere scenario_text + scenario_json structures
#       - Construction du ScenarioSession (signature reelle de vr_scenario_lib)
#       - TTS lit le resume_oral au naturel

#     PHASE 2 -- Questions / Reponses supervisees
#       - L'utilisateur pose des questions librement a voix haute
#       - discuss_scenario() repond via ScenarioSession.history
#       - SupervisorLLM evalue chaque echange : CONTINUER / CONSEIL / STOP
#       - EXIT word : cloture propre
#     """

#     def __init__(self, io: VoiceIO) -> None:
#         self.io = io

#     def run(self) -> None:
#         self._welcome()
#         topic      = self._ask_topic()
#         config     = self._setup_llm()
#         supervisor = SupervisorLLM(config)

#         # -- Phase 1 : generation + annonce --------------------------------
#         scenario_session = self._generate_and_announce(topic, config)

#         # -- Phase 2 : Q&R supervisee --------------------------------------
#         self._qa_loop(scenario_session, supervisor, config)

#         self._goodbye()

#     # ------------------------------------------------------------------
#     # Phase 1 : generation du scenario
#     # ------------------------------------------------------------------

#     def _welcome(self) -> None:
#         print("\n" + "=" * 60)
#         print("  APPLICATION VOCALE -- SCENARIOS VR")
#         print("=" * 60)
#         self.io.speak(
#             "Bienvenue dans l'application vocale de scenarios VR. "
#             "Je vais generer un scenario a partir de votre theme, "
#             "vous en presenter les grandes lignes, "
#             "puis repondre a vos questions. "
#             "Dites fin pour terminer a tout moment."
#         )

#     def _ask_topic(self) -> str:
#         text = self.io.listen_short(
#             "Quel est le theme du scenario VR que vous souhaitez explorer ? "
#             "Par exemple : consignation gaz, securite incendie, premiers secours."
#         )
#         if not text:
#             text = "securite industrielle"
#             self.io.speak("Theme par defaut : securite industrielle.")
#         else:
#             self.io.speak("Theme retenu : " + text + ".")
#         logger.info("Theme : '%s'", text)
#         print("\nTheme : " + text)
#         return text

#     def _generate_and_announce(self, topic: str, config) -> "ScenarioSession | None":
#         """
#         Appelle le LLM pour generer scenario_text + scenario_json,
#         construit un ScenarioSession complet, lit le resume oral.
#         Retourne None si la generation echoue (Q&R desactivee).
#         """
#         self.io.speak("Je genere votre scenario. Patientez quelques instants.")
#         print("\nGeneration en cours...")

#         scenario_json: Dict[str, Any] = {}
#         scenario_text: str = ""

#         # -- Tentative via vr_scenario_lib ----------------------------------
#         try:
#             from vr_scenario_lib.scenario import generate_scenario as lib_generate
#             result = lib_generate(topic=topic, llm_config=config)
#             # lib peut retourner (text, json_dict) ou un objet avec attributs
#             if isinstance(result, tuple):
#                 scenario_text, scenario_json = result[0], result[1]
#             else:
#                 scenario_text = getattr(result, "text", str(result))
#                 scenario_json = getattr(result, "json", {})
#             logger.info("Scenario genere via vr_scenario_lib (%d car.)", len(scenario_text))

#         except Exception as exc:
#             logger.warning("lib generate_scenario indisponible: %s -- fallback LLM direct", exc)
#             scenario_json, scenario_text = self._generate_via_llm(topic, config)

#         if not scenario_json and not scenario_text:
#             self.io.speak(
#                 "La generation du scenario a echoue. "
#                 "Vous pouvez poser vos questions directement."
#             )
#             return None

#         # -- Construction du ScenarioSession --------------------------------
#         now = datetime.now(timezone.utc).isoformat()
#         try:
#             from vr_scenario_lib.scenario_store import ScenarioSession
#             session = ScenarioSession(
#                 scenario_id   = str(uuid.uuid4()),
#                 topic         = topic,
#                 scenario_text = scenario_text,
#                 scenario_json = scenario_json,
#                 created_at    = now,
#                 updated_at    = now,
#             )
#             logger.info("ScenarioSession cree (id=%s)", session.scenario_id)
#         except Exception as exc:
#             logger.warning("ScenarioSession impossible: %s -- session None", exc)
#             session = None

#         # -- Annonce vocale des grandes lignes ------------------------------
#         self._announce_scenario(scenario_json, scenario_text)
#         return session

#     def _generate_via_llm(
#         self, topic: str, config
#     ) -> "tuple[Dict[str, Any], str]":
#         """
#         Appel LLM direct pour generer scenario_json + scenario_text.
#         Retourne ({}, "") en cas d'echec.
#         """
#         if config is None:
#             return self._fallback_static_scenario(topic)

#         user_msg = "Genere un scenario de formation VR sur le theme : " + topic

#         try:
#             raw = self._call_llm_raw(
#                 system    = SCENARIO_GEN_SYSTEM,
#                 user      = user_msg,
#                 config    = config,
#                 max_tokens= SCENARIO_GEN_MAX_TOKENS,
#             )
#         except Exception as exc:
#             logger.error("LLM generation echec: %s", exc)
#             return self._fallback_static_scenario(topic)

#         # Parse JSON
#         try:
#             import re
#             m = re.search(r'\{.*\}', raw, re.DOTALL)
#             if not m:
#                 raise ValueError("JSON introuvable")
#             obj = json.loads(m.group())
#         except Exception as exc:
#             logger.error("Parse JSON scenario echec: %s | raw=%s", exc, raw[:200])
#             return self._fallback_static_scenario(topic)

#         # Construit scenario_text a partir du JSON
#         text = self._json_to_text(obj, topic)
#         return obj, text

#     @staticmethod
#     def _json_to_text(obj: Dict[str, Any], topic: str) -> str:
#         """Serialise scenario_json en texte lisible pour scenario_text."""
#         lines = ["# SCENARIO VR -- " + topic.upper(), ""]
#         titre = obj.get("titre", topic)
#         lines += ["## " + titre, ""]

#         objectifs = obj.get("objectifs", [])
#         if objectifs:
#             lines.append("### Objectifs")
#             for o in objectifs:
#                 lines.append("- " + str(o))
#             lines.append("")

#         for etape in obj.get("grandes_lignes", []):
#             num = etape.get("etape", "")
#             titre_e = etape.get("titre", "")
#             desc = etape.get("description", "")
#             lines.append("### Etape %s : %s" % (num, titre_e))
#             lines.append(desc)
#             lines.append("")

#         procs = obj.get("procedures_cles", [])
#         if procs:
#             lines.append("### Procedures cles")
#             for p in procs:
#                 lines.append("- " + str(p))
#             lines.append("")

#         vigilance = obj.get("points_vigilance", [])
#         if vigilance:
#             lines.append("### Points de vigilance")
#             for v in vigilance:
#                 lines.append("- " + str(v))
#             lines.append("")

#         return "\n".join(lines)

#     @staticmethod
#     def _fallback_static_scenario(topic: str) -> "tuple[Dict[str, Any], str]":
#         """Scenario minimal si le LLM est inaccessible."""
#         obj = {
#             "titre": "Scenario " + topic,
#             "objectifs": [
#                 "Comprendre les principes fondamentaux de " + topic,
#                 "Maitriser les procedures de securite essentielles",
#                 "Reagir correctement aux situations d'urgence",
#             ],
#             "grandes_lignes": [
#                 {"etape": 1, "titre": "Preparation",
#                  "description": "Verifier les equipements et les EPI avant toute intervention."},
#                 {"etape": 2, "titre": "Intervention",
#                  "description": "Appliquer les procedures standard en respectant les consignes."},
#                 {"etape": 3, "titre": "Cloture",
#                  "description": "Consigner les actions effectuees et signaler tout incident."},
#             ],
#             "procedures_cles": [
#                 "Verifier les equipements avant intervention",
#                 "Respecter les zones de securite",
#                 "Alerter la chaine hierarchique en cas d'incident",
#             ],
#             "points_vigilance": [
#                 "Ne jamais intervenir seul",
#                 "Toujours porter les EPI adaptes",
#             ],
#             "resume_oral": (
#                 "Ce scenario porte sur le theme " + topic + ". "
#                 "Il se deroule en trois etapes : la preparation du materiel, "
#                 "l'intervention selon les procedures standard, "
#                 "et la cloture avec consignation des actions effectuees."
#             ),
#         }
#         text = VRScenarioApp._json_to_text(obj, topic)
#         return obj, text

#     def _announce_scenario(self, scenario_json: Dict[str, Any], scenario_text: str) -> None:
#         """Lit les grandes lignes du scenario a voix haute."""
#         print("\n" + "=" * 60)
#         print("  SCENARIO GENERE")
#         print("=" * 60)
#         print(scenario_text[:1200] + ("..." if len(scenario_text) > 1200 else ""))

#         # Lecture TTS du resume_oral (optimise pour TTS, sans listes ni symboles)
#         resume = scenario_json.get("resume_oral", "")
#         if not resume:
#             # Fallback : construit un resume oral minimal depuis le JSON
#             titre = scenario_json.get("titre", "le scenario")
#             etapes = scenario_json.get("grandes_lignes", [])
#             if etapes:
#                 noms = ", ".join(
#                     str(e.get("titre", "")) for e in etapes[:4]
#                 )
#                 resume = (
#                     "Le scenario intitule " + titre + " se deroule en "
#                     + str(len(etapes)) + " etapes : " + noms + "."
#                 )
#             else:
#                 resume = "Le scenario " + titre + " vient d'etre genere."

#         self.io.speak("Voici les grandes lignes de votre scenario.")
#         self.io.speak(resume)

#         # Annonce des points de vigilance s'ils existent
#         vigilance = scenario_json.get("points_vigilance", [])
#         if vigilance:
#             # Construit une phrase fluide (pas de liste TTS)
#             points = " et ".join(vigilance[:3])
#             self.io.speak("Points de vigilance a retenir : " + points + ".")

#         self.io.speak(
#             "Le scenario est pret. "
#             "Vous pouvez maintenant me poser vos questions. "
#             "Dites fin pour terminer."
#         )

#     # ------------------------------------------------------------------
#     # Phase 2 : Q&R supervisee
#     # ------------------------------------------------------------------

#     def _qa_loop(
#         self,
#         scenario_session,   # ScenarioSession | None
#         supervisor: SupervisorLLM,
#         config,
#     ) -> None:
#         """Boucle de questions / reponses supervisees."""
#         print("\n" + "-" * 60)
#         print("[ SESSION Q&R -- posez vos questions ]")
#         print("-" * 60)

#         narrator = NarratorSession(
#             topic = scenario_session.topic if scenario_session else "general"
#         )
#         consecutive_timeouts = 0
#         MAX_TIMEOUTS = 3

#         while True:

#             # ---- 1. Capture de la question --------------------------------
#             self.io.speak("Je vous ecoute.")
#             try:
#                 question = self.io.listen_chunk(
#                     pause_threshold   = STT_SILENCE_TIMEOUT,
#                     phrase_time_limit = STT_PHRASE_TIME_LIMIT,
#                     listen_timeout    = STT_LISTEN_TIMEOUT,
#                 )
#                 consecutive_timeouts = 0
#             except RuntimeError as exc:
#                 consecutive_timeouts += 1
#                 logger.info("Q&R timeout %d/%d: %s", consecutive_timeouts, MAX_TIMEOUTS, exc)
#                 if consecutive_timeouts >= MAX_TIMEOUTS:
#                     if self._ask_continue_qa():
#                         consecutive_timeouts = 0
#                     else:
#                         break
#                 continue

#             # ---- 2. Detection sortie --------------------------------------
#             if any(w in question.lower() for w in EXIT_WORDS):
#                 print("\nSortie Q&R : '%s'" % question)
#                 break

#             print("\n[Question] " + question)
#             narrator.add_chunk(question)

#             # ---- 3. Reponse LLM via ScenarioSession -----------------------
#             answer = self._get_answer(question, scenario_session, config)
#             print("[Reponse] " + answer)
#             self.io.speak(answer)

#             # ---- 4. Supervision de l'echange ------------------------------
#             exchange = "Q : " + question + "\nR : " + answer
#             decision = supervisor.analyse(narrator, exchange)
#             logger.info(
#                 "Superviseur Q&R: %s | '%s'",
#                 decision.decision.value,
#                 decision.message[:60] if decision.message else "",
#             )

#             if decision.decision == Decision.CONSEIL:
#                 print("\n[CONSEIL] " + decision.message)
#                 self.io.speak(decision.message)

#             elif decision.decision == Decision.STOP:
#                 print("\n[STOP] " + decision.message)
#                 self.io.interrupt_and_speak(decision.message)
#                 if not self._handle_stop_qa():
#                     break

#     def _get_answer(self, question: str, scenario_session, config) -> str:
#         """
#         Obtient une reponse LLM a la question posee.
#         Priorite : discuss_scenario() de vr_scenario_lib, puis LLM direct, puis fallback.
#         """
#         # -- Via vr_scenario_lib -------------------------------------------
#         if scenario_session is not None and config is not None:
#             try:
#                 from vr_scenario_lib.scenario import discuss_scenario
#                 reply = discuss_scenario(
#                     session      = scenario_session,
#                     user_message = question,
#                     llm_config   = config,
#                 )
#                 if reply and reply.strip():
#                     return reply.strip()
#             except Exception as exc:
#                 logger.warning("discuss_scenario erreur: %s -- fallback LLM direct", exc)

#         # -- LLM direct avec contexte scenario_text -------------------------
#         if config is not None:
#             context = (
#                 scenario_session.scenario_text[:800]
#                 if scenario_session and scenario_session.scenario_text
#                 else ""
#             )
#             user_msg = (
#                 ("Contexte du scenario :\n" + context + "\n\n" if context else "")
#                 + "Question de l'apprenant : " + question
#             )
#             try:
#                 return self._call_llm_raw(
#                     system    = QA_SYSTEM,
#                     user      = user_msg,
#                     config    = config,
#                     max_tokens= QA_MAX_TOKENS,
#                 ).strip()
#             except Exception as exc:
#                 logger.error("LLM direct Q&R erreur: %s", exc)

#         return "Je n'ai pas pu obtenir de reponse. Consultez la documentation du scenario."

#     # ------------------------------------------------------------------
#     # Helpers generaux
#     # ------------------------------------------------------------------

#     @staticmethod
#     def _call_llm_raw(*, system: str, user: str, config, max_tokens: int) -> str:
#         """Appel LLM unifie : vr_scenario_lib puis HTTP direct (OpenAI-compatible)."""
#         try:
#             from vr_scenario_lib.llm import call_llm
#             return call_llm(
#                 system=system, user=user,
#                 llm_config=config, max_tokens=max_tokens,
#             )
#         except ImportError:
#             pass

#         import urllib.request
#         payload = json.dumps({
#             "model":      getattr(config, "model", "gpt-3.5-turbo"),
#             "max_tokens": max_tokens,
#             "messages":   [
#                 {"role": "system", "content": system},
#                 {"role": "user",   "content": user},
#             ],
#         }).encode()
#         api_url = getattr(config, "api_url", "https://api.openai.com/v1/chat/completions")
#         token   = getattr(config, "token", "")
#         req = urllib.request.Request(
#             api_url, data=payload,
#             headers={
#                 "Content-Type":  "application/json",
#                 "Authorization": "Bearer " + token,
#             },
#         )
#         with urllib.request.urlopen(req, timeout=20) as resp:
#             data = json.loads(resp.read())
#         return data["choices"][0]["message"]["content"]

#     def _ask_continue_qa(self) -> bool:
#         text = self.io.listen_short(
#             "Je n'entends plus rien. "
#             "Avez-vous d'autres questions ? "
#             "Dites oui pour continuer, non pour terminer."
#         )
#         if not text:
#             return False
#         return any(w in text.lower() for w in {"oui", "yes", "continuer", "continue", "si"})

#     def _handle_stop_qa(self) -> bool:
#         """Pause apres STOP en phase Q&R. Retourne True pour reprendre."""
#         self.io.speak(
#             "La session est interrompue. "
#             "Dites reprendre pour continuer, ou fin pour terminer."
#         )
#         text = ""
#         try:
#             text = self.io.listen_chunk(
#                 pause_threshold=2.0,
#                 phrase_time_limit=10,
#                 listen_timeout=12,
#             )
#         except RuntimeError:
#             pass
#         if any(w in text.lower() for w in {"reprendre", "continuer", "oui", "yes"}):
#             self.io.speak("Tres bien. Continuez vos questions.")
#             return True
#         return False

#     def _goodbye(self) -> None:
#         self.io.speak("Merci pour cette session. A bientot !")
#         print("\nAu revoir !\n")

#     # ------------------------------------------------------------------
#     # LLM setup
#     # ------------------------------------------------------------------

#     def _setup_llm(self):
#         try:
#             from vr_scenario_lib.config import build_llm_config
#             return build_llm_config()
#         except Exception as exc:
#             logger.warning(
#                 "LLM config non disponible: %s -- mode degrade (scenarios statiques)", exc
#             )
#             return None


# # ============================================================================
# # CLI
# # ============================================================================

# def _parse_args() -> argparse.Namespace:
#     p = argparse.ArgumentParser(
#         description="Application vocale de supervision de scenarios VR",
#         formatter_class=argparse.ArgumentDefaultsHelpFormatter,
#     )
#     p.add_argument(
#         "--stt-backend", default="whisper", choices=["whisper", "google"],
#         help="Backend STT.",
#     )
#     p.add_argument(
#         "--tts-backend", default=TTS_DEFAULT_BACKEND,
#         choices=["coqui", "piper", "gtts", "pyttsx3"],
#         help="Backend TTS. 'coqui' et 'piper' sont 100%% offline et francais natif.",
#     )
#     p.add_argument(
#         "--language", default="fr",
#         help="Code langue ISO 639-1 (fr par defaut).",
#     )
#     p.add_argument(
#         "--whisper-model", default=WHISPER_DEFAULT_MODEL,
#         choices=["tiny", "base", "small", "medium", "large"],
#         help="Taille du modele Whisper. 'small' recommande pour le francais.",
#     )
#     p.add_argument(
#         "--coqui-model", default=COQUI_MODEL_FR,
#         help="Identifiant modele Coqui TTS.",
#     )
#     p.add_argument(
#         "--piper-model", default=PIPER_MODEL_FR,
#         help="Nom du modele Piper (ex: fr_FR-tom-medium).",
#     )
#     p.add_argument(
#         "--debug", action="store_true",
#         help="Active le logging DEBUG.",
#     )
#     return p.parse_args()


# def main() -> None:
#     args = _parse_args()
#     if args.debug:
#         logging.getLogger().setLevel(logging.DEBUG)

#     io = VoiceIO(
#         stt_backend   = args.stt_backend,
#         tts_backend   = args.tts_backend,
#         language      = args.language,
#         whisper_model = args.whisper_model,
#         coqui_model   = args.coqui_model,
#         piper_model   = args.piper_model,
#     )
#     app = VRScenarioApp(io)
#     try:
#         app.run()
#     except KeyboardInterrupt:
#         print("\nInterruption utilisateur.")
#     finally:
#         io.close()


# if __name__ == "__main__":
#     main()


# #!/usr/bin/env python3
# """
# Application vocale de supervision de scenarios VR.
# Version enterprise -- standards industriels.

# ROLE DE L'APP
# -------------
# L'utilisateur decrit librement un scenario VR a voix haute.
# L'application ecoute en continu, transcrit par chunks VAD, et
# soumet chaque chunk a un LLM superviseur qui peut :
#   - CONTINUER  : ne rien dire (ecoute silencieuse)
#   - CONSEIL    : interrompre poliment pour donner un conseil
#   - STOP       : interrompre fermement pour signaler une erreur critique

# Architecture
# ------------
# VoiceIO          : STT (faster-whisper + SpeechRecognition VAD) + TTS francais natif.
# SupervisorLLM    : analyse chaque chunk, decide CONTINUER / CONSEIL / STOP.
# NarratorSession  : accumule la transcription, maintient le contexte du scenario.
# VRScenarioApp    : orchestration metier (setup + boucle de narration supervisee).

# Backends TTS francais natifs (ordre de priorite automatique)
# ------------------------------------------------------------
# 1. coqui   -- Coqui VITS tts_models/fr/css10/vits  : voix neurale offline, haute qualite
# 2. piper   -- Piper fr_FR-upmc-medium               : voix neurale offline, ultra-rapide
# 3. gtts    -- Google TTS                            : voix cloud, qualite maximale
# 4. pyttsx3 -- espeak-fr                             : synthese basique, zero dependance

# Usage:
#     python app_vocal.py                            # auto-detection meilleur TTS dispo
#     python app_vocal.py --tts-backend coqui        # Coqui VITS (offline, haute qualite)
#     python app_vocal.py --tts-backend piper        # Piper (offline, ultra-rapide)
#     python app_vocal.py --tts-backend gtts         # Google TTS (cloud)
#     python app_vocal.py --stt-backend google       # Google STT (cloud)
#     python app_vocal.py --whisper-model small      # meilleure precision STT
#     python app_vocal.py --debug                    # logs DEBUG complets
# """

# from __future__ import annotations

# import argparse
# import json
# import logging
# import os
# import sys
# import tempfile
# import threading
# import time
# import uuid
# from dataclasses import dataclass, field
# from datetime import datetime, timezone
# from enum import Enum
# from typing import Any, Dict, List, Optional

# # ---------------------------------------------------------------------------
# # Logging
# # ---------------------------------------------------------------------------
# logging.basicConfig(
#     level=logging.INFO,
#     format="%(asctime)s | %(name)-36s | %(levelname)-8s | %(message)s",
#     datefmt="%H:%M:%S",
# )
# logger = logging.getLogger(__name__)

# sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# # ============================================================================
# # Constantes
# # ============================================================================

# STT_LISTEN_TIMEOUT    = 8
# STT_PHRASE_TIME_LIMIT = 20          # duree max d'un chunk narration
# STT_SILENCE_TIMEOUT   = 2.0         # silence VAD -> fin du chunk
# STT_AMBIENT_DURATION  = 0.5
# TTS_SPEECH_RATE       = 145
# TTS_VOLUME            = 0.92
# WHISPER_DEFAULT_MODEL = "base"
# WHISPER_BEAM_SIZE     = 5
# EXIT_WORDS            = {"quitter", "exit", "quit", "au revoir", "stop", "fin"}

# # Backends TTS francais natifs
# TTS_DEFAULT_BACKEND   = "coqui"
# TTS_FALLBACK_CHAIN    = ["coqui", "piper", "gtts", "pyttsx3"]

# # Coqui TTS
# # tts_models/fr/mai/tacotron2-DDC : voix feminine MAI, accent francais metropolitain marque
# # Fallback possible : tts_models/fr/css10/vits (accent neutre)
# COQUI_MODEL_FR        = "tts_models/fr/mai/tacotron2-DDC"
# COQUI_SAMPLE_RATE     = 22050

# # Piper TTS
# # fr_FR-tom-medium : voix masculine Tom, accent francais metropolitain naturel
# # Fallback possible : fr_FR-upmc-medium (accent neutre universitaire)
# PIPER_MODEL_FR        = "fr_FR-tom-medium"
# PIPER_SAMPLE_RATE     = 22050

# # Supervisor LLM
# SUPERVISOR_MAX_TOKENS = 256
# SUPERVISOR_SYSTEM = (
#     "Tu es un superviseur expert en securite VR et en procedures industrielles. "
#     "L'utilisateur decrit a voix haute un scenario de formation VR. "
#     "Tu recois des fragments de sa narration en temps reel.\n\n"
#     "Analyse le dernier fragment dans son contexte et reponds UNIQUEMENT avec un objet JSON :\n"
#     '{"decision": "CONTINUER" | "CONSEIL" | "STOP", "message": "<texte a dire, vide si CONTINUER>"}\n\n'
#     "Regles strictes :\n"
#     "- CONTINUER  : narration correcte, coherente, sans danger. Message vide obligatoire.\n"
#     "- CONSEIL    : amelioration possible. Message court, positif, actionnable. Max 2 phrases.\n"
#     "- STOP       : erreur critique de procedure, danger reel, incoherence grave. "
#     "Message direct et precis. Commence par 'Attention : '.\n"
#     "Ne jamais inventer de contexte non mentionne. Rester factuel."
# )

# # Scenario generation LLM
# SCENARIO_GEN_MAX_TOKENS = 1024
# SCENARIO_GEN_SYSTEM = (
#     "Tu es un expert en conception de scenarios de formation VR industrielle. "
#     "A partir d'un theme, genere un scenario structure en JSON UNIQUEMENT, sans aucun texte avant ou apres.\n\n"
#     "Format JSON attendu (respecte exactement ces cles) :\n"
#     '{\n'
#     '  "titre": "Titre court du scenario",\n'
#     '  "objectifs": ["objectif 1", "objectif 2", "objectif 3"],\n'
#     '  "grandes_lignes": [\n'
#     '    {"etape": 1, "titre": "Titre etape", "description": "Description concise"},\n'
#     '    ...\n'
#     '  ],\n'
#     '  "procedures_cles": ["procedure 1", "procedure 2"],\n'
#     '  "points_vigilance": ["point 1", "point 2"],\n'
#     '  "resume_oral": "Texte fluide de 3-4 phrases pour lecture TTS. Pas de liste, pas de symboles."\n'
#     '}\n\n'
#     "Le champ resume_oral doit etre lisible a voix haute sans accroc : pas de tirets, "
#     "pas de parentheses, pas d'abreviations. Maximum 4 phrases."
# )

# # Q&R supervisee
# QA_MAX_TOKENS = 512
# QA_SYSTEM = (
#     "Tu es un formateur expert qui aide un apprenant a comprendre un scenario de formation VR. "
#     "Tu reponds aux questions en te basant exclusivement sur le scenario fourni. "
#     "Tes reponses sont courtes (2-3 phrases maximum), claires, et adaptees a une lecture TTS : "
#     "pas de listes, pas de tirets, pas de symboles. Parle directement a l'apprenant."
# )


# # ============================================================================
# # Decision + NarratorSession
# # ============================================================================

# class Decision(Enum):
#     CONTINUER = "CONTINUER"
#     CONSEIL   = "CONSEIL"
#     STOP      = "STOP"


# @dataclass
# class SupervisorDecision:
#     decision: Decision = Decision.CONTINUER
#     message:  str      = ""

#     def must_speak(self) -> bool:
#         return self.decision in (Decision.CONSEIL, Decision.STOP)


# @dataclass
# class NarratorSession:
#     """Accumule la transcription et maintient le contexte pour le LLM."""
#     topic:     str
#     chunks:    List[str] = field(default_factory=list)
#     full_text: str       = ""

#     def add_chunk(self, text: str) -> None:
#         self.chunks.append(text)
#         self.full_text = " ".join(self.chunks)

#     def context_window(self, n: int = 5) -> str:
#         return " ".join(self.chunks[-n:])

#     def summary(self) -> str:
#         return "%d sequence(s), ~%d mots" % (len(self.chunks), len(self.full_text.split()))


# # ============================================================================
# # SupervisorLLM
# # ============================================================================

# class SupervisorLLM:
#     """Analyse les chunks de narration et produit des decisions superviseur."""

#     def __init__(self, config) -> None:
#         self._config = config
#         self._lock   = threading.Lock()

#     def analyse(self, session: NarratorSession, new_chunk: str) -> SupervisorDecision:
#         if self._config is None:
#             return SupervisorDecision()

#         user_msg = (
#             "Theme du scenario : %s\n\n"
#             "Contexte (narration precedente) :\n%s\n\n"
#             "Nouveau fragment :\n%s"
#         ) % (session.topic, session.context_window(), new_chunk)

#         try:
#             with self._lock:
#                 raw = self._call_llm(user_msg)
#             return self._parse(raw)
#         except Exception as exc:
#             logger.warning("SupervisorLLM erreur: %s", exc)
#             return SupervisorDecision()

#     def _call_llm(self, user_msg: str) -> str:
#         # Tentative via vr_scenario_lib
#         try:
#             from vr_scenario_lib.llm import call_llm
#             return call_llm(
#                 system=SUPERVISOR_SYSTEM,
#                 user=user_msg,
#                 llm_config=self._config,
#                 max_tokens=SUPERVISOR_MAX_TOKENS,
#             )
#         except ImportError:
#             pass

#         # Fallback HTTP direct (OpenAI-compatible)
#         import json
#         import urllib.request

#         payload = json.dumps({
#             "model":      getattr(self._config, "model", "gpt-3.5-turbo"),
#             "max_tokens": SUPERVISOR_MAX_TOKENS,
#             "messages":   [
#                 {"role": "system", "content": SUPERVISOR_SYSTEM},
#                 {"role": "user",   "content": user_msg},
#             ],
#         }).encode()
#         api_url = getattr(self._config, "api_url", "https://api.openai.com/v1/chat/completions")
#         token   = getattr(self._config, "token", "")
#         req = urllib.request.Request(
#             api_url,
#             data=payload,
#             headers={
#                 "Content-Type":  "application/json",
#                 "Authorization": "Bearer " + token,
#             },
#         )
#         with urllib.request.urlopen(req, timeout=15) as resp:
#             data = json.loads(resp.read())
#         return data["choices"][0]["message"]["content"]

#     def _parse(self, raw: str) -> SupervisorDecision:
#         import json
#         import re
#         m = re.search(r'\{.*\}', raw, re.DOTALL)
#         if not m:
#             logger.warning("SupervisorLLM: JSON introuvable dans '%s'", raw[:120])
#             return SupervisorDecision()
#         obj = json.loads(m.group())
#         try:
#             dec = Decision(obj.get("decision", "CONTINUER").upper())
#         except ValueError:
#             dec = Decision.CONTINUER
#         return SupervisorDecision(decision=dec, message=obj.get("message", "").strip())


# # ============================================================================
# # VoiceIO
# # ============================================================================

# class VoiceIO:
#     """Couche bas-niveau STT + TTS.

#     Regles fondamentales
#     --------------------
#     1. speak() est TOUJOURS bloquant dans le flux principal.
#        Un TTS non-bloquant avant listen() = echo capture par Whisper.
#     2. Le micro n'est jamais ouvert pendant la synthese vocale.
#     3. L'enregistrement utilise la VAD (SpeechRecognition), pas une duree fixe.
#     4. interrupt_and_speak() coupe l'audio en cours avant de parler (STOP urgents).
#     """

#     def __init__(
#         self,
#         stt_backend:   str = "whisper",
#         tts_backend:   str = TTS_DEFAULT_BACKEND,
#         language:      str = "fr",
#         whisper_model: str = WHISPER_DEFAULT_MODEL,
#         coqui_model:   str = COQUI_MODEL_FR,
#         piper_model:   str = PIPER_MODEL_FR,
#     ) -> None:
#         self.stt_backend      = stt_backend
#         self.tts_backend      = tts_backend
#         self.language         = language
#         self.whisper_model_id = whisper_model
#         self.coqui_model_id   = coqui_model
#         self.piper_model_id   = piper_model

#         self._recognizer    = None
#         self._whisper_model = None
#         self._tts_engine    = None
#         self._coqui_model   = None
#         self._lock_tts      = threading.Lock()

#         self._init()

#     # ------------------------------------------------------------------
#     # Init
#     # ------------------------------------------------------------------

#     def _init(self) -> None:
#         self._init_stt()
#         self._init_tts()
#         logger.info(
#             "VoiceIO pret -- STT: %s | TTS: %s | Langue: %s",
#             self.stt_backend, self.tts_backend, self.language,
#         )

#     def _init_stt(self) -> None:
#         try:
#             import speech_recognition as sr
#             self._recognizer = sr.Recognizer()
#             self._recognizer.energy_threshold         = 4000
#             self._recognizer.pause_threshold          = STT_SILENCE_TIMEOUT
#             self._recognizer.dynamic_energy_threshold = True
#         except ImportError:
#             raise RuntimeError(
#                 "SpeechRecognition manquant. pip install SpeechRecognition PyAudio"
#             )
#         if self.stt_backend == "whisper":
#             self._whisper_model = self._load_whisper()

#     def _load_whisper(self) -> object:
#         try:
#             from faster_whisper import WhisperModel
#             logger.info("Chargement faster-whisper '%s'...", self.whisper_model_id)
#             model = WhisperModel(
#                 self.whisper_model_id,
#                 device="cpu",
#                 compute_type="int8",
#             )
#             logger.info("faster-whisper pret")
#             return model
#         except ImportError:
#             raise RuntimeError("faster-whisper manquant. pip install faster-whisper")

#     def _init_tts(self) -> None:
#         chain = (
#             [self.tts_backend]
#             + [b for b in TTS_FALLBACK_CHAIN if b != self.tts_backend]
#         )
#         for backend in chain:
#             try:
#                 if backend == "coqui":
#                     self._init_coqui()
#                 elif backend == "piper":
#                     self._init_piper()
#                 elif backend == "gtts":
#                     self._init_gtts()
#                 elif backend == "pyttsx3":
#                     self._init_pyttsx3()
#                 else:
#                     continue
#                 self.tts_backend = backend
#                 logger.info("TTS backend actif : %s", backend)
#                 return
#             except Exception as exc:
#                 logger.warning(
#                     "TTS backend '%s' indisponible: %s -- essai suivant", backend, exc
#                 )

#         raise RuntimeError(
#             "Aucun backend TTS disponible. "
#             "Installez au moins : pip install coqui-tts sounddevice soundfile"
#         )

#     # ------------------------------------------------------------------
#     # Init Coqui VITS -- voix neurale francaise offline
#     # ------------------------------------------------------------------

#     def _init_coqui(self) -> None:
#         try:
#             from TTS.api import TTS as CoquiTTS
#             import sounddevice  # noqa: F401
#             import soundfile    # noqa: F401
#         except ImportError:
#             raise RuntimeError(
#                 "Coqui TTS manquant. pip install coqui-tts sounddevice soundfile"
#             )
#         logger.info("Chargement Coqui TTS '%s'...", self.coqui_model_id)
#         self._coqui_model = CoquiTTS(
#             model_name=self.coqui_model_id,
#             progress_bar=False,
#             gpu=False,
#         )
#         logger.info("Coqui TTS pret (fr/css10/vits)")

#     # ------------------------------------------------------------------
#     # Init Piper -- voix neurale francaise offline, ultra-rapide
#     # ------------------------------------------------------------------

#     def _init_piper(self) -> None:
#         try:
#             import piper  # noqa: F401
#         except ImportError:
#             raise RuntimeError("piper-tts manquant. pip install piper-tts")
#         logger.info("Piper TTS disponible -- modele '%s'", self.piper_model_id)

#     # ------------------------------------------------------------------
#     # Init gTTS -- Google TTS cloud
#     # ------------------------------------------------------------------

#     def _init_gtts(self) -> None:
#         try:
#             import gtts    # noqa: F401
#             import pygame  # noqa: F401
#         except ImportError:
#             raise RuntimeError("gTTS/pygame manquants. pip install gTTS pygame")
#         logger.info("gTTS cloud initialise")

#     # ------------------------------------------------------------------
#     # Init pyttsx3 -- fallback ultime espeak
#     # ------------------------------------------------------------------

#     def _init_pyttsx3(self) -> None:
#         try:
#             import pyttsx3
#         except ImportError:
#             raise RuntimeError("pyttsx3 manquant. pip install pyttsx3")

#         engine = pyttsx3.init()
#         engine.setProperty("rate",   TTS_SPEECH_RATE)
#         engine.setProperty("volume", TTS_VOLUME)

#         fr_voice_found = False
#         # Priorite 1 : fr_FR espeak-ng (accent francais metropolitain pur)
#         # Priorite 2 : toute voix contenant "french" ou "fr" dans le nom/id
#         for priority in ("fr_FR", "fr-FR", "french", "fr"):
#             for v in engine.getProperty("voices"):
#                 name_lower = v.name.lower()
#                 id_lower   = v.id.lower()
#                 if priority.lower() in id_lower or priority.lower() in name_lower:
#                     engine.setProperty("voice", v.id)
#                     logger.info("pyttsx3 voix francaise selectionnee : %s (%s)", v.name, v.id)
#                     fr_voice_found = True
#                     break
#             if fr_voice_found:
#                 break

#         if not fr_voice_found:
#             logger.warning(
#                 "Aucune voix francaise trouvee dans pyttsx3. "
#                 "Linux: sudo apt install espeak-ng-data"
#             )

#         self._tts_engine = engine
#         logger.info("pyttsx3 initialise (voix systeme)")

#     # ------------------------------------------------------------------
#     # TTS -- TOUJOURS bloquant dans le flux principal
#     # ------------------------------------------------------------------

#     def interrupt_and_speak(self, text: str) -> None:
#         """Coupe l'audio en cours PUIS parle. Reserve aux STOP urgents."""
#         self._stop_audio()
#         self.speak(text)

#     def _stop_audio(self) -> None:
#         """Arrete immediatement la lecture audio (tous backends)."""
#         try:
#             if self.tts_backend in ("coqui", "piper"):
#                 import sounddevice as sd
#                 sd.stop()
#             elif self.tts_backend == "gtts":
#                 try:
#                     import pygame
#                     if pygame.mixer.get_init():
#                         pygame.mixer.music.stop()
#                 except Exception:
#                     pass
#         except Exception as exc:
#             logger.debug("_stop_audio: %s", exc)

#     @staticmethod
#     def _sanitize_tts(text: str) -> str:
#         """Supprime les caracteres non oraux avant synthese vocale.

#         Regles appliquees dans l'ordre :
#         1. Blocs code Markdown (``` ... ```) -> supprimes
#         2. Emphase Markdown (* ** _ __ ~ ~~) -> supprimes (le texte reste)
#         3. Titres Markdown (# ## ###...)     -> supprimes (le texte reste)
#         4. URLs (http/https/ftp)             -> remplacees par 'lien'
#         5. Ponctuation non orale             -> remplacee ou supprimee
#         6. Espaces multiples / lignes vides  -> normalises
#         """
#         import re

#         # 1. Blocs code (``` ... ```) et code inline (` ... `)
#         text = re.sub(r'```.*?```', '', text, flags=re.DOTALL)
#         text = re.sub(r'`[^`]*`', '', text)

#         # 2. Emphase Markdown : **, *, __, _, ~~, ~
#         text = re.sub(r'\*{1,3}|_{1,3}|~{1,2}', '', text)

#         # 3. Titres Markdown : # au debut d'une ligne
#         text = re.sub(r'^\s*#{1,6}\s*', '', text, flags=re.MULTILINE)

#         # 4. URLs
#         text = re.sub(r'https?://\S+|ftp://\S+', 'lien', text)

#         # 5. Ponctuation non orale
#         #    - Tirets de liste en debut de ligne -> supprimes
#         text = re.sub(r'^\s*[-•–—]\s+', '', text, flags=re.MULTILINE)
#         #    - Lignes separateurs de tableaux Markdown (---|--- etc.)
#         text = re.sub(r'^\s*[\-|: ]{3,}\s*$', '', text, flags=re.MULTILINE)
#         #    - Barres verticales (tableaux Markdown)
#         text = re.sub(r'\|', ' ', text)
#         #    - Caracteres vraiment non oraux : \ / @ # $ % ^ & { } [ ] < > =
#         text = re.sub(r'[\\/@#$%^&{}\[\]<>=]', ' ', text)
#         #    - Parentheses et crochets : garder le contenu, supprimer les delimiteurs
#         text = re.sub(r'[(){}\[\]]', ' ', text)
#         #    - Points de suspension : remplacer par une virgule (pause naturelle)
#         text = re.sub(r'\.{2,}', ',', text)
#         #    - Tirets en milieu de phrase (em-dash, en-dash) -> virgule
#         text = re.sub(r'\s*[–—]\s*', ', ', text)
#         #    - Astérisques restants
#         text = re.sub(r'\*+', '', text)
#         #    - Underscores restants
#         text = re.sub(r'_+', ' ', text)

#         # 6. Normalisation des espaces et sauts de ligne
#         text = re.sub(r'\n+', ' ', text)
#         text = re.sub(r' {2,}', ' ', text)

#         return text.strip()

#     def speak(self, text: str, *, blocking: bool = True) -> None:
#         """Synthese vocale en francais natif.

#         blocking=True (defaut) : retourne APRES la fin de la lecture.
#         blocking=False         : usage exceptionnel uniquement.
#         REGLE : ne JAMAIS appeler avec blocking=False avant listen().
#         """
#         if not text or not text.strip():
#             return
#         text = self._sanitize_tts(text)
#         if not text:
#             return
#         logger.info("TTS [%s]: '%s'", self.tts_backend, text[:80])

#         dispatch = {
#             "coqui":   self._speak_coqui,
#             "piper":   self._speak_piper,
#             "gtts":    self._speak_gtts,
#             "pyttsx3": self._speak_pyttsx3,
#         }
#         fn = dispatch.get(self.tts_backend)
#         if fn is None:
#             logger.error("Backend TTS inconnu: %s", self.tts_backend)
#             print("[TTS] " + text)
#             return
#         fn(text, blocking)

#     # ------------------------------------------------------------------
#     # _speak_coqui : Coqui VITS fr/css10 -- reference qualite
#     # ------------------------------------------------------------------

#     def _speak_coqui(self, text: str, blocking: bool) -> None:
#         tmp_path: Optional[str] = None
#         try:
#             import soundfile as sf
#             import sounddevice as sd

#             with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
#                 tmp_path = f.name

#             with self._lock_tts:
#                 self._coqui_model.tts_to_file(text=text, file_path=tmp_path)

#             data, sr = sf.read(tmp_path, dtype="float32")
#             if blocking:
#                 sd.play(data, sr)
#                 sd.wait()
#             else:
#                 sd.play(data, sr)

#         except Exception as exc:
#             logger.error("Coqui TTS erreur: %s", exc)
#             print("[TTS] " + text)
#         finally:
#             if tmp_path and os.path.exists(tmp_path):
#                 try:
#                     os.unlink(tmp_path)
#                 except OSError:
#                     pass

#     # ------------------------------------------------------------------
#     # _speak_piper : Piper fr_FR-upmc -- latence minimale
#     # ------------------------------------------------------------------

#     def _speak_piper(self, text: str, blocking: bool) -> None:
#         tmp_path: Optional[str] = None
#         try:
#             import subprocess
#             import soundfile as sf
#             import sounddevice as sd

#             with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
#                 tmp_path = f.name

#             result = subprocess.run(
#                 ["piper", "--model", self.piper_model_id, "--output_file", tmp_path],
#                 input=text.encode("utf-8"),
#                 capture_output=True,
#                 timeout=30,
#             )
#             if result.returncode != 0:
#                 raise RuntimeError(
#                     "piper returncode=%d: %s" % (result.returncode, result.stderr.decode())
#                 )

#             data, sr = sf.read(tmp_path, dtype="float32")
#             if blocking:
#                 sd.play(data, sr)
#                 sd.wait()
#             else:
#                 sd.play(data, sr)

#         except FileNotFoundError:
#             logger.error("Executable 'piper' introuvable. pip install piper-tts")
#             print("[TTS] " + text)
#         except Exception as exc:
#             logger.error("Piper TTS erreur: %s", exc)
#             print("[TTS] " + text)
#         finally:
#             if tmp_path and os.path.exists(tmp_path):
#                 try:
#                     os.unlink(tmp_path)
#                 except OSError:
#                     pass

#     # ------------------------------------------------------------------
#     # _speak_gtts : Google TTS cloud
#     # Bug corrige : mixer reinitialise a chaque appel (non-reentrant).
#     # ------------------------------------------------------------------

#     def _speak_gtts(self, text: str, blocking: bool) -> None:
#         tmp_path: Optional[str] = None
#         try:
#             from gtts import gTTS
#             import pygame

#             tts = gTTS(text=text, lang=self.language, slow=False)
#             with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
#                 tmp_path = f.name
#             tts.save(tmp_path)

#             # Reinitialisation propre du mixer a chaque appel
#             if pygame.mixer.get_init():
#                 pygame.mixer.quit()
#             pygame.mixer.init(frequency=22050, size=-16, channels=1, buffer=512)
#             pygame.mixer.music.load(tmp_path)
#             pygame.mixer.music.play()

#             if blocking:
#                 while pygame.mixer.music.get_busy():
#                     time.sleep(0.05)
#                 pygame.mixer.quit()

#         except Exception as exc:
#             logger.error("gTTS erreur: %s", exc)
#             print("[TTS] " + text)
#         finally:
#             if tmp_path and os.path.exists(tmp_path):
#                 try:
#                     time.sleep(0.1)   # libere le handle fichier
#                     os.unlink(tmp_path)
#                 except OSError:
#                     pass

#     # ------------------------------------------------------------------
#     # _speak_pyttsx3 : espeak fallback ultime
#     # ------------------------------------------------------------------

#     def _speak_pyttsx3(self, text: str, blocking: bool) -> None:
#         with self._lock_tts:
#             try:
#                 self._tts_engine.say(text)
#                 if blocking:
#                     self._tts_engine.runAndWait()
#                 else:
#                     # NOTE : non-bloquant uniquement si explicitement demande.
#                     # Ne jamais appeler avant listen() -- race condition micro.
#                     t = threading.Thread(
#                         target=self._tts_engine.runAndWait, daemon=True
#                     )
#                     t.start()
#             except Exception as exc:
#                 logger.error("pyttsx3 erreur: %s", exc)
#                 print("[TTS] " + text)

#     # ------------------------------------------------------------------
#     # STT -- chunk VAD (narration continue)
#     # ------------------------------------------------------------------

#     def listen_chunk(
#         self,
#         *,
#         pause_threshold:   float = STT_SILENCE_TIMEOUT,
#         phrase_time_limit: int   = STT_PHRASE_TIME_LIMIT,
#         listen_timeout:    float = STT_LISTEN_TIMEOUT,
#     ) -> str:
#         """Capture un chunk de parole (VAD) et transcrit.

#         Returns:
#             Texte transcrit non-vide.

#         Raises:
#             RuntimeError: Capture ou transcription impossible.
#         """
#         import speech_recognition as sr

#         original = self._recognizer.pause_threshold
#         self._recognizer.pause_threshold = pause_threshold
#         tmp_path: Optional[str] = None

#         try:
#             with sr.Microphone() as src:
#                 logger.info(
#                     "Ecoute chunk (silence=%.1fs, max=%ds)...",
#                     pause_threshold, phrase_time_limit,
#                 )
#                 self._recognizer.adjust_for_ambient_noise(src, duration=STT_AMBIENT_DURATION)
#                 audio = self._recognizer.listen(
#                     src,
#                     timeout=listen_timeout,
#                     phrase_time_limit=phrase_time_limit,
#                 )

#             with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
#                 tmp_path = f.name
#                 f.write(audio.get_wav_data())

#             if self.stt_backend == "whisper":
#                 return self._transcribe_whisper(tmp_path)
#             else:
#                 return self._transcribe_google(audio)

#         finally:
#             self._recognizer.pause_threshold = original
#             if tmp_path and os.path.exists(tmp_path):
#                 try:
#                     os.unlink(tmp_path)
#                 except OSError:
#                     pass

#     def listen_short(self, question: str, timeout: float = 8.0) -> str:
#         """Pose une question courte et attend une reponse breve.
#         Retourne la chaine vide en cas d'echec (pas de RuntimeError propagee).
#         """
#         self.speak(question)
#         self.speak("Je vous ecoute.")
#         try:
#             return self.listen_chunk(
#                 pause_threshold=1.5,
#                 phrase_time_limit=15,
#                 listen_timeout=timeout,
#             )
#         except RuntimeError as exc:
#             logger.info("listen_short: pas de reponse (%s)", exc)
#             return ""

#     def _transcribe_whisper(self, wav_path: str) -> str:
#         segments_gen, info = self._whisper_model.transcribe(
#             wav_path,
#             language=self.language,
#             beam_size=WHISPER_BEAM_SIZE,
#         )
#         logger.debug(
#             "Whisper: langue=%s (%.0f%%)",
#             info.language, info.language_probability * 100,
#         )
#         text = " ".join(seg.text.strip() for seg in segments_gen).strip()
#         if not text:
#             raise RuntimeError("Whisper n'a produit aucun texte")
#         logger.info("STT chunk: '%s'", text[:100])
#         return text

#     def _transcribe_google(self, audio) -> str:
#         import speech_recognition as sr
#         lang = "fr-FR" if self.language == "fr" else (self.language + "-" + self.language.upper())
#         try:
#             text = self._recognizer.recognize_google(audio, language=lang)
#             logger.info("Google STT: '%s'", text[:100])
#             return text
#         except sr.UnknownValueError:
#             raise RuntimeError("Google STT: audio incomprehensible")
#         except sr.RequestError as exc:
#             raise RuntimeError("Google STT: erreur API: %s" % exc)

#     # ------------------------------------------------------------------
#     # Nettoyage
#     # ------------------------------------------------------------------

#     def close(self) -> None:
#         self._stop_audio()
#         if self._tts_engine is not None:
#             try:
#                 with self._lock_tts:
#                     self._tts_engine.stop()
#             except Exception:
#                 pass
#         logger.info("VoiceIO ferme")


# # ============================================================================
# # VRScenarioApp  -- orchestration principale
# # ============================================================================

# class VRScenarioApp:
#     """
#     Flux en deux phases :

#     PHASE 1 -- Generation et annonce du scenario
#       - Saisie vocale du theme
#       - LLM genere scenario_text + scenario_json structures
#       - Construction du ScenarioSession (signature reelle de vr_scenario_lib)
#       - TTS lit le resume_oral au naturel

#     PHASE 2 -- Questions / Reponses supervisees
#       - L'utilisateur pose des questions librement a voix haute
#       - discuss_scenario() repond via ScenarioSession.history
#       - SupervisorLLM evalue chaque echange : CONTINUER / CONSEIL / STOP
#       - EXIT word : cloture propre
#     """

#     def __init__(self, io: VoiceIO) -> None:
#         self.io = io

#     def run(self) -> None:
#         self._welcome()
#         topic      = self._ask_topic()
#         config     = self._setup_llm()
#         supervisor = SupervisorLLM(config)

#         # -- Phase 1 : generation + annonce --------------------------------
#         scenario_session = self._generate_and_announce(topic, config)

#         # -- Phase 2 : Q&R supervisee --------------------------------------
#         self._qa_loop(scenario_session, supervisor, config)

#         self._goodbye()

#     # ------------------------------------------------------------------
#     # Phase 1 : generation du scenario
#     # ------------------------------------------------------------------

#     def _welcome(self) -> None:
#         print("\n" + "=" * 60)
#         print("  APPLICATION VOCALE -- SCENARIOS VR")
#         print("=" * 60)
#         self.io.speak(
#             "Bienvenue dans l'application vocale de scenarios VR. "
#             "Je vais generer un scenario a partir de votre theme, "
#             "vous en presenter les grandes lignes, "
#             "puis repondre a vos questions. "
#             "Dites fin pour terminer a tout moment."
#         )

#     def _ask_topic(self) -> str:
#         text = self.io.listen_short(
#             "Quel est le theme du scenario VR que vous souhaitez explorer ? "
#             "Par exemple : consignation gaz, securite incendie, premiers secours."
#         )
#         if not text:
#             text = "securite industrielle"
#             self.io.speak("Theme par defaut : securite industrielle.")
#         else:
#             self.io.speak("Theme retenu : " + text + ".")
#         logger.info("Theme : '%s'", text)
#         print("\nTheme : " + text)
#         return text

#     def _generate_and_announce(self, topic: str, config) -> "ScenarioSession | None":
#         """
#         Appelle le LLM pour generer scenario_text + scenario_json,
#         construit un ScenarioSession complet, lit le resume oral.
#         Retourne None si la generation echoue (Q&R desactivee).
#         """
#         self.io.speak("Je genere votre scenario. Patientez quelques instants.")
#         print("\nGeneration en cours...")

#         scenario_json: Dict[str, Any] = {}
#         scenario_text: str = ""

#         # -- Tentative via vr_scenario_lib ----------------------------------
#         try:
#             from vr_scenario_lib.scenario import generate_scenario as lib_generate
#             result = lib_generate(topic=topic, llm_config=config)
#             # lib peut retourner (text, json_dict) ou un objet avec attributs
#             if isinstance(result, tuple):
#                 scenario_text, scenario_json = result[0], result[1]
#             else:
#                 scenario_text = getattr(result, "text", str(result))
#                 scenario_json = getattr(result, "json", {})
#             logger.info("Scenario genere via vr_scenario_lib (%d car.)", len(scenario_text))

#         except Exception as exc:
#             logger.warning("lib generate_scenario indisponible: %s -- fallback LLM direct", exc)
#             scenario_json, scenario_text = self._generate_via_llm(topic, config)

#         if not scenario_json and not scenario_text:
#             self.io.speak(
#                 "La generation du scenario a echoue. "
#                 "Vous pouvez poser vos questions directement."
#             )
#             return None

#         # -- Construction du ScenarioSession --------------------------------
#         now = datetime.now(timezone.utc).isoformat()
#         try:
#             from vr_scenario_lib.scenario_store import ScenarioSession
#             session = ScenarioSession(
#                 scenario_id   = str(uuid.uuid4()),
#                 topic         = topic,
#                 scenario_text = scenario_text,
#                 scenario_json = scenario_json,
#                 created_at    = now,
#                 updated_at    = now,
#             )
#             logger.info("ScenarioSession cree (id=%s)", session.scenario_id)
#         except Exception as exc:
#             logger.warning("ScenarioSession impossible: %s -- session None", exc)
#             session = None

#         # -- Annonce vocale des grandes lignes ------------------------------
#         self._announce_scenario(scenario_json, scenario_text)
#         return session

#     def _generate_via_llm(
#         self, topic: str, config
#     ) -> "tuple[Dict[str, Any], str]":
#         """
#         Appel LLM direct pour generer scenario_json + scenario_text.
#         Retourne ({}, "") en cas d'echec.
#         """
#         if config is None:
#             return self._fallback_static_scenario(topic)

#         user_msg = "Genere un scenario de formation VR sur le theme : " + topic

#         try:
#             raw = self._call_llm_raw(
#                 system    = SCENARIO_GEN_SYSTEM,
#                 user      = user_msg,
#                 config    = config,
#                 max_tokens= SCENARIO_GEN_MAX_TOKENS,
#             )
#         except Exception as exc:
#             logger.error("LLM generation echec: %s", exc)
#             return self._fallback_static_scenario(topic)

#         # Parse JSON
#         try:
#             import re
#             m = re.search(r'\{.*\}', raw, re.DOTALL)
#             if not m:
#                 raise ValueError("JSON introuvable")
#             obj = json.loads(m.group())
#         except Exception as exc:
#             logger.error("Parse JSON scenario echec: %s | raw=%s", exc, raw[:200])
#             return self._fallback_static_scenario(topic)

#         # Construit scenario_text a partir du JSON
#         text = self._json_to_text(obj, topic)
#         return obj, text

#     @staticmethod
#     def _json_to_text(obj: Dict[str, Any], topic: str) -> str:
#         """Serialise scenario_json en texte lisible pour scenario_text."""
#         lines = ["# SCENARIO VR -- " + topic.upper(), ""]
#         titre = obj.get("titre", topic)
#         lines += ["## " + titre, ""]

#         objectifs = obj.get("objectifs", [])
#         if objectifs:
#             lines.append("### Objectifs")
#             for o in objectifs:
#                 lines.append("- " + str(o))
#             lines.append("")

#         for etape in obj.get("grandes_lignes", []):
#             num = etape.get("etape", "")
#             titre_e = etape.get("titre", "")
#             desc = etape.get("description", "")
#             lines.append("### Etape %s : %s" % (num, titre_e))
#             lines.append(desc)
#             lines.append("")

#         procs = obj.get("procedures_cles", [])
#         if procs:
#             lines.append("### Procedures cles")
#             for p in procs:
#                 lines.append("- " + str(p))
#             lines.append("")

#         vigilance = obj.get("points_vigilance", [])
#         if vigilance:
#             lines.append("### Points de vigilance")
#             for v in vigilance:
#                 lines.append("- " + str(v))
#             lines.append("")

#         return "\n".join(lines)

#     @staticmethod
#     def _fallback_static_scenario(topic: str) -> "tuple[Dict[str, Any], str]":
#         """Scenario minimal si le LLM est inaccessible."""
#         obj = {
#             "titre": "Scenario " + topic,
#             "objectifs": [
#                 "Comprendre les principes fondamentaux de " + topic,
#                 "Maitriser les procedures de securite essentielles",
#                 "Reagir correctement aux situations d'urgence",
#             ],
#             "grandes_lignes": [
#                 {"etape": 1, "titre": "Preparation",
#                  "description": "Verifier les equipements et les EPI avant toute intervention."},
#                 {"etape": 2, "titre": "Intervention",
#                  "description": "Appliquer les procedures standard en respectant les consignes."},
#                 {"etape": 3, "titre": "Cloture",
#                  "description": "Consigner les actions effectuees et signaler tout incident."},
#             ],
#             "procedures_cles": [
#                 "Verifier les equipements avant intervention",
#                 "Respecter les zones de securite",
#                 "Alerter la chaine hierarchique en cas d'incident",
#             ],
#             "points_vigilance": [
#                 "Ne jamais intervenir seul",
#                 "Toujours porter les EPI adaptes",
#             ],
#             "resume_oral": (
#                 "Ce scenario porte sur le theme " + topic + ". "
#                 "Il se deroule en trois etapes : la preparation du materiel, "
#                 "l'intervention selon les procedures standard, "
#                 "et la cloture avec consignation des actions effectuees."
#             ),
#         }
#         text = VRScenarioApp._json_to_text(obj, topic)
#         return obj, text

#     def _announce_scenario(self, scenario_json: Dict[str, Any], scenario_text: str) -> None:
#         """Lit les grandes lignes du scenario a voix haute."""
#         print("\n" + "=" * 60)
#         print("  SCENARIO GENERE")
#         print("=" * 60)
#         print(scenario_text[:1200] + ("..." if len(scenario_text) > 1200 else ""))

#         # Lecture TTS du resume_oral (optimise pour TTS, sans listes ni symboles)
#         resume = scenario_json.get("resume_oral", "")
#         if not resume:
#             # Fallback : construit un resume oral minimal depuis le JSON
#             titre = scenario_json.get("titre", "le scenario")
#             etapes = scenario_json.get("grandes_lignes", [])
#             if etapes:
#                 noms = ", ".join(
#                     str(e.get("titre", "")) for e in etapes[:4]
#                 )
#                 resume = (
#                     "Le scenario intitule " + titre + " se deroule en "
#                     + str(len(etapes)) + " etapes : " + noms + "."
#                 )
#             else:
#                 resume = "Le scenario " + titre + " vient d'etre genere."

#         self.io.speak("Voici les grandes lignes de votre scenario.")
#         self.io.speak(resume)

#         # Annonce des points de vigilance s'ils existent
#         vigilance = scenario_json.get("points_vigilance", [])
#         if vigilance:
#             # Construit une phrase fluide (pas de liste TTS)
#             points = " et ".join(vigilance[:3])
#             self.io.speak("Points de vigilance a retenir : " + points + ".")

#         self.io.speak(
#             "Le scenario est pret. "
#             "Vous pouvez maintenant me poser vos questions. "
#             "Dites fin pour terminer."
#         )

#     # ------------------------------------------------------------------
#     # Phase 2 : Q&R supervisee
#     # ------------------------------------------------------------------

#     def _qa_loop(
#         self,
#         scenario_session,   # ScenarioSession | None
#         supervisor: SupervisorLLM,
#         config,
#     ) -> None:
#         """Boucle de questions / reponses supervisees."""
#         print("\n" + "-" * 60)
#         print("[ SESSION Q&R -- posez vos questions ]")
#         print("-" * 60)

#         narrator = NarratorSession(
#             topic = scenario_session.topic if scenario_session else "general"
#         )
#         consecutive_timeouts = 0
#         MAX_TIMEOUTS = 3

#         while True:

#             # ---- 1. Capture de la question --------------------------------
#             self.io.speak("Je vous ecoute.")
#             try:
#                 question = self.io.listen_chunk(
#                     pause_threshold   = STT_SILENCE_TIMEOUT,
#                     phrase_time_limit = STT_PHRASE_TIME_LIMIT,
#                     listen_timeout    = STT_LISTEN_TIMEOUT,
#                 )
#                 consecutive_timeouts = 0
#             except RuntimeError as exc:
#                 consecutive_timeouts += 1
#                 logger.info("Q&R timeout %d/%d: %s", consecutive_timeouts, MAX_TIMEOUTS, exc)
#                 if consecutive_timeouts >= MAX_TIMEOUTS:
#                     if self._ask_continue_qa():
#                         consecutive_timeouts = 0
#                     else:
#                         break
#                 continue

#             # ---- 2. Detection sortie --------------------------------------
#             if any(w in question.lower() for w in EXIT_WORDS):
#                 print("\nSortie Q&R : '%s'" % question)
#                 break

#             print("\n[Question] " + question)
#             narrator.add_chunk(question)

#             # ---- 3. Reponse LLM via ScenarioSession -----------------------
#             answer = self._get_answer(question, scenario_session, config)
#             print("[Reponse] " + answer)
#             self.io.speak(answer)

#             # ---- 4. Supervision de l'echange ------------------------------
#             exchange = "Q : " + question + "\nR : " + answer
#             decision = supervisor.analyse(narrator, exchange)
#             logger.info(
#                 "Superviseur Q&R: %s | '%s'",
#                 decision.decision.value,
#                 decision.message[:60] if decision.message else "",
#             )

#             if decision.decision == Decision.CONSEIL:
#                 print("\n[CONSEIL] " + decision.message)
#                 self.io.speak(decision.message)

#             elif decision.decision == Decision.STOP:
#                 print("\n[STOP] " + decision.message)
#                 self.io.interrupt_and_speak(decision.message)
#                 if not self._handle_stop_qa():
#                     break

#     def _get_answer(self, question: str, scenario_session, config) -> str:
#         """
#         Obtient une reponse LLM a la question posee.
#         Priorite : discuss_scenario() de vr_scenario_lib, puis LLM direct, puis fallback.
#         """
#         # -- Via vr_scenario_lib -------------------------------------------
#         if scenario_session is not None and config is not None:
#             try:
#                 from vr_scenario_lib.scenario import discuss_scenario
#                 reply = discuss_scenario(
#                     session      = scenario_session,
#                     user_message = question,
#                     llm_config   = config,
#                 )
#                 if reply and reply.strip():
#                     return reply.strip()
#             except Exception as exc:
#                 logger.warning("discuss_scenario erreur: %s -- fallback LLM direct", exc)

#         # -- LLM direct avec contexte scenario_text -------------------------
#         if config is not None:
#             context = (
#                 scenario_session.scenario_text[:800]
#                 if scenario_session and scenario_session.scenario_text
#                 else ""
#             )
#             user_msg = (
#                 ("Contexte du scenario :\n" + context + "\n\n" if context else "")
#                 + "Question de l'apprenant : " + question
#             )
#             try:
#                 return self._call_llm_raw(
#                     system    = QA_SYSTEM,
#                     user      = user_msg,
#                     config    = config,
#                     max_tokens= QA_MAX_TOKENS,
#                 ).strip()
#             except Exception as exc:
#                 logger.error("LLM direct Q&R erreur: %s", exc)

#         return "Je n'ai pas pu obtenir de reponse. Consultez la documentation du scenario."

#     # ------------------------------------------------------------------
#     # Helpers generaux
#     # ------------------------------------------------------------------

#     @staticmethod
#     def _call_llm_raw(*, system: str, user: str, config, max_tokens: int) -> str:
#         """Appel LLM unifie : vr_scenario_lib puis HTTP direct (OpenAI-compatible)."""
#         try:
#             from vr_scenario_lib.llm import call_llm
#             return call_llm(
#                 system=system, user=user,
#                 llm_config=config, max_tokens=max_tokens,
#             )
#         except ImportError:
#             pass

#         import urllib.request
#         payload = json.dumps({
#             "model":      getattr(config, "model", "gpt-3.5-turbo"),
#             "max_tokens": max_tokens,
#             "messages":   [
#                 {"role": "system", "content": system},
#                 {"role": "user",   "content": user},
#             ],
#         }).encode()
#         api_url = getattr(config, "api_url", "https://api.openai.com/v1/chat/completions")
#         token   = getattr(config, "token", "")
#         req = urllib.request.Request(
#             api_url, data=payload,
#             headers={
#                 "Content-Type":  "application/json",
#                 "Authorization": "Bearer " + token,
#             },
#         )
#         with urllib.request.urlopen(req, timeout=20) as resp:
#             data = json.loads(resp.read())
#         return data["choices"][0]["message"]["content"]

#     def _ask_continue_qa(self) -> bool:
#         text = self.io.listen_short(
#             "Je n'entends plus rien. "
#             "Avez-vous d'autres questions ? "
#             "Dites oui pour continuer, non pour terminer."
#         )
#         if not text:
#             return False
#         return any(w in text.lower() for w in {"oui", "yes", "continuer", "continue", "si"})

#     def _handle_stop_qa(self) -> bool:
#         """Pause apres STOP en phase Q&R. Retourne True pour reprendre."""
#         self.io.speak(
#             "La session est interrompue. "
#             "Dites reprendre pour continuer, ou fin pour terminer."
#         )
#         text = ""
#         try:
#             text = self.io.listen_chunk(
#                 pause_threshold=2.0,
#                 phrase_time_limit=10,
#                 listen_timeout=12,
#             )
#         except RuntimeError:
#             pass
#         if any(w in text.lower() for w in {"reprendre", "continuer", "oui", "yes"}):
#             self.io.speak("Tres bien. Continuez vos questions.")
#             return True
#         return False

#     def _goodbye(self) -> None:
#         self.io.speak("Merci pour cette session. A bientot !")
#         print("\nAu revoir !\n")

#     # ------------------------------------------------------------------
#     # LLM setup
#     # ------------------------------------------------------------------

#     def _setup_llm(self):
#         try:
#             from vr_scenario_lib.config import build_llm_config
#             return build_llm_config()
#         except Exception as exc:
#             logger.warning(
#                 "LLM config non disponible: %s -- mode degrade (scenarios statiques)", exc
#             )
#             return None


# # ============================================================================
# # CLI
# # ============================================================================

# def _parse_args() -> argparse.Namespace:
#     p = argparse.ArgumentParser(
#         description="Application vocale de supervision de scenarios VR",
#         formatter_class=argparse.ArgumentDefaultsHelpFormatter,
#     )
#     p.add_argument(
#         "--stt-backend", default="whisper", choices=["whisper", "google"],
#         help="Backend STT.",
#     )
#     p.add_argument(
#         "--tts-backend", default=TTS_DEFAULT_BACKEND,
#         choices=["coqui", "piper", "gtts", "pyttsx3"],
#         help="Backend TTS. 'coqui' et 'piper' sont 100%% offline et francais natif.",
#     )
#     p.add_argument(
#         "--language", default="fr",
#         help="Code langue ISO 639-1 (fr par defaut).",
#     )
#     p.add_argument(
#         "--whisper-model", default=WHISPER_DEFAULT_MODEL,
#         choices=["tiny", "base", "small", "medium", "large"],
#         help="Taille du modele Whisper. 'small' recommande pour le francais.",
#     )
#     p.add_argument(
#         "--coqui-model", default=COQUI_MODEL_FR,
#         help="Identifiant modele Coqui TTS.",
#     )
#     p.add_argument(
#         "--piper-model", default=PIPER_MODEL_FR,
#         help="Nom du modele Piper (ex: fr_FR-tom-medium).",
#     )
#     p.add_argument(
#         "--debug", action="store_true",
#         help="Active le logging DEBUG.",
#     )
#     return p.parse_args()


# def main() -> None:
#     args = _parse_args()
#     if args.debug:
#         logging.getLogger().setLevel(logging.DEBUG)

#     io = VoiceIO(
#         stt_backend   = args.stt_backend,
#         tts_backend   = args.tts_backend,
#         language      = args.language,
#         whisper_model = args.whisper_model,
#         coqui_model   = args.coqui_model,
#         piper_model   = args.piper_model,
#     )
#     app = VRScenarioApp(io)
#     try:
#         app.run()
#     except KeyboardInterrupt:
#         print("\nInterruption utilisateur.")
#     finally:
#         io.close()


# if __name__ == "__main__":
#     main()


# """
# tts_fr_normalizer.py
# ====================
# Préprocesseur de normalisation du texte pour synthèse vocale française (gTTS).

# Problème fondamental de gTTS
# -----------------------------
# gTTS transmet le texte brut à l'API Google Translate TTS sans normalisation.
# Le moteur TTS est optimisé pour du texte naturel : il prononce mal ou de façon
# incohérente les sigles, abréviations, termes techniques, mots anglais, symboles,
# et nombres dans certains contextes.

# Ce module corrige ces problèmes AVANT l'envoi à gTTS.
# Il est également utile pour Coqui et Piper (mêmes limitations de base).

# Architecture
# ------------
# La normalisation s'applique dans un ordre strict :
#   1. Blocs non oraux (code, URLs, Markdown)     → suppression
#   2. Symboles non oraux                          → suppression ou remplacement
#   3. Sigles et acronymes connus                  → expansion phonétique
#   4. Substitutions mot-à-mot (dictionnaire)      → remplacement direct
#   5. Mots anglais fréquents                      → translittération/équivalent
#   6. Nombres et unités                           → expansion littérale
#   7. Ponctuation et rythme                       → normalisation des pauses
#   8. Nettoyage final                             → espaces, casse

# Usage
# -----
#     from tts_fr_normalizer import normalize_for_tts

#     raw  = "L'EPI est OK. Le backend LLM (STT + TTS) tourne en 3ms."
#     text = normalize_for_tts(raw)
#     # → "L'équipement de protection individuelle est d'accord.
#     #    Le serveur du modèle de langage, transcription et synthèse vocale, tourne en 3 millisecondes."
# """

# from __future__ import annotations

# import re
# import unicodedata
# from typing import Dict, List, Tuple


# # ============================================================================
# # 1. SIGLES ET ACRONYMES  (expansion phonétique complète)
# # ============================================================================
# # Format : "SIGLE" → "expansion lue à voix haute"
# # Règle : toujours en minuscules dans la valeur (gTTS lit mieux le bas de casse)
# # Ordre : du plus long au plus court pour éviter les substitutions partielles

# ACRONYMS: Dict[str, str] = {
#     # Domaine VR / formation
#     "VR":       "réalité virtuelle",
#     "AR":       "réalité augmentée",
#     "XR":       "réalité étendue",

#     # Domaine IA / LLM
#     "LLM":      "modèle de langage",
#     "LLMs":     "modèles de langage",
#     "IA":       "intelligence artificielle",
#     "GPT":      "G P T",
#     "ChatGPT":  "tchat G P T",
#     "API":      "interface de programmation",
#     "APIs":     "interfaces de programmation",
#     "JSON":     "J S O N",
#     "XML":      "X M L",
#     "HTTP":     "H T T P",
#     "HTTPS":    "H T T P S",
#     "SDK":      "S D K",
#     "CLI":      "interface en ligne de commande",

#     # Audio / Speech
#     "STT":      "transcription vocale",
#     "TTS":      "synthèse vocale",
#     "VAD":      "détection d'activité vocale",
#     "NLP":      "traitement du langage naturel",
#     "ASR":      "reconnaissance automatique de la parole",

#     # Sécurité industrielle
#     "EPI":      "équipement de protection individuelle",
#     "EPIs":     "équipements de protection individuelle",
#     "EPC":      "équipement de protection collective",
#     "ATEX":     "atmosphère explosive",
#     "CHSCT":    "comité d'hygiène sécurité et conditions de travail",
#     "DUERP":    "document unique d'évaluation des risques professionnels",
#     "PRAP":     "prévention des risques liés à l'activité physique",
#     "CACES":    "certificat d'aptitude à la conduite en sécurité",
#     "SSIAP":    "service de sécurité incendie et d'assistance aux personnes",
#     "SST":      "sauveteur secouriste du travail",
#     "ERP":      "établissement recevant du public",
#     "IGH":      "immeuble de grande hauteur",
#     "ICPE":     "installation classée pour la protection de l'environnement",
#     "SEVESO":   "site Seveso",
#     "REACH":    "règlement sur les substances chimiques",

#     # Informatique générale
#     "CPU":      "processeur",
#     "GPU":      "carte graphique",
#     "RAM":      "mémoire vive",
#     "SSD":      "disque dur à semi-conducteur",
#     "OS":       "système d'exploitation",
#     "UI":       "interface utilisateur",
#     "UX":       "expérience utilisateur",

#     # Abréviations courantes mal lues
#     "Q&R":      "questions et réponses",
#     "Q/R":      "questions et réponses",
#     "R&D":      "recherche et développement",
#     # Normes : EN est trop ambigu (mot courant "en"), géré manuellement si besoin
#     # "EN" retiré du dictionnaire pour éviter "norme européenne" dans "en cours", etc.
#     # Conserver ISO car peu ambigu dans le contexte industriel
#     "ISO":      "I S O",
#     "NF":       "norme française",
#     "CEI":      "commission électrotechnique internationale",
#     "OK":       "d'accord",
#     "KO":       "en erreur",
#     "NB":       "nota bene",
#     "VS":       "par rapport à",
#     "vs":       "par rapport à",
# }

# # ============================================================================
# # 2. MOTS ET EXPRESSIONS ANGLAIS  (translittération / équivalent français)
# # ============================================================================
# # Ces termes sont fréquents dans le domaine IA / tech et souvent mal prononcés

# ENGLISH_WORDS: Dict[str, str] = {
#     # Termes IA / tech fréquents dans les prompts et réponses LLM
#     "backend":          "serveur dorsal",
#     "frontend":         "interface utilisateur",
#     "streaming":        "diffusion en continu",
#     "stream":           "flux",
#     "pipeline":         "chaîne de traitement",
#     "pipelines":        "chaînes de traitement",
#     "workflow":         "flux de travail",
#     "workflows":        "flux de travail",
#     "feedback":         "retour",
#     "feedbacks":        "retours",
#     "barge-in":         "interruption",
#     "warmup":           "préchauffage",
#     "cache":            "mémoire cache",
#     "chunk":            "segment",
#     "chunks":           "segments",
#     "prompt":           "instruction",
#     "prompts":          "instructions",
#     "token":            "unité de texte",
#     "tokens":           "unités de texte",
#     "thread":           "fil d'exécution",
#     "threads":          "fils d'exécution",
#     "debug":            "débogage",
#     "log":              "journal",
#     "logs":             "journaux",
#     "timeout":          "délai d'expiration",
#     "timeouts":         "délais d'expiration",
#     "offline":          "hors ligne",
#     "online":           "en ligne",
#     "input":            "entrée",
#     "output":           "sortie",
#     "outputs":          "sorties",
#     "benchmark":        "évaluation de performance",
#     "fallback":         "solution de repli",

#     # Termes VR / formation
#     "learner":          "apprenant",
#     "trainer":          "formateur",
#     "session":          "séance",
#     "checklist":        "liste de vérification",
#     "briefing":         "réunion de préparation",
#     "debriefing":       "debriefing",          # accepté en français technique
#     "safety":           "sécurité",
#     "procedure":        "procédure",
#     "scenario":         "scénario",

#     # Marques / produits (prononciations françaises naturelles)
#     "Whisper":          "ouisper",
#     "Coqui":            "coqui",               # déjà bon
#     "Piper":            "païpeur",
#     "Copilot":          "copilote",
#     "Gemini":           "géminaï",
# }

# # ============================================================================
# # 3. SUBSTITUTIONS CONTEXTUELLES (regex avec groupes)
# # ============================================================================
# # (pattern, remplacement) — appliqués dans l'ordre, sensibles à la casse via flags

# CONTEXTUAL_SUBS: List[Tuple[str, str]] = [
#     # Modèles de type "gpt-3.5-turbo", "claude-3-opus"
#     (r'\bgpt[-‑](\d[\w.-]*)', r'G P T \1'),
#     (r'\bclaude[-‑](\d[\w.-]*)', r'claude \1'),
#     (r'\bllama[-‑](\d[\w.-]*)', r'llama \1'),

#     # Langues type "fr-FR", "fr_FR", "en-US"
#     (r'\b([a-z]{2})[-_]([A-Z]{2})\b', r'\1 \2'),

#     # Versions type "v2.1", "v3" — uniquement si précédé d'un espace ou début de mot
#     # Évite de doubler si "version" est déjà présent avant
#     (r'(?<![a-zA-Z])v(\d+(?:\.\d+)*)\b', r'version \1'),

#     # Pourcentages : "95%", "100 %"
#     (r'(\d+)\s*%', r'\1 pourcent'),

#     # Millisecondes, secondes, minutes, heures avec chiffres
#     (r'(\d+)\s*ms\b',  r'\1 millisecondes'),
#     (r'(\d+)\s*s\b',   r'\1 secondes'),
#     (r'(\d+)\s*min\b', r'\1 minutes'),
#     (r'(\d+)\s*h\b',   r'\1 heures'),
#     (r'(\d+)\s*Hz\b',  r'\1 hertz'),
#     (r'(\d+)\s*kHz\b', r'\1 kilohertz'),

#     # Tailles mémoire
#     (r'(\d+)\s*Mo\b',  r'\1 mégaoctets'),
#     (r'(\d+)\s*Go\b',  r'\1 gigaoctets'),
#     (r'(\d+)\s*Ko\b',  r'\1 kilooctets'),
#     (r'(\d+)\s*MB\b',  r'\1 mégaoctets'),
#     (r'(\d+)\s*GB\b',  r'\1 gigaoctets'),
#     (r'(\d+)\s*KB\b',  r'\1 kilooctets'),

#     # Températures
#     (r'(\d+)\s*°C\b',  r'\1 degrés Celsius'),
#     (r'(\d+)\s*°F\b',  r'\1 degrés Fahrenheit'),

#     # Nombres ordinaux en chiffres : "1er", "2ème", "3ème"
#     (r'\b1er\b',  'premier'),
#     (r'\b1ère\b', 'première'),
#     (r'\b(\d+)ème\b', r'\1ième'),
#     (r'\b(\d+)e\b',   r'\1ième'),

#     # Slash entre termes techniques : "STT/TTS" → déjà géré par ACRONYMS
#     # mais les slash résiduels → "et"
#     (r'(?<=[a-zA-Z])/(?=[a-zA-Z])', ' et '),

#     # Tirets de composition technique : "temps-réel", "hors-ligne"
#     # Conserver le tiret dans les mots composés français courants (gTTS les gère)
#     # Supprimer uniquement dans les identifiants techniques (tout-en-minuscules-chiffres)
#     (r'\b([a-z0-9]+)-([a-z0-9]+)-([a-z0-9]+)\b', r'\1 \2 \3'),

#     # Parenthèses : lire le contenu, supprimer les délimiteurs
#     (r'\(([^)]{1,60})\)', r', \1,'),

#     # Points de suspension → pause
#     (r'\.{2,}', ','),

#     # Em-dash / en-dash → virgule
#     (r'\s*[–—]\s*', ', '),
# ]

# # ============================================================================
# # 4. PHRASES FIGÉES ET TOURNURES ORALES  (substitutions exactes)
# # ============================================================================
# # Phrases que l'application prononce souvent, optimisées pour la prosodie gTTS

# FIXED_PHRASES: Dict[str, str] = {
#     "je vous écoute":          "je vous écoute",        # déjà bon
#     "patientez":               "patientez",
#     "analyse en cours":        "analyse en cours",
#     "très bien":               "très bien",
#     "attention :":             "attention,",            # le ":" crée une pause gênante
#     "Attention :":             "Attention,",
#     "nota bene :":             "nota bene,",
#     "c'est-à-dire":            "c'est à dire",
#     "vis-à-vis":               "vis à vis",
#     "a priori":                "à priori",
#     "a posteriori":            "à posteriori",
#     "in situ":                 "in situ",
#     "de facto":                "de facto",
# }

# # ============================================================================
# # 5. CARACTÈRES INDIVIDUELS MAL LUS
# # ============================================================================

# CHAR_SUBS: Dict[str, str] = {
#     "&":  " et ",
#     "+":  " plus ",
#     "=":  " égal ",
#     "→":  " vers ",
#     "←":  " depuis ",
#     "↔":  " entre ",
#     "✓":  " valide ",
#     "✗":  " invalide ",
#     "⚠":  " attention ",
#     "★":  " étoile ",
#     "•":  " ",
#     "–":  ", ",
#     "—":  ", ",
#     "…":  ", ",
#     "«":  " ",
#     "»":  " ",
#     """:  " ",
#     """:  " ",
#     "'":  "'",   # apostrophe courbe → droite (essentiel pour gTTS)
#     "′":  "'",
#     "″":  " ",
#     "°":  " degrés ",
#     "€":  " euros ",
#     "$":  " dollars ",
#     "£":  " livres sterling ",
#     "©":  " copyright ",
#     "®":  " marque déposée ",
#     "™":  " marque ",
#     "№":  " numéro ",
#     "§":  " paragraphe ",
#     "¶":  " alinéa ",
#     "÷":  " divisé par ",
#     "×":  " fois ",
#     "≤":  " inférieur ou égal à ",
#     "≥":  " supérieur ou égal à ",
#     "≠":  " différent de ",
#     "≈":  " environ ",
#     "∞":  " infini ",
#     "π":  " pi ",
#     "µ":  " micro ",
#     "Ω":  " ohms ",
#     "²":  " au carré ",
#     "³":  " au cube ",
#     "¹":  " ",
#     "½":  " un demi ",
#     "⅓":  " un tiers ",
#     "¼":  " un quart ",
#     "¾":  " trois quarts ",
# }


# # ============================================================================
# # FONCTION PRINCIPALE
# # ============================================================================

# def normalize_for_tts(text: str, *, agressive: bool = False) -> str:
#     """Normalise un texte pour une prononciation optimale par gTTS (français).

#     Args:
#         text:      Texte brut à normaliser.
#         agressive: Si True, traduit également les mots anglais techniques
#                    (utile quand le texte LLM mélange français et anglais).

#     Returns:
#         Texte normalisé, lisible naturellement en français.
#     """
#     if not text:
#         return text

#     # --- 0. Normalisation Unicode (NFC) ------------------------------------
#     text = unicodedata.normalize("NFC", text)

#     # --- 1. Blocs non oraux -----------------------------------------------
#     text = _remove_non_verbal(text)
#     if not text.strip():
#         return ""

#     # --- 2. Phrases figées (avant toute autre substitution) ---------------
#     for src, dst in FIXED_PHRASES.items():
#         text = text.replace(src, dst)

#     # --- 3. Sigles et acronymes MULTI-CARACTÈRES (avant remplacement char) -
#     # Doit précéder CHAR_SUBS pour traiter "Q&R" avant que "&" → " et "
#     # et les unités "°C", "°F" avant que "°" → " degrés "
#     text = _expand_acronyms(text)

#     # --- 4. Substitutions contextuelles regex (avant remplacement char) ---
#     # "°C" et "°F" sont gérés ici avant que "°" isolé soit remplacé
#     for pattern, replacement in CONTEXTUAL_SUBS:
#         text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)

#     # --- 5. Caractères individuels (après sigles et regex) ----------------
#     for char, replacement in CHAR_SUBS.items():
#         text = text.replace(char, replacement)

#     # --- 6. Mots anglais (mode agressive) ---------------------------------
#     if agressive:
#         text = _replace_english(text)

#     # --- 7. Nettoyage final -----------------------------------------------
#     text = _final_cleanup(text)

#     return text


# # ============================================================================
# # HELPERS INTERNES
# # ============================================================================

# def _remove_non_verbal(text: str) -> str:
#     """Supprime les éléments non lisibles à voix haute."""
#     # Blocs de code Markdown (``` ... ```)
#     text = re.sub(r'```.*?```', ' ', text, flags=re.DOTALL)
#     # Code inline (`...`)
#     text = re.sub(r'`[^`]*`', ' ', text)
#     # Titres Markdown (# ## ###...)
#     text = re.sub(r'^\s*#{1,6}\s*', '', text, flags=re.MULTILINE)
#     # Emphase Markdown : **, *, __, _, ~~
#     text = re.sub(r'\*{1,3}|_{1,3}|~{1,2}', '', text)
#     # URLs
#     text = re.sub(r'https?://\S+|ftp://\S+', 'lien', text)
#     # Tirets de liste en début de ligne
#     text = re.sub(r'^\s*[-•–—]\s+', '', text, flags=re.MULTILINE)
#     # Séparateurs de tableaux Markdown
#     text = re.sub(r'^\s*[\-|: ]{3,}\s*$', '', text, flags=re.MULTILINE)
#     # Barres verticales (tableaux)
#     text = re.sub(r'\|', ' ', text)
#     # Caractères non oraux résiduels : \ @ # $ ^ { } [ ] < > =
#     text = re.sub(r'[\\@#$^{}\[\]<>=]', ' ', text)
#     return text


# def _expand_acronyms(text: str) -> str:
#     """Remplace les sigles et acronymes par leur expansion phonétique.

#     Stratégie :
#     - Trie les clés du plus long au plus court (évite les substitutions partielles).
#     - Utilise des frontières de mots (\b) pour ne pas déformer "épis" en "équipements..."
#     - Respecte la casse de l'original (insensible à la casse pour la détection).
#     """
#     # Tri par longueur décroissante pour éviter les collisions
#     sorted_acronyms = sorted(ACRONYMS.items(), key=lambda x: len(x[0]), reverse=True)

#     for sigle, expansion in sorted_acronyms:
#         # Frontières de mots, insensible à la casse
#         pattern = r'\b' + re.escape(sigle) + r'\b'
#         text = re.sub(pattern, expansion, text, flags=re.IGNORECASE)

#     return text


# def _replace_english(text: str) -> str:
#     """Remplace les termes anglais fréquents par leurs équivalents français.

#     Appliqué uniquement en mode agressive=True car certains termes anglais
#     sont acceptés en français technique (ex: "feedback" est courant).
#     """
#     sorted_english = sorted(ENGLISH_WORDS.items(), key=lambda x: len(x[0]), reverse=True)

#     for en_word, fr_word in sorted_english:
#         pattern = r'\b' + re.escape(en_word) + r'\b'
#         text = re.sub(pattern, fr_word, text, flags=re.IGNORECASE)

#     return text


# # def _final_cleanup(text: str) -> str:
# #     """Nettoyage final : espaces, sauts de ligne, ponctuation doublée, mots doublés."""
# #     # Sauts de ligne → espace
# #     text = re.sub(r'\n+', ' ', text)
# #     # Espaces multiples
# #     text = re.sub(r' {2,}', ' ', text)
# #     # Ponctuation doublée : ".." → ".", ",," → ","
# #     text = re.sub(r'([.,;:!?])\1+', r'\1', text)
# #     # Espace avant ponctuation finale (artefact des substitutions)
# #     text = re.sub(r' ([.,;:!?])', r'\1', text)
# #     # Mot immédiatement répété (ex: "version version") → une seule occurrence
# #     text = re.sub(r'\b(\w+) \1\b', r'\1', text, flags=re.IGNORECASE)
# #     # Virgule en début ou fin de chaîne
# #     text = text.strip(' ,')
# #     return text.strip()
# def _final_cleanup(text: str) -> str:
#     """Nettoyage final : espaces, sauts de ligne, ponctuation doublée."""
#     # Sauts de ligne → espace
#     text = re.sub(r'\n+', ' ', text)
#     # Espaces multiples
#     text = re.sub(r' {2,}', ' ', text)
#     # Ponctuation doublée : ".." → ".", ",," → ","
#     text = re.sub(r'([.,;:!?])\1+', r'\1', text)
#     # Espace avant ponctuation finale (artefact des substitutions)
#     text = re.sub(r' ([.,;:!?])', r'\1', text)
#     # Virgule en début ou fin de chaîne
#     text = text.strip(' ,')
#     return text.strip()

# # ============================================================================
# # INTÉGRATION DANS VoiceIO  (patch drop-in pour _sanitize_tts)
# # ============================================================================

# def sanitize_for_gtts(text: str) -> str:
#     """
#     Remplacement direct de VoiceIO._sanitize_tts() pour le backend gTTS.

#     Utilise le pipeline complet de normalisation avec mode agressive activé
#     (les réponses LLM mélangent souvent français et anglais technique).

#     Usage dans VoiceIO :
#         if self.tts_backend == "gtts":
#             text = sanitize_for_gtts(text)
#         else:
#             text = self._sanitize_tts(text)  # version originale
#     """
#     return normalize_for_tts(text, agressive=True)


# # ============================================================================
# # CACHE DES PHRASES FRÉQUENTES (pré-génération audio)
# # ============================================================================
# # Phrases que l'application prononce souvent et dont le fichier audio
# # peut être pré-généré au démarrage pour une latence nulle.

# CACHED_PHRASES_FR: List[str] = [
#     "Je vous écoute.",
#     "Patientez quelques instants.",
#     "Analyse en cours.",
#     "Très bien.",
#     "D'accord.",
#     "Je n'ai pas compris. Pouvez-vous répéter ?",
#     "La session est interrompue.",
#     "Merci pour cette session. À bientôt.",
#     "Bienvenue dans l'application vocale de scénarios de réalité virtuelle.",
#     "Je génère votre scénario.",
#     "Le scénario est prêt.",
#     "Vous pouvez maintenant me poser vos questions.",
#     "Dites fin pour terminer à tout moment.",
# ]


# def prewarm_gtts_cache(cache_dir: str = "/tmp/gtts_cache") -> Dict[str, str]:
#     """Pré-génère les fichiers audio pour les phrases fréquentes.

#     Returns:
#         Dictionnaire {texte_normalisé: chemin_fichier_mp3}

#     Usage :
#         cache = prewarm_gtts_cache()
#         # Puis dans _speak_gtts, vérifier si text est dans cache avant d'appeler gTTS
#     """
#     import hashlib
#     import os
#     from gtts import gTTS

#     os.makedirs(cache_dir, exist_ok=True)
#     cache: Dict[str, str] = {}

#     for phrase in CACHED_PHRASES_FR:
#         normalized = sanitize_for_gtts(phrase)
#         key = hashlib.md5(normalized.encode("utf-8")).hexdigest()
#         path = os.path.join(cache_dir, key + ".mp3")

#         if not os.path.exists(path):
#             try:
#                 tts = gTTS(text=normalized, lang="fr", slow=False)
#                 tts.save(path)
#             except Exception as exc:
#                 print(f"[prewarm] Erreur pour '{phrase[:40]}': {exc}")
#                 continue

#         cache[normalized] = path

#     return cache


# # ============================================================================
# # TESTS
# # ============================================================================

# def _run_tests() -> None:
#     """Vérifie les normalisations critiques."""
#     tests = [
#         # (entrée, fragment attendu dans la sortie)
#         ("L'EPI est obligatoire.", "équipement de protection individuelle"),
#         ("Le backend LLM répond en 50ms.", "modèle de langage"),
#         ("Le backend LLM répond en 50ms.", "50 millisecondes"),
#         ("Score : 95%", "95 pourcent"),
#         ("STT + TTS actifs.", "transcription vocale"),
#         ("Modèle gpt-3.5-turbo chargé.", "G P T"),
#         ("Version v2.1 disponible.", "version 2.1"),
#         ("Langue : fr-FR", "fr FR"),
#         ("Q&R supervisée", "questions et réponses"),
#         ("Télécharger 500Mo de données.", "500 mégaoctets"),
#         ("Température : 37°C", "37 degrés Celsius"),
#         ("**Attention** : EPI requis !", "Attention"),
#         ("```python\ncode\n```", ""),          # blocs code supprimés
#         ("Visitez https://example.com", "lien"),
#     ]

#     passed = 0
#     failed = 0
#     for raw, expected_fragment in tests:
#         result = normalize_for_tts(raw, agressive=True)
#         if expected_fragment.lower() in result.lower():
#             print(f"  ✓ '{raw[:50]}' → '{result[:80]}'")
#             passed += 1
#         else:
#             print(f"  ✗ '{raw[:50]}'")
#             print(f"      attendu  : '{expected_fragment}'")
#             print(f"      obtenu   : '{result[:80]}'")
#             failed += 1

#     print(f"\n{passed} tests réussis, {failed} échecs.")


# if __name__ == "__main__":
#     print("=== Tests de normalisation TTS français ===\n")
#     _run_tests()

#     print("\n=== Exemples de normalisation ===\n")
#     exemples = [
#         "L'EPI est OK. Le backend LLM (STT + TTS) tourne en 3ms.",
#         "Attention : le CACES R489 expire le 1er janvier. Prévenez le CHSCT.",
#         "Le modèle gpt-3.5-turbo traite 512 tokens en 150ms avec 95% de précision.",
#         "Q&R supervisée : phase 2/3 du scénario VR ATEX en cours.",
#         "Téléchargez 200Mo, version v3.2, langue fr-FR, température 22°C.",
#         "**Important** : vérifiez les EPI avant toute intervention SEVESO.",
#     ]
#     for ex in exemples:
#         print(f"AVANT : {ex}")
#         print(f"APRÈS : {normalize_for_tts(ex, agressive=True)}")
#         print()



#!/usr/bin/env python3
# """
# Application vocale de supervision de scenarios VR.
# Version enterprise -- standards industriels.

# ROLE DE L'APP
# -------------
# L'utilisateur decrit librement un scenario VR a voix haute.
# L'application ecoute en continu, transcrit par chunks VAD, et
# soumet chaque chunk a un LLM superviseur qui peut :
#   - CONTINUER  : ne rien dire (ecoute silencieuse)
#   - CONSEIL    : interrompre poliment pour donner un conseil
#   - STOP       : interrompre fermement pour signaler une erreur critique

# Architecture
# ------------
# VoiceIO          : STT (faster-whisper + SpeechRecognition VAD) + TTS francais natif.
# SupervisorLLM    : analyse chaque chunk, decide CONTINUER / CONSEIL / STOP.
# NarratorSession  : accumule la transcription, maintient le contexte du scenario.
# VRScenarioApp    : orchestration metier (setup + boucle de narration supervisee).
# PatienceManager  : feedback audio pendant la latence (earcons + phrases combinees).

# Backends TTS francais natifs (ordre de priorite automatique)
# ------------------------------------------------------------
# 1. coqui   -- Coqui VITS tts_models/fr/mai/tacotron2-DDC : voix neurale offline, haute qualite
# 2. piper   -- Piper fr_FR-tom-medium                      : voix neurale offline, ultra-rapide
# 3. gtts    -- Google TTS                                  : voix cloud, qualite maximale
# 4. pyttsx3 -- espeak-fr                                    : synthese basique, zero dependance

# Usage:
#     python app_vocal.py                            # auto-detection meilleur TTS dispo
#     python app_vocal.py --tts-backend coqui        # Coqui VITS (offline, haute qualite)
#     python app_vocal.py --tts-backend piper        # Piper (offline, ultra-rapide)
#     python app_vocal.py --tts-backend gtts         # Google TTS (cloud)
#     python app_vocal.py --stt-backend google       # Google STT (cloud)
#     python app_vocal.py --whisper-model small      # meilleure precision STT
#     python app_vocal.py --debug                    # logs DEBUG complets
# """

# from __future__ import annotations

# import argparse
# import json
# import logging
# import math
# import os
# import random
# import struct
# import sys
# import tempfile
# import threading
# import time
# import uuid
# from dataclasses import dataclass, field
# from datetime import datetime, timezone
# from enum import Enum
# from typing import Any, Dict, List, Optional

# # ---------------------------------------------------------------------------
# # Logging
# # ---------------------------------------------------------------------------
# logging.basicConfig(
#     level=logging.INFO,
#     format="%(asctime)s | %(name)-36s | %(levelname)-8s | %(message)s",
#     datefmt="%H:%M:%S",
# )
# logger = logging.getLogger(__name__)

# sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# # ============================================================================
# # Constantes
# # ============================================================================

# STT_LISTEN_TIMEOUT    = 8
# STT_PHRASE_TIME_LIMIT = 20          # duree max d'un chunk narration
# STT_SILENCE_TIMEOUT   = 2.0         # silence VAD -> fin du chunk
# STT_AMBIENT_DURATION  = 0.5
# TTS_SPEECH_RATE       = 145
# TTS_VOLUME            = 0.92
# WHISPER_DEFAULT_MODEL = "base"
# WHISPER_BEAM_SIZE     = 5
# EXIT_WORDS            = {"quitter", "exit", "quit", "au revoir", "stop", "fin"}

# # Backends TTS francais natifs
# TTS_DEFAULT_BACKEND   = "coqui"
# TTS_FALLBACK_CHAIN    = ["coqui", "piper", "gtts", "pyttsx3"]

# # Coqui TTS
# # tts_models/fr/mai/tacotron2-DDC : voix feminine MAI, accent francais metropolitain marque
# # Fallback possible : tts_models/fr/css10/vits (accent neutre)
# COQUI_MODEL_FR        = "tts_models/fr/mai/tacotron2-DDC"
# COQUI_SAMPLE_RATE     = 22050

# # Piper TTS
# # fr_FR-tom-medium : voix masculine Tom, accent francais metropolitain naturel
# # Fallback possible : fr_FR-upmc-medium (accent neutre universitaire)
# PIPER_MODEL_FR        = "fr_FR-tom-medium"
# PIPER_SAMPLE_RATE     = 22050

# # Supervisor LLM
# SUPERVISOR_MAX_TOKENS = 256
# SUPERVISOR_SYSTEM = (
#     "Tu es un superviseur expert en securite VR et en procedures industrielles. "
#     "L'utilisateur decrit a voix haute un scenario de formation VR. "
#     "Tu recois des fragments de sa narration en temps reel.\n\n"
#     "Analyse le dernier fragment dans son contexte et reponds UNIQUEMENT avec un objet JSON :\n"
#     '{"decision": "CONTINUER" | "CONSEIL" | "STOP", "message": "<texte a dire, vide si CONTINUER>"}\n\n'
#     "Regles strictes :\n"
#     "- CONTINUER  : narration correcte, coherente, sans danger. Message vide obligatoire.\n"
#     "- CONSEIL    : amelioration possible. Message court, positif, actionnable. Max 2 phrases.\n"
#     "- STOP       : erreur critique de procedure, danger reel, incoherence grave. "
#     "Message direct et precis. Commence par 'Attention : '.\n"
#     "Ne jamais inventer de contexte non mentionne. Rester factuel."
# )

# # Scenario generation LLM
# SCENARIO_GEN_MAX_TOKENS = 1024
# SCENARIO_GEN_SYSTEM = (
#     "Tu es un expert en conception de scenarios de formation VR industrielle. "
#     "A partir d'un theme, genere un scenario structure en JSON UNIQUEMENT, sans aucun texte avant ou apres.\n\n"
#     "Format JSON attendu (respecte exactement ces cles) :\n"
#     '{\n'
#     '  "titre": "Titre court du scenario",\n'
#     '  "objectifs": ["objectif 1", "objectif 2", "objectif 3"],\n'
#     '  "grandes_lignes": [\n'
#     '    {"etape": 1, "titre": "Titre etape", "description": "Description concise"},\n'
#     '    ...\n'
#     '  ],\n'
#     '  "procedures_cles": ["procedure 1", "procedure 2"],\n'
#     '  "points_vigilance": ["point 1", "point 2"],\n'
#     '  "resume_oral": "Texte fluide de 3-4 phrases pour lecture TTS. Pas de liste, pas de symboles."\n'
#     '}\n\n'
#     "Le champ resume_oral doit etre lisible a voix haute sans accroc : pas de tirets, "
#     "pas de parentheses, pas d'abreviations. Maximum 4 phrases."
# )

# # Q&R supervisee
# QA_MAX_TOKENS = 512
# QA_SYSTEM = (
#     "Tu es un formateur expert qui aide un apprenant a comprendre un scenario de formation VR. "
#     "Tu reponds aux questions en te basant exclusivement sur le scenario fourni. "
#     "Tes reponses sont courtes (2-3 phrases maximum), claires, et adaptees a une lecture TTS : "
#     "pas de listes, pas de tirets, pas de symboles. Parle directement a l'apprenant."
# )


# # ============================================================================
# # Phrases systeme variees (reduction de la fatigue auditive)
# # ----------------------------------------------------------------------------
# # Chaque cle correspond a une situation recurrente. Plusieurs formulations
# # evitent la repetition exacte ressentie par l'utilisateur sur une longue
# # session de Q&R. pick() tire une variante au hasard a chaque appel.
# # ============================================================================

# CACHED_PHRASES_FR: Dict[str, List[str]] = {
#     "listening": [
#         "Je vous ecoute.",
#         "A vous.",
#         "Je vous laisse parler.",
#     ],
#     "ack_short": [
#         "Compris.",
#         "Bien recu.",
#         "Note.",
#     ],
#     "thinking_short": [
#         "Un instant.",
#         "Je regarde.",
#     ],
#     "thinking_medium": [
#         "Je prepare votre reponse.",
#         "Je verifie les informations.",
#         "Je consulte le scenario.",
#     ],
#     "thinking_long": [
#         "Cela demande un peu plus de reflexion, je continue.",
#         "Je creuse le sujet, merci de patienter.",
#         "C'est une question detaillee, je finalise la reponse.",
#     ],
#     "thinking_very_long": [
#         "Je suis toujours en train de traiter votre demande, encore un instant.",
#         "Le traitement prend un peu plus de temps que prevu, je reste sur le sujet.",
#     ],
#     "soft_nudge": [
#         "Je suis toujours a l'ecoute si vous voulez continuer.",
#         "Prenez votre temps, je reste disponible.",
#         "Quand vous etes pret, je vous ecoute.",
#     ],
#     "no_response_continue_check": [
#         "Je n'entends plus rien. Avez-vous d'autres questions ? Dites oui pour continuer, non pour terminer.",
#     ],
# }


# def pick(key: str) -> str:
#     """Tire une variante de phrase systeme pour limiter la repetition exacte."""
#     options = CACHED_PHRASES_FR.get(key)
#     if not options:
#         return ""
#     return random.choice(options)


# # ============================================================================
# # Decision + NarratorSession
# # ============================================================================

# class Decision(Enum):
#     CONTINUER = "CONTINUER"
#     CONSEIL   = "CONSEIL"
#     STOP      = "STOP"


# @dataclass
# class SupervisorDecision:
#     decision: Decision = Decision.CONTINUER
#     message:  str      = ""

#     def must_speak(self) -> bool:
#         return self.decision in (Decision.CONSEIL, Decision.STOP)


# @dataclass
# class NarratorSession:
#     """Accumule la transcription et maintient le contexte pour le LLM."""
#     topic:     str
#     chunks:    List[str] = field(default_factory=list)
#     full_text: str       = ""

#     def add_chunk(self, text: str) -> None:
#         self.chunks.append(text)
#         self.full_text = " ".join(self.chunks)

#     def context_window(self, n: int = 5) -> str:
#         return " ".join(self.chunks[-n:])

#     def summary(self) -> str:
#         return "%d sequence(s), ~%d mots" % (len(self.chunks), len(self.full_text.split()))


# # ============================================================================
# # PatienceManager -- feedback audio pendant la latence (earcons + phrases)
# # ----------------------------------------------------------------------------
# # Strategie a paliers, alignee sur la duree d'attente reelle observee :
# #   < 1s    : rien (sous le seuil de perception genante)
# #   1-3s    : earcon discret seul (pas de phrase, evite la surcharge verbale)
# #   3-10s   : earcon + courte phrase de transition ("Je prepare votre reponse.")
# #   > 10s   : earcon + phrase "longue attente" repetee a intervalle reduit,
# #             avec un message different si l'attente continue (> 20s).
# #
# # Le monitoring tourne dans un thread separe pendant l'appel bloquant au LLM,
# # et s'arrete proprement (Event) dès que le resultat est disponible.
# # ============================================================================

# class PatienceManager:
#     """Pilote earcons + phrases de patience selon la duree d'attente reelle."""

#     LEVEL_SHORT_S       = 1.0    # < 1s : rien
#     LEVEL_MEDIUM_S       = 3.0   # 1-3s : earcon seul
#     LEVEL_LONG_S         = 10.0  # 3-10s : earcon + phrase courte
#     LEVEL_VERY_LONG_S    = 20.0  # >10s : earcon + phrase longue, repete au-dela

#     def __init__(self, io: "VoiceIO") -> None:
#         self.io = io
#         self._stop_event = threading.Event()
#         self._thread: Optional[threading.Thread] = None

#     def start(self) -> None:
#         self._stop_event.clear()
#         self._thread = threading.Thread(target=self._run, daemon=True)
#         self._thread.start()

#     def stop(self) -> None:
#         self._stop_event.set()
#         if self._thread is not None:
#             self._thread.join(timeout=2.0)
#             self._thread = None

#     def _run(self) -> None:
#         start = time.monotonic()
#         announced_medium    = False
#         announced_long      = False
#         announced_very_long = False

#         while not self._stop_event.is_set():
#             elapsed = time.monotonic() - start

#             if elapsed >= self.LEVEL_MEDIUM_S and not announced_medium:
#                 announced_medium = True
#                 self.io.play_earcon("patience_short")

#             if elapsed >= self.LEVEL_LONG_S and not announced_long:
#                 announced_long = True
#                 self.io.play_earcon("patience_medium")
#                 self.io.speak(pick("thinking_medium"), blocking=False)

#             if elapsed >= self.LEVEL_VERY_LONG_S and not announced_very_long:
#                 announced_very_long = True
#                 self.io.play_earcon("patience_long")
#                 self.io.speak(pick("thinking_long"), blocking=False)

#             # Au-dela de la tres longue attente, on rappelle l'utilisateur
#             # qu'on est toujours actif, a intervalle reduit pour eviter le
#             # silence total qui inquiete plus que la repetition.
#             if announced_very_long and elapsed >= self.LEVEL_VERY_LONG_S + 12.0:
#                 self.io.speak(pick("thinking_very_long"), blocking=False)
#                 start -= 12.0  # reprogramme le prochain rappel +12s plus tard

#             self._stop_event.wait(timeout=0.25)

#     def run_with_patience(self, fn, *args, **kwargs):
#         """Execute fn(*args, **kwargs) en pilotant le feedback de patience."""
#         self.start()
#         try:
#             return fn(*args, **kwargs)
#         finally:
#             self.stop()


# # ============================================================================
# # SupervisorLLM
# # ============================================================================

# class SupervisorLLM:
#     """Analyse les chunks de narration et produit des decisions superviseur."""

#     def __init__(self, config) -> None:
#         self._config = config
#         self._lock   = threading.Lock()

#     def analyse(self, session: NarratorSession, new_chunk: str) -> SupervisorDecision:
#         if self._config is None:
#             return SupervisorDecision()

#         user_msg = (
#             "Theme du scenario : %s\n\n"
#             "Contexte (narration precedente) :\n%s\n\n"
#             "Nouveau fragment :\n%s"
#         ) % (session.topic, session.context_window(), new_chunk)

#         try:
#             with self._lock:
#                 raw = self._call_llm(user_msg)
#             return self._parse(raw)
#         except Exception as exc:
#             logger.warning("SupervisorLLM erreur: %s", exc)
#             return SupervisorDecision()

#     def _call_llm(self, user_msg: str) -> str:
#         # Tentative via vr_scenario_lib
#         try:
#             from vr_scenario_lib.llm import call_llm
#             return call_llm(
#                 system=SUPERVISOR_SYSTEM,
#                 user=user_msg,
#                 llm_config=self._config,
#                 max_tokens=SUPERVISOR_MAX_TOKENS,
#             )
#         except ImportError:
#             pass

#         # Fallback HTTP direct (OpenAI-compatible)
#         import json
#         import urllib.request

#         payload = json.dumps({
#             "model":      getattr(self._config, "model", "gpt-3.5-turbo"),
#             "max_tokens": SUPERVISOR_MAX_TOKENS,
#             "messages":   [
#                 {"role": "system", "content": SUPERVISOR_SYSTEM},
#                 {"role": "user",   "content": user_msg},
#             ],
#         }).encode()
#         api_url = getattr(self._config, "api_url", "https://api.openai.com/v1/chat/completions")
#         token   = getattr(self._config, "token", "")
#         req = urllib.request.Request(
#             api_url,
#             data=payload,
#             headers={
#                 "Content-Type":  "application/json",
#                 "Authorization": "Bearer " + token,
#             },
#         )
#         with urllib.request.urlopen(req, timeout=15) as resp:
#             data = json.loads(resp.read())
#         return data["choices"][0]["message"]["content"]

#     def _parse(self, raw: str) -> SupervisorDecision:
#         import json
#         import re
#         m = re.search(r'\{.*\}', raw, re.DOTALL)
#         if not m:
#             logger.warning("SupervisorLLM: JSON introuvable dans '%s'", raw[:120])
#             return SupervisorDecision()
#         obj = json.loads(m.group())
#         try:
#             dec = Decision(obj.get("decision", "CONTINUER").upper())
#         except ValueError:
#             dec = Decision.CONTINUER
#         return SupervisorDecision(decision=dec, message=obj.get("message", "").strip())


# # ============================================================================
# # VoiceIO
# # ============================================================================

# class VoiceIO:
#     """Couche bas-niveau STT + TTS.

#     Regles fondamentales
#     --------------------
#     1. speak() est TOUJOURS bloquant dans le flux principal.
#        Un TTS non-bloquant avant listen() = echo capture par Whisper.
#     2. Le micro n'est jamais ouvert pendant la synthese vocale.
#     3. L'enregistrement utilise la VAD (SpeechRecognition), pas une duree fixe.
#     4. interrupt_and_speak() coupe l'audio en cours avant de parler (STOP urgents).
#     5. play_earcon() est toujours non-bloquant et tres court (< 400ms) : il ne
#        doit jamais retarder le flux conversationnel.
#     """

#     def __init__(
#         self,
#         stt_backend:   str = "whisper",
#         tts_backend:   str = TTS_DEFAULT_BACKEND,
#         language:      str = "fr",
#         whisper_model: str = WHISPER_DEFAULT_MODEL,
#         coqui_model:   str = COQUI_MODEL_FR,
#         piper_model:   str = PIPER_MODEL_FR,
#     ) -> None:
#         self.stt_backend      = stt_backend
#         self.tts_backend      = tts_backend
#         self.language         = language
#         self.whisper_model_id = whisper_model
#         self.coqui_model_id   = coqui_model
#         self.piper_model_id   = piper_model

#         self._recognizer    = None
#         self._whisper_model = None
#         self._tts_engine    = None
#         self._coqui_model   = None
#         self._lock_tts      = threading.Lock()

#         self._init()

#     # ------------------------------------------------------------------
#     # Init
#     # ------------------------------------------------------------------

#     def _init(self) -> None:
#         self._init_stt()
#         self._init_tts()
#         logger.info(
#             "VoiceIO pret -- STT: %s | TTS: %s | Langue: %s",
#             self.stt_backend, self.tts_backend, self.language,
#         )

#     def _init_stt(self) -> None:
#         try:
#             import speech_recognition as sr
#             self._recognizer = sr.Recognizer()
#             self._recognizer.energy_threshold         = 4000
#             self._recognizer.pause_threshold          = STT_SILENCE_TIMEOUT
#             self._recognizer.dynamic_energy_threshold = True
#         except ImportError:
#             raise RuntimeError(
#                 "SpeechRecognition manquant. pip install SpeechRecognition PyAudio"
#             )
#         if self.stt_backend == "whisper":
#             self._whisper_model = self._load_whisper()

#     def _load_whisper(self) -> object:
#         try:
#             from faster_whisper import WhisperModel
#             logger.info("Chargement faster-whisper '%s'...", self.whisper_model_id)
#             model = WhisperModel(
#                 self.whisper_model_id,
#                 device="cpu",
#                 compute_type="int8",
#             )
#             logger.info("faster-whisper pret")
#             return model
#         except ImportError:
#             raise RuntimeError("faster-whisper manquant. pip install faster-whisper")

#     def _init_tts(self) -> None:
#         chain = (
#             [self.tts_backend]
#             + [b for b in TTS_FALLBACK_CHAIN if b != self.tts_backend]
#         )
#         for backend in chain:
#             try:
#                 if backend == "coqui":
#                     self._init_coqui()
#                 elif backend == "piper":
#                     self._init_piper()
#                 elif backend == "gtts":
#                     self._init_gtts()
#                 elif backend == "pyttsx3":
#                     self._init_pyttsx3()
#                 else:
#                     continue
#                 self.tts_backend = backend
#                 logger.info("TTS backend actif : %s", backend)
#                 return
#             except Exception as exc:
#                 logger.warning(
#                     "TTS backend '%s' indisponible: %s -- essai suivant", backend, exc
#                 )

#         raise RuntimeError(
#             "Aucun backend TTS disponible. "
#             "Installez au moins : pip install coqui-tts sounddevice soundfile"
#         )

#     # ------------------------------------------------------------------
#     # Init Coqui VITS -- voix neurale francaise offline
#     # ------------------------------------------------------------------

#     def _init_coqui(self) -> None:
#         try:
#             from TTS.api import TTS as CoquiTTS
#             import sounddevice  # noqa: F401
#             import soundfile    # noqa: F401
#         except ImportError:
#             raise RuntimeError(
#                 "Coqui TTS manquant. pip install coqui-tts sounddevice soundfile"
#             )
#         logger.info("Chargement Coqui TTS '%s'...", self.coqui_model_id)
#         self._coqui_model = CoquiTTS(
#             model_name=self.coqui_model_id,
#             progress_bar=False,
#             gpu=False,
#         )
#         logger.info("Coqui TTS pret")

#     # ------------------------------------------------------------------
#     # Init Piper -- voix neurale francaise offline, ultra-rapide
#     # ------------------------------------------------------------------

#     def _init_piper(self) -> None:
#         try:
#             import piper  # noqa: F401
#         except ImportError:
#             raise RuntimeError("piper-tts manquant. pip install piper-tts")
#         logger.info("Piper TTS disponible -- modele '%s'", self.piper_model_id)

#     # ------------------------------------------------------------------
#     # Init gTTS -- Google TTS cloud
#     # ------------------------------------------------------------------

#     def _init_gtts(self) -> None:
#         try:
#             import gtts    # noqa: F401
#             import pygame  # noqa: F401
#         except ImportError:
#             raise RuntimeError("gTTS/pygame manquants. pip install gTTS pygame")
#         logger.info("gTTS cloud initialise")

#     # ------------------------------------------------------------------
#     # Init pyttsx3 -- fallback ultime espeak
#     # ------------------------------------------------------------------

#     def _init_pyttsx3(self) -> None:
#         try:
#             import pyttsx3
#         except ImportError:
#             raise RuntimeError("pyttsx3 manquant. pip install pyttsx3")

#         engine = pyttsx3.init()
#         engine.setProperty("rate",   TTS_SPEECH_RATE)
#         engine.setProperty("volume", TTS_VOLUME)

#         fr_voice_found = False
#         # Priorite 1 : fr_FR espeak-ng (accent francais metropolitain pur)
#         # Priorite 2 : toute voix contenant "french" ou "fr" dans le nom/id
#         for priority in ("fr_FR", "fr-FR", "french", "fr"):
#             for v in engine.getProperty("voices"):
#                 name_lower = v.name.lower()
#                 id_lower   = v.id.lower()
#                 if priority.lower() in id_lower or priority.lower() in name_lower:
#                     engine.setProperty("voice", v.id)
#                     logger.info("pyttsx3 voix francaise selectionnee : %s (%s)", v.name, v.id)
#                     fr_voice_found = True
#                     break
#             if fr_voice_found:
#                 break

#         if not fr_voice_found:
#             logger.warning(
#                 "Aucune voix francaise trouvee dans pyttsx3. "
#                 "Linux: sudo apt install espeak-ng-data"
#             )

#         self._tts_engine = engine
#         logger.info("pyttsx3 initialise (voix systeme)")

#     # ------------------------------------------------------------------
#     # TTS -- TOUJOURS bloquant dans le flux principal
#     # ------------------------------------------------------------------

#     def interrupt_and_speak(self, text: str) -> None:
#         """Coupe l'audio en cours PUIS parle. Reserve aux STOP urgents."""
#         self._stop_audio()
#         self.speak(text)

#     def _stop_audio(self) -> None:
#         """Arrete immediatement la lecture audio (tous backends)."""
#         try:
#             if self.tts_backend in ("coqui", "piper"):
#                 import sounddevice as sd
#                 sd.stop()
#             elif self.tts_backend == "gtts":
#                 try:
#                     import pygame
#                     if pygame.mixer.get_init():
#                         pygame.mixer.music.stop()
#                 except Exception:
#                     pass
#         except Exception as exc:
#             logger.debug("_stop_audio: %s", exc)

#     @staticmethod
#     def _sanitize_tts(text: str) -> str:
#         """Supprime les caracteres non oraux avant synthese vocale.

#         Regles appliquees dans l'ordre :
#         1. Blocs code Markdown (``` ... ```) -> supprimes
#         2. Emphase Markdown (* ** _ __ ~ ~~) -> supprimes (le texte reste)
#         3. Titres Markdown (# ## ###...)     -> supprimes (le texte reste)
#         4. URLs (http/https/ftp)             -> remplacees par 'lien'
#         5. Ponctuation non orale             -> remplacee ou supprimee
#         6. Espaces multiples / lignes vides  -> normalises
#         """
#         import re

#         # 1. Blocs code (``` ... ```) et code inline (` ... `)
#         text = re.sub(r'```.*?```', '', text, flags=re.DOTALL)
#         text = re.sub(r'`[^`]*`', '', text)

#         # 2. Emphase Markdown : **, *, __, _, ~~, ~
#         text = re.sub(r'\*{1,3}|_{1,3}|~{1,2}', '', text)

#         # 3. Titres Markdown : # au debut d'une ligne
#         text = re.sub(r'^\s*#{1,6}\s*', '', text, flags=re.MULTILINE)

#         # 4. URLs
#         text = re.sub(r'https?://\S+|ftp://\S+', 'lien', text)

#         # 5. Ponctuation non orale
#         #    - Tirets de liste en debut de ligne -> supprimes
#         text = re.sub(r'^\s*[-•–—]\s+', '', text, flags=re.MULTILINE)
#         #    - Lignes separateurs de tableaux Markdown (---|--- etc.)
#         text = re.sub(r'^\s*[\-|: ]{3,}\s*$', '', text, flags=re.MULTILINE)
#         #    - Barres verticales (tableaux Markdown)
#         text = re.sub(r'\|', ' ', text)
#         #    - Caracteres vraiment non oraux : \ / @ # $ % ^ & { } [ ] < > =
#         text = re.sub(r'[\\/@#$%^&{}\[\]<>=]', ' ', text)
#         #    - Parentheses et crochets : garder le contenu, supprimer les delimiteurs
#         text = re.sub(r'[(){}\[\]]', ' ', text)
#         #    - Points de suspension : remplacer par une virgule (pause naturelle)
#         text = re.sub(r'\.{2,}', ',', text)
#         #    - Tirets en milieu de phrase (em-dash, en-dash) -> virgule
#         text = re.sub(r'\s*[–—]\s*', ', ', text)
#         #    - Astérisques restants
#         text = re.sub(r'\*+', '', text)
#         #    - Underscores restants
#         text = re.sub(r'_+', ' ', text)

#         # 6. Normalisation des espaces et sauts de ligne
#         text = re.sub(r'\n+', ' ', text)
#         text = re.sub(r' {2,}', ' ', text)

#         return text.strip()

#     def speak(self, text: str, *, blocking: bool = True) -> None:
#         """Synthese vocale en francais natif.

#         blocking=True (defaut) : retourne APRES la fin de la lecture.
#         blocking=False         : usage exceptionnel uniquement (ex: phrases de
#                                   patience emises par PatienceManager pendant
#                                   qu'un autre thread attend le LLM -- dans ce
#                                   cas le micro n'est pas sollicite en parallele,
#                                   donc pas de risque d'echo capture par le STT).
#         REGLE : ne JAMAIS appeler avec blocking=False juste avant listen().
#         """
#         if not text or not text.strip():
#             return
#         text = self._sanitize_tts(text)
#         if not text:
#             return
#         logger.info("TTS [%s]: '%s'", self.tts_backend, text[:80])

#         dispatch = {
#             "coqui":   self._speak_coqui,
#             "piper":   self._speak_piper,
#             "gtts":    self._speak_gtts,
#             "pyttsx3": self._speak_pyttsx3,
#         }
#         fn = dispatch.get(self.tts_backend)
#         if fn is None:
#             logger.error("Backend TTS inconnu: %s", self.tts_backend)
#             print("[TTS] " + text)
#             return
#         fn(text, blocking)

#     # ------------------------------------------------------------------
#     # Earcons -- feedback sonore court de patience (non-bloquant, < 400ms)
#     # ----------------------------------------------------------------------
#     # Generes a la volee (bips sinusoidaux), zero dependance audio externe
#     # au-dela de ce qui est deja requis par les backends coqui/piper (sounddevice
#     # + soundfile). Si indisponible, on degrade silencieusement (pas de crash,
#     # pas de print parasite -- un earcon manque ne doit jamais bloquer le flux).
#     # ------------------------------------------------------------------

#     _EARCON_PROFILES = {
#         # (frequence Hz, duree s, amplitude) -- profils courts et discrets
#         "patience_short":  (880.0, 0.10, 0.15),   # bip discret, attente 1-3s
#         "patience_medium": (660.0, 0.15, 0.18),   # bip un peu plus marque, 3-10s
#         "patience_long":   (440.0, 0.22, 0.20),   # bip grave, attente longue >10s
#     }

#     def play_earcon(self, profile: str) -> None:
#         """Joue un earcon court et non-bloquant. Echec = silencieux."""
#         params = self._EARCON_PROFILES.get(profile)
#         if params is None:
#             return
#         try:
#             threading.Thread(
#                 target=self._play_earcon_sync, args=(params,), daemon=True
#             ).start()
#         except Exception as exc:
#             logger.debug("play_earcon: %s", exc)

#     def _play_earcon_sync(self, params) -> None:
#         freq, duration, amplitude = params
#         try:
#             import sounddevice as sd
#             sample_rate = 22050
#             n_samples = int(sample_rate * duration)
#             tone = [
#                 amplitude * math.sin(2 * math.pi * freq * (i / sample_rate))
#                 for i in range(n_samples)
#             ]
#             sd.play(tone, sample_rate)
#             sd.wait()
#         except Exception as exc:
#             logger.debug("Earcon indisponible (%s), feedback sonore ignore", exc)

#     # ------------------------------------------------------------------
#     # _speak_coqui : Coqui VITS -- reference qualite
#     # ------------------------------------------------------------------

#     def _speak_coqui(self, text: str, blocking: bool) -> None:
#         tmp_path: Optional[str] = None
#         try:
#             import soundfile as sf
#             import sounddevice as sd

#             with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
#                 tmp_path = f.name

#             with self._lock_tts:
#                 self._coqui_model.tts_to_file(text=text, file_path=tmp_path)

#             data, sr = sf.read(tmp_path, dtype="float32")
#             if blocking:
#                 sd.play(data, sr)
#                 sd.wait()
#             else:
#                 sd.play(data, sr)

#         except Exception as exc:
#             logger.error("Coqui TTS erreur: %s", exc)
#             print("[TTS] " + text)
#         finally:
#             if tmp_path and os.path.exists(tmp_path):
#                 try:
#                     os.unlink(tmp_path)
#                 except OSError:
#                     pass

#     # ------------------------------------------------------------------
#     # _speak_piper : Piper -- latence minimale
#     # ------------------------------------------------------------------

#     def _speak_piper(self, text: str, blocking: bool) -> None:
#         tmp_path: Optional[str] = None
#         try:
#             import subprocess
#             import soundfile as sf
#             import sounddevice as sd

#             with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
#                 tmp_path = f.name

#             result = subprocess.run(
#                 ["piper", "--model", self.piper_model_id, "--output_file", tmp_path],
#                 input=text.encode("utf-8"),
#                 capture_output=True,
#                 timeout=30,
#             )
#             if result.returncode != 0:
#                 raise RuntimeError(
#                     "piper returncode=%d: %s" % (result.returncode, result.stderr.decode())
#                 )

#             data, sr = sf.read(tmp_path, dtype="float32")
#             if blocking:
#                 sd.play(data, sr)
#                 sd.wait()
#             else:
#                 sd.play(data, sr)

#         except FileNotFoundError:
#             logger.error("Executable 'piper' introuvable. pip install piper-tts")
#             print("[TTS] " + text)
#         except Exception as exc:
#             logger.error("Piper TTS erreur: %s", exc)
#             print("[TTS] " + text)
#         finally:
#             if tmp_path and os.path.exists(tmp_path):
#                 try:
#                     os.unlink(tmp_path)
#                 except OSError:
#                     pass

#     # ------------------------------------------------------------------
#     # _speak_gtts : Google TTS cloud
#     # Bug corrige : mixer reinitialise a chaque appel (non-reentrant).
#     # ------------------------------------------------------------------

#     def _speak_gtts(self, text: str, blocking: bool) -> None:
#         tmp_path: Optional[str] = None
#         try:
#             from gtts import gTTS
#             import pygame

#             tts = gTTS(text=text, lang=self.language, slow=False)
#             with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
#                 tmp_path = f.name
#             tts.save(tmp_path)

#             # Reinitialisation propre du mixer a chaque appel
#             if pygame.mixer.get_init():
#                 pygame.mixer.quit()
#             pygame.mixer.init(frequency=22050, size=-16, channels=1, buffer=512)
#             pygame.mixer.music.load(tmp_path)
#             pygame.mixer.music.play()

#             if blocking:
#                 while pygame.mixer.music.get_busy():
#                     time.sleep(0.05)
#                 pygame.mixer.quit()

#         except Exception as exc:
#             logger.error("gTTS erreur: %s", exc)
#             print("[TTS] " + text)
#         finally:
#             if tmp_path and os.path.exists(tmp_path):
#                 try:
#                     time.sleep(0.1)   # libere le handle fichier
#                     os.unlink(tmp_path)
#                 except OSError:
#                     pass

#     # ------------------------------------------------------------------
#     # _speak_pyttsx3 : espeak fallback ultime
#     # ------------------------------------------------------------------

#     def _speak_pyttsx3(self, text: str, blocking: bool) -> None:
#         with self._lock_tts:
#             try:
#                 self._tts_engine.say(text)
#                 if blocking:
#                     self._tts_engine.runAndWait()
#                 else:
#                     # NOTE : non-bloquant uniquement si explicitement demande.
#                     # Ne jamais appeler avant listen() -- race condition micro.
#                     t = threading.Thread(
#                         target=self._tts_engine.runAndWait, daemon=True
#                     )
#                     t.start()
#             except Exception as exc:
#                 logger.error("pyttsx3 erreur: %s", exc)
#                 print("[TTS] " + text)

#     # ------------------------------------------------------------------
#     # STT -- chunk VAD (narration continue)
#     # ------------------------------------------------------------------

#     # def listen_chunk(
#     #     self,
#     #     *,
#     #     pause_threshold:   float = STT_SILENCE_TIMEOUT,
#     #     phrase_time_limit: int   = STT_PHRASE_TIME_LIMIT,
#     #     listen_timeout:    float = STT_LISTEN_TIMEOUT,
#     # ) -> str:
#     #     """Capture un chunk de parole (VAD) et transcrit.

#     #     Returns:
#     #         Texte transcrit non-vide.

#     #     Raises:
#     #         RuntimeError: Capture ou transcription impossible.
#     #     """
#     #     import speech_recognition as sr

#     #     original = self._recognizer.pause_threshold
#     #     self._recognizer.pause_threshold = pause_threshold
#     #     tmp_path: Optional[str] = None

#     #     try:
#     #         with sr.Microphone() as src:
#     #             logger.info(
#     #                 "Ecoute chunk (silence=%.1fs, max=%ds)...",
#     #                 pause_threshold, phrase_time_limit,
#     #             )
#     #             self._recognizer.adjust_for_ambient_noise(src, duration=STT_AMBIENT_DURATION)
#     #             audio = self._recognizer.listen(
#     #                 src,
#     #                 timeout=listen_timeout,
#     #                 phrase_time_limit=phrase_time_limit,
#     #             )

#     #         with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
#     #             tmp_path = f.name
#     #             f.write(audio.get_wav_data())

#     #         if self.stt_backend == "whisper":
#     #             return self._transcribe_whisper(tmp_path)
#     #         else:
#     #             return self._transcribe_google(audio)

#     #     finally:
#     #         self._recognizer.pause_threshold = original
#     #         if tmp_path and os.path.exists(tmp_path):
#     #             try:
#     #                 os.unlink(tmp_path)
#     #             except OSError:
#     #                 pass
#     def listen_chunk(
#         self,
#         *,
#         pause_threshold:   float = STT_SILENCE_TIMEOUT,
#         phrase_time_limit: int   = STT_PHRASE_TIME_LIMIT,
#         listen_timeout:    float = STT_LISTEN_TIMEOUT,
#     ) -> str:
#         """Capture un chunk de parole (VAD) et transcrit.

#         Returns:
#             Texte transcrit non-vide.

#         Raises:
#             RuntimeError: Capture ou transcription impossible (y compris en cas de silence).
#         """
#         import speech_recognition as sr

#         original = self._recognizer.pause_threshold
#         self._recognizer.pause_threshold = pause_threshold
#         tmp_path: Optional[str] = None

#         try:
#             with sr.Microphone() as src:
#                 logger.info(
#                     "Ecoute chunk (silence=%.1fs, max=%ds)...",
#                     pause_threshold, phrase_time_limit,
#                 )
#                 self._recognizer.adjust_for_ambient_noise(src, duration=STT_AMBIENT_DURATION)
#                 audio = self._recognizer.listen(
#                     src,
#                     timeout=listen_timeout,
#                     phrase_time_limit=phrase_time_limit,
#                 )

#             with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
#                 tmp_path = f.name
#                 f.write(audio.get_wav_data())

#             if self.stt_backend == "whisper":
#                 return self._transcribe_whisper(tmp_path)
#             else:
#                 return self._transcribe_google(audio)

#         except sr.WaitTimeoutError as exc:
#             # On convertit le timeout d'attente en RuntimeError pour correspondre
#             # à l'interface attendue et gérée par les appelants.
#             raise RuntimeError("Aucun début de parole détecté (silence)") from exc

#         finally:
#             self._recognizer.pause_threshold = original
#             if tmp_path and os.path.exists(tmp_path):
#                 try:
#                     os.unlink(tmp_path)
#                 except OSError:
#                     pass
#     def listen_short(self, question: str, timeout: float = 8.0) -> str:
#         """Pose une question courte et attend une reponse breve.
#         Retourne la chaine vide en cas d'echec (pas de RuntimeError propagee).
#         """
#         self.speak(question)
#         self.speak(pick("listening"))
#         try:
#             return self.listen_chunk(
#                 pause_threshold=1.5,
#                 phrase_time_limit=15,
#                 listen_timeout=timeout,
#             )
#         except RuntimeError as exc:
#             logger.info("listen_short: pas de reponse (%s)", exc)
#             return ""

#     def _transcribe_whisper(self, wav_path: str) -> str:
#         segments_gen, info = self._whisper_model.transcribe(
#             wav_path,
#             language=self.language,
#             beam_size=WHISPER_BEAM_SIZE,
#         )
#         logger.debug(
#             "Whisper: langue=%s (%.0f%%)",
#             info.language, info.language_probability * 100,
#         )
#         text = " ".join(seg.text.strip() for seg in segments_gen).strip()
#         if not text:
#             raise RuntimeError("Whisper n'a produit aucun texte")
#         logger.info("STT chunk: '%s'", text[:100])
#         return text

#     def _transcribe_google(self, audio) -> str:
#         import speech_recognition as sr
#         lang = "fr-FR" if self.language == "fr" else (self.language + "-" + self.language.upper())
#         try:
#             text = self._recognizer.recognize_google(audio, language=lang)
#             logger.info("Google STT: '%s'", text[:100])
#             return text
#         except sr.UnknownValueError:
#             raise RuntimeError("Google STT: audio incomprehensible")
#         except sr.RequestError as exc:
#             raise RuntimeError("Google STT: erreur API: %s" % exc)

#     # ------------------------------------------------------------------
#     # Nettoyage
#     # ------------------------------------------------------------------

#     def close(self) -> None:
#         self._stop_audio()
#         if self._tts_engine is not None:
#             try:
#                 with self._lock_tts:
#                     self._tts_engine.stop()
#             except Exception:
#                 pass
#         logger.info("VoiceIO ferme")


# # ============================================================================
# # VRScenarioApp  -- orchestration principale
# # ============================================================================

# class VRScenarioApp:
#     """
#     Flux en deux phases :

#     PHASE 1 -- Generation et annonce du scenario
#       - Saisie vocale du theme
#       - LLM genere scenario_text + scenario_json structures
#       - Construction du ScenarioSession (signature reelle de vr_scenario_lib)
#       - TTS lit le resume_oral au naturel

#     PHASE 2 -- Questions / Reponses supervisees
#       - L'utilisateur pose des questions librement a voix haute
#       - discuss_scenario() repond via ScenarioSession.history
#       - SupervisorLLM evalue chaque echange : CONTINUER / CONSEIL / STOP
#       - EXIT word : cloture propre

#     Feedback de patience
#     ---------------------
#     Toute attente potentiellement longue (generation de scenario, appel LLM
#     en Q&R) est enveloppee par PatienceManager.run_with_patience(), qui pilote
#     earcons + phrases de transition selon la duree reelle d'attente.
#     """

#     def __init__(self, io: VoiceIO) -> None:
#         self.io = io
#         self.patience = PatienceManager(io)

#     def run(self) -> None:
#         self._welcome()
#         topic      = self._ask_topic()
#         config     = self._setup_llm()
#         supervisor = SupervisorLLM(config)

#         # -- Phase 1 : generation + annonce --------------------------------
#         scenario_session = self._generate_and_announce(topic, config)

#         # -- Phase 2 : Q&R supervisee --------------------------------------
#         self._qa_loop(scenario_session, supervisor, config)

#         self._goodbye()

#     # ------------------------------------------------------------------
#     # Phase 1 : generation du scenario
#     # ------------------------------------------------------------------

#     def _welcome(self) -> None:
#         print("\n" + "=" * 60)
#         print("  APPLICATION VOCALE -- SCENARIOS VR")
#         print("=" * 60)
#         self.io.speak(
#             "Bienvenue dans l'application vocale de scenarios VR. "
#             "Je vais generer un scenario a partir de votre theme, "
#             "vous en presenter les grandes lignes, "
#             "puis repondre a vos questions. "
#             "Dites fin pour terminer a tout moment."
#         )

#     def _ask_topic(self) -> str:
#         text = self.io.listen_short(
#             "Quel est le theme du scenario VR que vous souhaitez explorer ? "
#             "Par exemple : consignation gaz, securite incendie, premiers secours."
#         )
#         if not text:
#             text = "securite industrielle"
#             self.io.speak("Theme par defaut : securite industrielle.")
#         else:
#             self.io.speak("Theme retenu : " + text + ".")
#         logger.info("Theme : '%s'", text)
#         print("\nTheme : " + text)
#         return text

#     def _generate_and_announce(self, topic: str, config) -> "ScenarioSession | None":
#         """
#         Appelle le LLM pour generer scenario_text + scenario_json,
#         construit un ScenarioSession complet, lit le resume oral.
#         Retourne None si la generation echoue (Q&R desactivee).

#         La generation peut prendre plusieurs secondes : elle est enveloppee
#         par le PatienceManager pour masquer la latence percue (earcons +
#         phrases de transition automatiques selon la duree reelle).
#         """
#         print("\nGeneration en cours...")

#         scenario_json: Dict[str, Any] = {}
#         scenario_text: str = ""

#         def _do_generate():
#             nonlocal scenario_text, scenario_json
#             # -- Tentative via vr_scenario_lib --------------------------
#             try:
#                 from vr_scenario_lib.scenario import generate_scenario as lib_generate
#                 result = lib_generate(topic=topic, llm_config=config)
#                 # lib peut retourner (text, json_dict) ou un objet avec attributs
#                 if isinstance(result, tuple):
#                     scenario_text, scenario_json = result[0], result[1]
#                 else:
#                     scenario_text = getattr(result, "text", str(result))
#                     scenario_json = getattr(result, "json", {})
#                 logger.info("Scenario genere via vr_scenario_lib (%d car.)", len(scenario_text))

#             except Exception as exc:
#                 logger.warning("lib generate_scenario indisponible: %s -- fallback LLM direct", exc)
#                 scenario_json, scenario_text = self._generate_via_llm(topic, config)

#         # "Je prepare votre reponse." etc. seront emis automatiquement par
#         # le PatienceManager si la generation depasse les seuils de latence.
#         self.patience.run_with_patience(_do_generate)

#         if not scenario_json and not scenario_text:
#             self.io.speak(
#                 "La generation du scenario a echoue. "
#                 "Vous pouvez poser vos questions directement."
#             )
#             return None

#         # -- Construction du ScenarioSession --------------------------------
#         now = datetime.now(timezone.utc).isoformat()
#         try:
#             from vr_scenario_lib.scenario_store import ScenarioSession
#             session = ScenarioSession(
#                 scenario_id   = str(uuid.uuid4()),
#                 topic         = topic,
#                 scenario_text = scenario_text,
#                 scenario_json = scenario_json,
#                 created_at    = now,
#                 updated_at    = now,
#             )
#             logger.info("ScenarioSession cree (id=%s)", session.scenario_id)
#         except Exception as exc:
#             logger.warning("ScenarioSession impossible: %s -- session None", exc)
#             session = None

#         # -- Annonce vocale des grandes lignes ------------------------------
#         self._announce_scenario(scenario_json, scenario_text)
#         return session

#     def _generate_via_llm(
#         self, topic: str, config
#     ) -> "tuple[Dict[str, Any], str]":
#         """
#         Appel LLM direct pour generer scenario_json + scenario_text.
#         Retourne ({}, "") en cas d'echec.
#         """
#         if config is None:
#             return self._fallback_static_scenario(topic)

#         user_msg = "Genere un scenario de formation VR sur le theme : " + topic

#         try:
#             raw = self._call_llm_raw(
#                 system    = SCENARIO_GEN_SYSTEM,
#                 user      = user_msg,
#                 config    = config,
#                 max_tokens= SCENARIO_GEN_MAX_TOKENS,
#             )
#         except Exception as exc:
#             logger.error("LLM generation echec: %s", exc)
#             return self._fallback_static_scenario(topic)

#         # Parse JSON
#         try:
#             import re
#             m = re.search(r'\{.*\}', raw, re.DOTALL)
#             if not m:
#                 raise ValueError("JSON introuvable")
#             obj = json.loads(m.group())
#         except Exception as exc:
#             logger.error("Parse JSON scenario echec: %s | raw=%s", exc, raw[:200])
#             return self._fallback_static_scenario(topic)

#         # Construit scenario_text a partir du JSON
#         text = self._json_to_text(obj, topic)
#         return obj, text

#     @staticmethod
#     def _json_to_text(obj: Dict[str, Any], topic: str) -> str:
#         """Serialise scenario_json en texte lisible pour scenario_text."""
#         lines = ["# SCENARIO VR -- " + topic.upper(), ""]
#         titre = obj.get("titre", topic)
#         lines += ["## " + titre, ""]

#         objectifs = obj.get("objectifs", [])
#         if objectifs:
#             lines.append("### Objectifs")
#             for o in objectifs:
#                 lines.append("- " + str(o))
#             lines.append("")

#         for etape in obj.get("grandes_lignes", []):
#             num = etape.get("etape", "")
#             titre_e = etape.get("titre", "")
#             desc = etape.get("description", "")
#             lines.append("### Etape %s : %s" % (num, titre_e))
#             lines.append(desc)
#             lines.append("")

#         procs = obj.get("procedures_cles", [])
#         if procs:
#             lines.append("### Procedures cles")
#             for p in procs:
#                 lines.append("- " + str(p))
#             lines.append("")

#         vigilance = obj.get("points_vigilance", [])
#         if vigilance:
#             lines.append("### Points de vigilance")
#             for v in vigilance:
#                 lines.append("- " + str(v))
#             lines.append("")

#         return "\n".join(lines)

#     @staticmethod
#     def _fallback_static_scenario(topic: str) -> "tuple[Dict[str, Any], str]":
#         """Scenario minimal si le LLM est inaccessible."""
#         obj = {
#             "titre": "Scenario " + topic,
#             "objectifs": [
#                 "Comprendre les principes fondamentaux de " + topic,
#                 "Maitriser les procedures de securite essentielles",
#                 "Reagir correctement aux situations d'urgence",
#             ],
#             "grandes_lignes": [
#                 {"etape": 1, "titre": "Preparation",
#                  "description": "Verifier les equipements et les EPI avant toute intervention."},
#                 {"etape": 2, "titre": "Intervention",
#                  "description": "Appliquer les procedures standard en respectant les consignes."},
#                 {"etape": 3, "titre": "Cloture",
#                  "description": "Consigner les actions effectuees et signaler tout incident."},
#             ],
#             "procedures_cles": [
#                 "Verifier les equipements avant intervention",
#                 "Respecter les zones de securite",
#                 "Alerter la chaine hierarchique en cas d'incident",
#             ],
#             "points_vigilance": [
#                 "Ne jamais intervenir seul",
#                 "Toujours porter les EPI adaptes",
#             ],
#             "resume_oral": (
#                 "Ce scenario porte sur le theme " + topic + ". "
#                 "Il se deroule en trois etapes : la preparation du materiel, "
#                 "l'intervention selon les procedures standard, "
#                 "et la cloture avec consignation des actions effectuees."
#             ),
#         }
#         text = VRScenarioApp._json_to_text(obj, topic)
#         return obj, text

#     def _announce_scenario(self, scenario_json: Dict[str, Any], scenario_text: str) -> None:
#         """Lit les grandes lignes du scenario a voix haute."""
#         print("\n" + "=" * 60)
#         print("  SCENARIO GENERE")
#         print("=" * 60)
#         print(scenario_text[:1200] + ("..." if len(scenario_text) > 1200 else ""))

#         # Lecture TTS du resume_oral (optimise pour TTS, sans listes ni symboles)
#         resume = scenario_json.get("resume_oral", "")
#         if not resume:
#             # Fallback : construit un resume oral minimal depuis le JSON
#             titre = scenario_json.get("titre", "le scenario")
#             etapes = scenario_json.get("grandes_lignes", [])
#             if etapes:
#                 noms = ", ".join(
#                     str(e.get("titre", "")) for e in etapes[:4]
#                 )
#                 resume = (
#                     "Le scenario intitule " + titre + " se deroule en "
#                     + str(len(etapes)) + " etapes : " + noms + "."
#                 )
#             else:
#                 resume = "Le scenario " + titre + " vient d'etre genere."

#         self.io.speak("Voici les grandes lignes de votre scenario.")
#         self.io.speak(resume)

#         # Annonce des points de vigilance s'ils existent
#         vigilance = scenario_json.get("points_vigilance", [])
#         if vigilance:
#             # Construit une phrase fluide (pas de liste TTS)
#             points = " et ".join(vigilance[:3])
#             self.io.speak("Points de vigilance a retenir : " + points + ".")

#         self.io.speak(
#             "Le scenario est pret. "
#             "Vous pouvez maintenant me poser vos questions. "
#             "Dites fin pour terminer."
#         )

#     # ------------------------------------------------------------------
#     # Phase 2 : Q&R supervisee
#     # ------------------------------------------------------------------

#     def _qa_loop(
#         self,
#         scenario_session,   # ScenarioSession | None
#         supervisor: SupervisorLLM,
#         config,
#     ) -> None:
#         """Boucle de questions / reponses supervisees.

#         Gestion du silence utilisateur a trois niveaux :
#           1. silence leger      -> on continue d'ecouter sans rien dire
#                                     (le timeout de listen_chunk gere ca seul)
#           2. silence intermediaire (relance douce) -> apres le 1er timeout,
#                                     une phrase courte rassure sans interroger
#                                     explicitement l'utilisateur
#           3. silence prolonge / absence probable -> apres MAX_TIMEOUTS,
#                                     question explicite oui/non pour continuer
#                                     ou clore la session
#         """
#         print("\n" + "-" * 60)
#         print("[ SESSION Q&R -- posez vos questions ]")
#         print("-" * 60)

#         narrator = NarratorSession(
#             topic = scenario_session.topic if scenario_session else "general"
#         )
#         consecutive_timeouts = 0
#         MAX_TIMEOUTS  = 3
#         SOFT_NUDGE_AT = 1   # apres le 1er timeout : relance douce (niveau intermediaire)

#         while True:

#             # ---- 1. Capture de la question --------------------------------
#             self.io.speak(pick("listening"))
#             try:
#                 question = self.io.listen_chunk(
#                     pause_threshold   = STT_SILENCE_TIMEOUT,
#                     phrase_time_limit = STT_PHRASE_TIME_LIMIT,
#                     listen_timeout    = STT_LISTEN_TIMEOUT,
#                 )
#                 consecutive_timeouts = 0
#             except RuntimeError as exc:
#                 consecutive_timeouts += 1
#                 logger.info("Q&R timeout %d/%d: %s", consecutive_timeouts, MAX_TIMEOUTS, exc)

#                 if consecutive_timeouts >= MAX_TIMEOUTS:
#                     # Niveau 3 : silence prolonge / absence probable
#                     if self._ask_continue_qa():
#                         consecutive_timeouts = 0
#                     else:
#                         break
#                 elif consecutive_timeouts == SOFT_NUDGE_AT:
#                     # Niveau 2 : relance douce, sans interroger explicitement
#                     self.io.speak(pick("soft_nudge"))
#                 # Niveau 1 (silence leger, 1er timeout non atteint) : rien,
#                 # on relance simplement l'ecoute au tour suivant.
#                 continue

#             # ---- 2. Detection sortie --------------------------------------
#             if any(w in question.lower() for w in EXIT_WORDS):
#                 print("\nSortie Q&R : '%s'" % question)
#                 break

#             print("\n[Question] " + question)
#             narrator.add_chunk(question)

#             # ---- 3. Reponse LLM via ScenarioSession (avec patience) -------
#             answer = self.patience.run_with_patience(
#                 self._get_answer, question, scenario_session, config
#             )
#             print("[Reponse] " + answer)
#             self.io.speak(answer)

#             # ---- 4. Supervision de l'echange ------------------------------
#             exchange = "Q : " + question + "\nR : " + answer
#             decision = supervisor.analyse(narrator, exchange)
#             logger.info(
#                 "Superviseur Q&R: %s | '%s'",
#                 decision.decision.value,
#                 decision.message[:60] if decision.message else "",
#             )

#             if decision.decision == Decision.CONSEIL:
#                 print("\n[CONSEIL] " + decision.message)
#                 self.io.speak(decision.message)

#             elif decision.decision == Decision.STOP:
#                 print("\n[STOP] " + decision.message)
#                 self.io.interrupt_and_speak(decision.message)
#                 if not self._handle_stop_qa():
#                     break

#     def _get_answer(self, question: str, scenario_session, config) -> str:
#         """
#         Obtient une reponse LLM a la question posee.
#         Priorite : discuss_scenario() de vr_scenario_lib, puis LLM direct, puis fallback.
#         """
#         # -- Via vr_scenario_lib -------------------------------------------
#         if scenario_session is not None and config is not None:
#             try:
#                 from vr_scenario_lib.scenario import discuss_scenario
#                 reply = discuss_scenario(
#                     session      = scenario_session,
#                     user_message = question,
#                     llm_config   = config,
#                 )
#                 if reply and reply.strip():
#                     return reply.strip()
#             except Exception as exc:
#                 logger.warning("discuss_scenario erreur: %s -- fallback LLM direct", exc)

#         # -- LLM direct avec contexte scenario_text -------------------------
#         if config is not None:
#             context = (
#                 scenario_session.scenario_text[:800]
#                 if scenario_session and scenario_session.scenario_text
#                 else ""
#             )
#             user_msg = (
#                 ("Contexte du scenario :\n" + context + "\n\n" if context else "")
#                 + "Question de l'apprenant : " + question
#             )
#             try:
#                 return self._call_llm_raw(
#                     system    = QA_SYSTEM,
#                     user      = user_msg,
#                     config    = config,
#                     max_tokens= QA_MAX_TOKENS,
#                 ).strip()
#             except Exception as exc:
#                 logger.error("LLM direct Q&R erreur: %s", exc)

#         return "Je n'ai pas pu obtenir de reponse. Consultez la documentation du scenario."

#     # ------------------------------------------------------------------
#     # Helpers generaux
#     # ------------------------------------------------------------------

#     @staticmethod
#     def _call_llm_raw(*, system: str, user: str, config, max_tokens: int) -> str:
#         """Appel LLM unifie : vr_scenario_lib puis HTTP direct (OpenAI-compatible)."""
#         try:
#             from vr_scenario_lib.llm import call_llm
#             return call_llm(
#                 system=system, user=user,
#                 llm_config=config, max_tokens=max_tokens,
#             )
#         except ImportError:
#             pass

#         import urllib.request
#         payload = json.dumps({
#             "model":      getattr(config, "model", "gpt-3.5-turbo"),
#             "max_tokens": max_tokens,
#             "messages":   [
#                 {"role": "system", "content": system},
#                 {"role": "user",   "content": user},
#             ],
#         }).encode()
#         api_url = getattr(config, "api_url", "https://api.openai.com/v1/chat/completions")
#         token   = getattr(config, "token", "")
#         req = urllib.request.Request(
#             api_url, data=payload,
#             headers={
#                 "Content-Type":  "application/json",
#                 "Authorization": "Bearer " + token,
#             },
#         )
#         with urllib.request.urlopen(req, timeout=20) as resp:
#             data = json.loads(resp.read())
#         return data["choices"][0]["message"]["content"]

#     def _ask_continue_qa(self) -> bool:
#         text = self.io.listen_short(pick("no_response_continue_check"))
#         if not text:
#             return False
#         return any(w in text.lower() for w in {"oui", "yes", "continuer", "continue", "si"})

#     def _handle_stop_qa(self) -> bool:
#         """Pause apres STOP en phase Q&R. Retourne True pour reprendre."""
#         self.io.speak(
#             "La session est interrompue. "
#             "Dites reprendre pour continuer, ou fin pour terminer."
#         )
#         text = ""
#         try:
#             text = self.io.listen_chunk(
#                 pause_threshold=2.0,
#                 phrase_time_limit=10,
#                 listen_timeout=12,
#             )
#         except RuntimeError:
#             pass
#         if any(w in text.lower() for w in {"reprendre", "continuer", "oui", "yes"}):
#             self.io.speak("Tres bien. Continuez vos questions.")
#             return True
#         return False

#     def _goodbye(self) -> None:
#         self.io.speak("Merci pour cette session. A bientot !")
#         print("\nAu revoir !\n")

#     # ------------------------------------------------------------------
#     # LLM setup
#     # ------------------------------------------------------------------

#     def _setup_llm(self):
#         try:
#             from vr_scenario_lib.config import build_llm_config
#             return build_llm_config()
#         except Exception as exc:
#             logger.warning(
#                 "LLM config non disponible: %s -- mode degrade (scenarios statiques)", exc
#             )
#             return None


# # ============================================================================
# # CLI
# # ============================================================================

# def _parse_args() -> argparse.Namespace:
#     p = argparse.ArgumentParser(
#         description="Application vocale de supervision de scenarios VR",
#         formatter_class=argparse.ArgumentDefaultsHelpFormatter,
#     )
#     p.add_argument(
#         "--stt-backend", default="whisper", choices=["whisper", "google"],
#         help="Backend STT.",
#     )
#     p.add_argument(
#         "--tts-backend", default=TTS_DEFAULT_BACKEND,
#         choices=["coqui", "piper", "gtts", "pyttsx3"],
#         help="Backend TTS. 'coqui' et 'piper' sont 100%% offline et francais natif.",
#     )
#     p.add_argument(
#         "--language", default="fr",
#         help="Code langue ISO 639-1 (fr par defaut).",
#     )
#     p.add_argument(
#         "--whisper-model", default=WHISPER_DEFAULT_MODEL,
#         choices=["tiny", "base", "small", "medium", "large"],
#         help="Taille du modele Whisper. 'small' recommande pour le francais.",
#     )
#     p.add_argument(
#         "--coqui-model", default=COQUI_MODEL_FR,
#         help="Identifiant modele Coqui TTS.",
#     )
#     p.add_argument(
#         "--piper-model", default=PIPER_MODEL_FR,
#         help="Nom du modele Piper (ex: fr_FR-tom-medium).",
#     )
#     p.add_argument(
#         "--debug", action="store_true",
#         help="Active le logging DEBUG.",
#     )
#     return p.parse_args()


# def main() -> None:
#     args = _parse_args()
#     if args.debug:
#         logging.getLogger().setLevel(logging.DEBUG)

#     io = VoiceIO(
#         stt_backend   = args.stt_backend,
#         tts_backend   = args.tts_backend,
#         language      = args.language,
#         whisper_model = args.whisper_model,
#         coqui_model   = args.coqui_model,
#         piper_model   = args.piper_model,
#     )
#     app = VRScenarioApp(io)
#     try:
#         app.run()
#     except KeyboardInterrupt:
#         print("\nInterruption utilisateur.")
#     finally:
#         io.close()


# if __name__ == "__main__":
#     main()














































# """
# Application vocale de supervision de scénarios de formation en réalité virtuelle.
# Version entreprise — standards industriels.

# RÔLE DE L'APPLICATION
# ----------------------
# L'utilisateur décrit librement un scénario de réalité virtuelle à voix haute.
# L'application écoute en continu, transcrit par fragments avec détection de voix,
# et soumet chaque fragment à un superviseur linguistique qui peut :
#   - CONTINUER  : rester silencieux (écoute neutre)
#   - CONSEIL    : intervenir poliment pour formuler un conseil
#   - STOP       : interrompre fermement pour signaler une erreur critique

# Architecture
# ------------
# VoiceIO          : reconnaissance vocale (Faster Whisper + VAD SpeechRecognition) + synthèse vocale française native.
# SupervisorLLM    : analyse chaque fragment, décide CONTINUER / CONSEIL / STOP.
# NarratorSession  : accumule la transcription, maintient le contexte du scénario.
# VRScenarioApp    : orchestration métier (initialisation + boucle de narration supervisée).
# PatienceManager  : retour sonore pendant les temps de traitement (signaux d'ambiance + phrases de transition).

# Moteurs de synthèse vocale française (ordre de priorité automatique)
# --------------------------------------------------------------------
# 1. coqui   -- Coqui VITS tts_models/fr/mai/tacotron2-DDC : voix neurale hors ligne, haute qualité
# 2. piper   -- Piper fr_FR-tom-medium                      : voix neurale hors ligne, très rapide
# 3. gtts    -- Google Synthèse vocale                      : voix en ligne, qualité maximale
# 4. pyttsx3 -- espeak-fr                                   : synthèse de base, sans dépendances

# Usage :
#     python app_vocal.py                            # détection automatique du meilleur moteur disponible
#     python app_vocal.py --tts-backend coqui        # Coqui VITS (hors ligne, haute qualité)
#     python app_vocal.py --tts-backend piper        # Piper (hors ligne, très rapide)
#     python app_vocal.py --tts-backend gtts         # Google Synthèse vocale (en ligne)
#     python app_vocal.py --stt-backend google       # Google Reconnaissance vocale (en ligne)
#     python app_vocal.py --whisper-model small      # meilleure précision de reconnaissance
#     python app_vocal.py --debug                    # journaux de débogage complets
# """

# from __future__ import annotations

# import argparse
# import json
# import logging
# import math
# import os
# import random
# import struct
# import sys
# import tempfile
# import threading
# import time
# import uuid
# from dataclasses import dataclass, field
# from datetime import datetime, timezone
# from enum import Enum
# from typing import Any, Dict, List, Optional

# # ---------------------------------------------------------------------------
# # Journalisation
# # ---------------------------------------------------------------------------
# logging.basicConfig(
#     level=logging.INFO,
#     format="%(asctime)s | %(name)-36s | %(levelname)-8s | %(message)s",
#     datefmt="%H:%M:%S",
# )
# logger = logging.getLogger(__name__)

# sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# # ============================================================================
# # Constantes
# # ============================================================================

# STT_LISTEN_TIMEOUT    = 8
# STT_PHRASE_TIME_LIMIT = 20          # durée maximale d'un fragment de narration
# STT_SILENCE_TIMEOUT   = 2.0         # silence détecté → fin du fragment
# STT_AMBIENT_DURATION  = 0.5
# TTS_SPEECH_RATE       = 145
# TTS_VOLUME            = 0.92
# WHISPER_DEFAULT_MODEL = "base"
# WHISPER_BEAM_SIZE     = 5

# # Mots déclencheurs de fin de session
# # Rédigés pour être naturels à l'oral et fiables à la transcription
# EXIT_WORDS = {"quitter", "terminer", "au revoir", "fin", "arrêter", "c'est tout"}

# # Moteurs de synthèse vocale française native
# TTS_DEFAULT_BACKEND   = "coqui"
# TTS_FALLBACK_CHAIN    = ["coqui", "piper", "gtts", "pyttsx3"]

# # Coqui : voix féminine Maï, accent français métropolitain soigné
# COQUI_MODEL_FR    = "tts_models/fr/mai/tacotron2-DDC"
# COQUI_SAMPLE_RATE = 22050

# # Piper : voix masculine Tom, accent français métropolitain naturel
# PIPER_MODEL_FR    = "fr_FR-tom-medium"
# PIPER_SAMPLE_RATE = 22050

# # Superviseur — instructions système
# SUPERVISOR_MAX_TOKENS = 256
# SUPERVISOR_SYSTEM = (
#     "Tu es un superviseur expert en sécurité de la réalité virtuelle et en procédures industrielles. "
#     "L'utilisateur décrit à voix haute un scénario de formation en réalité virtuelle. "
#     "Tu reçois des fragments de sa narration en temps réel.\n\n"
#     "Analyse le dernier fragment dans son contexte et réponds UNIQUEMENT avec un objet JSON :\n"
#     '{"decision": "CONTINUER" | "CONSEIL" | "STOP", "message": "<texte à dire, vide si CONTINUER>"}\n\n'
#     "Règles strictes :\n"
#     "- CONTINUER  : narration correcte, cohérente, sans danger. Message vide obligatoire.\n"
#     "- CONSEIL    : amélioration possible. Message court, positif, concret. Deux phrases maximum.\n"
#     "- STOP       : erreur critique de procédure, danger réel, incohérence grave. "
#     "Message direct et précis. Commence par 'Attention : '.\n"
#     "Ne jamais inventer de contexte non mentionné. Rester factuel."
# )

# # Génération de scénario — instructions système
# SCENARIO_GEN_MAX_TOKENS = 1024
# SCENARIO_GEN_SYSTEM = (
#     "Tu es un expert en conception de scénarios de formation en réalité virtuelle industrielle. "
#     "À partir d'un thème, génère un scénario structuré en JSON uniquement, sans aucun texte avant ou après.\n\n"
#     "Format JSON attendu (respecte exactement ces clés) :\n"
#     '{\n'
#     '  "titre": "Titre court du scénario",\n'
#     '  "objectifs": ["objectif 1", "objectif 2", "objectif 3"],\n'
#     '  "grandes_lignes": [\n'
#     '    {"etape": 1, "titre": "Titre de l\'étape", "description": "Description concise"},\n'
#     '    ...\n'
#     '  ],\n'
#     '  "procedures_cles": ["procédure 1", "procédure 2"],\n'
#     '  "points_vigilance": ["point 1", "point 2"],\n'
#     '  "resume_oral": "Texte fluide de trois à quatre phrases pour lecture vocale. Pas de listes, pas de symboles."\n'
#     '}\n\n'
#     "Le champ resume_oral doit être lisible à voix haute sans aucun accroc : pas de tirets, "
#     "pas de parenthèses, pas d'abréviations, pas de sigles. Quatre phrases au maximum."
# )

# # Questions-réponses — instructions système
# QA_MAX_TOKENS = 512
# QA_SYSTEM = (
#     "Tu es un formateur expert qui aide un apprenant à comprendre un scénario de formation en réalité virtuelle. "
#     "Tu réponds aux questions en t'appuyant exclusivement sur le scénario fourni. "
#     "Tes réponses sont courtes, claires, et conçues pour la lecture à voix haute : "
#     "deux ou trois phrases au maximum, pas de listes, pas de tirets, pas de symboles. "
#     "Parle directement à l'apprenant, avec chaleur et précision."
# )


# # ============================================================================
# # Bibliothèque de phrases système
# # ----------------------------------------------------------------------------
# # Chaque entrée regroupe plusieurs formulations d'une même situation récurrente.
# # La fonction pick() tire une variante aléatoire à chaque appel, ce qui réduit
# # sensiblement la fatigue auditive lors de longues sessions.
# #
# # Principes de rédaction appliqués :
# #   - Phrases courtes, musicalité naturelle, rythme parlé
# #   - Pas de sigles ni d'anglicismes difficiles à prononcer
# #   - Pas de virgules superflues (pause TTS mal placée)
# #   - Finales ouvertes ou légèrement montantes (intonation invitante)
# #   - Chaleur professionnelle — ni trop formel ni trop familier
# # ============================================================================

# CACHED_PHRASES_FR: Dict[str, List[str]] = {

#     # Invitation à parler — brève, neutre, non répétitive
#     "listening": [
#         "Je vous écoute.",
#         "À vous.",
#         "Allez-y.",
#         "Je suis prêt.",
#         "La parole est à vous.",
#     ],

#     # Accusé de réception très court
#     "ack_short": [
#         "Bien reçu.",
#         "Compris.",
#         "Noté.",
#         "Entendu.",
#     ],

#     # Attente courte (1 à 3 secondes) — rien de verbal, juste un signal d'ambiance
#     # Ces phrases ne sont pas utilisées directement : le niveau 1 est traité
#     # uniquement par earcon, sans parole, pour ne pas alourdir les courtes attentes.
#     "thinking_short": [
#         "Un instant.",
#         "Je vérifie.",
#     ],

#     # Attente moyenne (3 à 10 secondes) — une phrase rassurante, pas d'explication
#     "thinking_medium": [
#         "Je prépare votre réponse.",
#         "Je consulte le scénario.",
#         "Je rassemble les éléments.",
#         "Je cherche la bonne information.",
#         "Je réfléchis à votre question.",
#     ],

#     # Attente longue (10 à 20 secondes) — on reconnaît que ça prend du temps
#     "thinking_long": [
#         "La question est détaillée, je finalise ma réponse.",
#         "Cela demande un peu plus de réflexion. Je suis sur le sujet.",
#         "Je creuse la question. Encore un court instant.",
#         "Je vérifie tous les éléments. Merci de votre patience.",
#     ],

#     # Attente très longue (au-delà de 20 secondes) — ton calme, pas d'alarme
#     "thinking_very_long": [
#         "Je suis toujours en train de traiter votre demande.",
#         "Le traitement prend un peu plus de temps que prévu. Je reste sur le sujet.",
#         "Toujours en cours. Je reviens vers vous très bientôt.",
#     ],

#     # Relance douce après un premier silence — sans interroger explicitement
#     "soft_nudge": [
#         "Je reste disponible si vous avez une question.",
#         "Prenez votre temps. Je vous écoute quand vous êtes prêt.",
#         "Pas de précipitation. Je suis là.",
#         "Vous pouvez continuer quand vous le souhaitez.",
#     ],

#     # Question explicite après un silence prolongé (oui / non)
#     "no_response_continue_check": [
#         "Je n'entends plus rien. Souhaitez-vous continuer la session ? "
#         "Dites oui pour continuer, ou non pour terminer.",
#         "Il y a un long silence. Voulez-vous poursuivre ? "
#         "Répondez oui ou non.",
#     ],
# }


# def pick(key: str) -> str:
#     """Tire aléatoirement une variante de phrase système pour réduire la répétition."""
#     options = CACHED_PHRASES_FR.get(key)
#     if not options:
#         return ""
#     return random.choice(options)


# # ============================================================================
# # Décision + NarratorSession
# # ============================================================================

# class Decision(Enum):
#     CONTINUER = "CONTINUER"
#     CONSEIL   = "CONSEIL"
#     STOP      = "STOP"


# @dataclass
# class SupervisorDecision:
#     decision: Decision = Decision.CONTINUER
#     message:  str      = ""

#     def must_speak(self) -> bool:
#         return self.decision in (Decision.CONSEIL, Decision.STOP)


# @dataclass
# class NarratorSession:
#     """Accumule la transcription et maintient le contexte pour le superviseur."""
#     topic:     str
#     chunks:    List[str] = field(default_factory=list)
#     full_text: str       = ""

#     def add_chunk(self, text: str) -> None:
#         self.chunks.append(text)
#         self.full_text = " ".join(self.chunks)

#     def context_window(self, n: int = 5) -> str:
#         return " ".join(self.chunks[-n:])

#     def summary(self) -> str:
#         return "%d séquence(s), environ %d mots" % (len(self.chunks), len(self.full_text.split()))


# # ============================================================================
# # PatienceManager — retour sonore pendant les temps de traitement
# # ----------------------------------------------------------------------------
# # Stratégie à paliers calibrée sur la durée d'attente réelle :
# #
# #   Moins de 1 s    : rien (imperceptible)
# #   De 1 à 3 s      : signal d'ambiance discret seul (pas de phrase —
# #                     évite la surcharge verbale sur les attentes courantes)
# #   De 3 à 10 s     : signal d'ambiance + courte phrase de transition
# #   Au-delà de 10 s : signal grave + phrase "longue attente", puis rappel
# #                     toutes les 12 s pour éviter le silence total anxiogène
# #
# # Le suivi tourne dans un fil d'exécution dédié pendant l'appel bloquant
# # au modèle de langage. Il s'arrête proprement (threading.Event) dès que
# # le résultat est disponible.
# # ============================================================================

# class PatienceManager:
#     """Pilote les signaux d'ambiance et les phrases de patience selon la durée réelle d'attente."""

#     LEVEL_SHORT_S     = 1.0    # moins de 1 s : rien
#     LEVEL_MEDIUM_S    = 3.0    # 1 à 3 s : signal seul
#     LEVEL_LONG_S      = 10.0   # 3 à 10 s : signal + phrase courte
#     LEVEL_VERY_LONG_S = 20.0   # au-delà de 10 s : signal grave + phrase longue

#     def __init__(self, io: "VoiceIO") -> None:
#         self.io = io
#         self._stop_event = threading.Event()
#         self._thread: Optional[threading.Thread] = None

#     def start(self) -> None:
#         self._stop_event.clear()
#         self._thread = threading.Thread(target=self._run, daemon=True)
#         self._thread.start()

#     def stop(self) -> None:
#         self._stop_event.set()
#         if self._thread is not None:
#             self._thread.join(timeout=2.0)
#             self._thread = None

#     def _run(self) -> None:
#         start = time.monotonic()
#         announced_medium    = False
#         announced_long      = False
#         announced_very_long = False

#         while not self._stop_event.is_set():
#             elapsed = time.monotonic() - start

#             if elapsed >= self.LEVEL_MEDIUM_S and not announced_medium:
#                 announced_medium = True
#                 self.io.play_earcon("patience_short")

#             if elapsed >= self.LEVEL_LONG_S and not announced_long:
#                 announced_long = True
#                 self.io.play_earcon("patience_medium")
#                 self.io.speak(pick("thinking_medium"), blocking=False)

#             if elapsed >= self.LEVEL_VERY_LONG_S and not announced_very_long:
#                 announced_very_long = True
#                 self.io.play_earcon("patience_long")
#                 self.io.speak(pick("thinking_long"), blocking=False)

#             # Rappel périodique au-delà du seuil très long
#             if announced_very_long and elapsed >= self.LEVEL_VERY_LONG_S + 12.0:
#                 self.io.speak(pick("thinking_very_long"), blocking=False)
#                 start -= 12.0  # reprogramme le prochain rappel dans 12 s

#             self._stop_event.wait(timeout=0.25)

#     def run_with_patience(self, fn, *args, **kwargs):
#         """Exécute fn(*args, **kwargs) en pilotant le retour sonore de patience."""
#         self.start()
#         try:
#             return fn(*args, **kwargs)
#         finally:
#             self.stop()


# # ============================================================================
# # SupervisorLLM
# # ============================================================================

# class SupervisorLLM:
#     """Analyse les fragments de narration et produit des décisions de supervision."""

#     def __init__(self, config) -> None:
#         self._config = config
#         self._lock   = threading.Lock()

#     def analyse(self, session: NarratorSession, new_chunk: str) -> SupervisorDecision:
#         if self._config is None:
#             return SupervisorDecision()

#         user_msg = (
#             "Thème du scénario : %s\n\n"
#             "Contexte (narration précédente) :\n%s\n\n"
#             "Nouveau fragment :\n%s"
#         ) % (session.topic, session.context_window(), new_chunk)

#         try:
#             with self._lock:
#                 raw = self._call_llm(user_msg)
#             return self._parse(raw)
#         except Exception as exc:
#             logger.warning("SupervisorLLM erreur : %s", exc)
#             return SupervisorDecision()

#     def _call_llm(self, user_msg: str) -> str:
#         # Tentative via la bibliothèque de scénarios
#         try:
#             from vr_scenario_lib.llm import call_llm
#             return call_llm(
#                 system=SUPERVISOR_SYSTEM,
#                 user=user_msg,
#                 llm_config=self._config,
#                 max_tokens=SUPERVISOR_MAX_TOKENS,
#             )
#         except ImportError:
#             pass

#         # Appel direct compatible avec l'interface de l'API de langage
#         import json
#         import urllib.request

#         payload = json.dumps({
#             "model":      getattr(self._config, "model", "gpt-3.5-turbo"),
#             "max_tokens": SUPERVISOR_MAX_TOKENS,
#             "messages":   [
#                 {"role": "system", "content": SUPERVISOR_SYSTEM},
#                 {"role": "user",   "content": user_msg},
#             ],
#         }).encode()
#         api_url = getattr(self._config, "api_url", "https://api.openai.com/v1/chat/completions")
#         token   = getattr(self._config, "token", "")
#         req = urllib.request.Request(
#             api_url,
#             data=payload,
#             headers={
#                 "Content-Type":  "application/json",
#                 "Authorization": "Bearer " + token,
#             },
#         )
#         with urllib.request.urlopen(req, timeout=15) as resp:
#             data = json.loads(resp.read())
#         return data["choices"][0]["message"]["content"]

#     def _parse(self, raw: str) -> SupervisorDecision:
#         import json
#         import re
#         m = re.search(r'\{.*\}', raw, re.DOTALL)
#         if not m:
#             logger.warning("SupervisorLLM : structure JSON introuvable dans '%s'", raw[:120])
#             return SupervisorDecision()
#         obj = json.loads(m.group())
#         try:
#             dec = Decision(obj.get("decision", "CONTINUER").upper())
#         except ValueError:
#             dec = Decision.CONTINUER
#         return SupervisorDecision(decision=dec, message=obj.get("message", "").strip())


# # ============================================================================
# # VoiceIO
# # ============================================================================

# class VoiceIO:
#     """Couche basse — reconnaissance vocale et synthèse vocale.

#     Principes fondamentaux
#     ----------------------
#     1. speak() est TOUJOURS bloquant dans le fil principal.
#        Une synthèse non bloquante avant écoute = écho capturé par le moteur de
#        reconnaissance.
#     2. Le microphone n'est jamais ouvert pendant la synthèse vocale.
#     3. L'enregistrement utilise la détection automatique de voix, pas une durée fixe.
#     4. interrupt_and_speak() coupe l'audio en cours avant de parler (alertes STOP).
#     5. play_earcon() est toujours non bloquant et très court (moins de 400 ms) :
#        il ne doit jamais retarder le flux conversationnel.
#     """

#     def __init__(
#         self,
#         stt_backend:   str = "whisper",
#         tts_backend:   str = TTS_DEFAULT_BACKEND,
#         language:      str = "fr",
#         whisper_model: str = WHISPER_DEFAULT_MODEL,
#         coqui_model:   str = COQUI_MODEL_FR,
#         piper_model:   str = PIPER_MODEL_FR,
#     ) -> None:
#         self.stt_backend      = stt_backend
#         self.tts_backend      = tts_backend
#         self.language         = language
#         self.whisper_model_id = whisper_model
#         self.coqui_model_id   = coqui_model
#         self.piper_model_id   = piper_model

#         self._recognizer    = None
#         self._whisper_model = None
#         self._tts_engine    = None
#         self._coqui_model   = None
#         self._lock_tts      = threading.Lock()

#         self._init()

#     # ------------------------------------------------------------------
#     # Initialisation
#     # ------------------------------------------------------------------

#     def _init(self) -> None:
#         self._init_stt()
#         self._init_tts()
#         logger.info(
#             "VoiceIO prêt — Reconnaissance : %s | Synthèse : %s | Langue : %s",
#             self.stt_backend, self.tts_backend, self.language,
#         )

#     def _init_stt(self) -> None:
#         try:
#             import speech_recognition as sr
#             self._recognizer = sr.Recognizer()
#             self._recognizer.energy_threshold         = 4000
#             self._recognizer.pause_threshold          = STT_SILENCE_TIMEOUT
#             self._recognizer.dynamic_energy_threshold = True
#         except ImportError:
#             raise RuntimeError(
#                 "Module SpeechRecognition manquant. "
#                 "Installez-le avec : pip install SpeechRecognition PyAudio"
#             )
#         if self.stt_backend == "whisper":
#             self._whisper_model = self._load_whisper()

#     def _load_whisper(self) -> object:
#         try:
#             from faster_whisper import WhisperModel
#             logger.info("Chargement du modèle Faster Whisper '%s'...", self.whisper_model_id)
#             model = WhisperModel(
#                 self.whisper_model_id,
#                 device="cpu",
#                 compute_type="int8",
#             )
#             logger.info("Faster Whisper prêt")
#             return model
#         except ImportError:
#             raise RuntimeError(
#                 "Module faster-whisper manquant. Installez-le avec : pip install faster-whisper"
#             )

#     def _init_tts(self) -> None:
#         chain = (
#             [self.tts_backend]
#             + [b for b in TTS_FALLBACK_CHAIN if b != self.tts_backend]
#         )
#         for backend in chain:
#             try:
#                 if backend == "coqui":
#                     self._init_coqui()
#                 elif backend == "piper":
#                     self._init_piper()
#                 elif backend == "gtts":
#                     self._init_gtts()
#                 elif backend == "pyttsx3":
#                     self._init_pyttsx3()
#                 else:
#                     continue
#                 self.tts_backend = backend
#                 logger.info("Moteur de synthèse actif : %s", backend)
#                 return
#             except Exception as exc:
#                 logger.warning(
#                     "Moteur '%s' indisponible : %s — essai du suivant", backend, exc
#                 )

#         raise RuntimeError(
#             "Aucun moteur de synthèse vocale disponible. "
#             "Installez au minimum : pip install coqui-tts sounddevice soundfile"
#         )

#     # ------------------------------------------------------------------
#     # Initialisation Coqui VITS — voix neurale française hors ligne
#     # ------------------------------------------------------------------

#     def _init_coqui(self) -> None:
#         try:
#             from TTS.api import TTS as CoquiTTS
#             import sounddevice  # noqa: F401
#             import soundfile    # noqa: F401
#         except ImportError:
#             raise RuntimeError(
#                 "Module Coqui manquant. Installez-le avec : pip install coqui-tts sounddevice soundfile"
#             )
#         logger.info("Chargement de Coqui '%s'...", self.coqui_model_id)
#         self._coqui_model = CoquiTTS(
#             model_name=self.coqui_model_id,
#             progress_bar=False,
#             gpu=False,
#         )
#         logger.info("Coqui prêt")

#     # ------------------------------------------------------------------
#     # Initialisation Piper — voix neurale française hors ligne, très rapide
#     # ------------------------------------------------------------------

#     def _init_piper(self) -> None:
#         try:
#             import piper  # noqa: F401
#         except ImportError:
#             raise RuntimeError("Module piper-tts manquant. Installez-le avec : pip install piper-tts")
#         logger.info("Piper disponible — modèle '%s'", self.piper_model_id)

#     # ------------------------------------------------------------------
#     # Initialisation Google Synthèse vocale — en ligne
#     # ------------------------------------------------------------------

#     def _init_gtts(self) -> None:
#         try:
#             import gtts    # noqa: F401
#             import pygame  # noqa: F401
#         except ImportError:
#             raise RuntimeError(
#                 "Modules gTTS ou pygame manquants. Installez-les avec : pip install gTTS pygame"
#             )
#         logger.info("Google Synthèse vocale initialisée")

#     # ------------------------------------------------------------------
#     # Initialisation pyttsx3 — solution de secours ultime
#     # ------------------------------------------------------------------

#     def _init_pyttsx3(self) -> None:
#         try:
#             import pyttsx3
#         except ImportError:
#             raise RuntimeError(
#                 "Module pyttsx3 manquant. Installez-le avec : pip install pyttsx3"
#             )

#         engine = pyttsx3.init()
#         engine.setProperty("rate",   TTS_SPEECH_RATE)
#         engine.setProperty("volume", TTS_VOLUME)

#         fr_voice_found = False
#         # Priorité 1 : voix fr_FR espeak-ng (accent français métropolitain)
#         # Priorité 2 : toute voix contenant "french" ou "fr" dans le nom ou l'identifiant
#         for priority in ("fr_FR", "fr-FR", "french", "fr"):
#             for v in engine.getProperty("voices"):
#                 name_lower = v.name.lower()
#                 id_lower   = v.id.lower()
#                 if priority.lower() in id_lower or priority.lower() in name_lower:
#                     engine.setProperty("voice", v.id)
#                     logger.info(
#                         "pyttsx3 : voix française sélectionnée : %s (%s)", v.name, v.id
#                     )
#                     fr_voice_found = True
#                     break
#             if fr_voice_found:
#                 break

#         if not fr_voice_found:
#             logger.warning(
#                 "Aucune voix française trouvée dans pyttsx3. "
#                 "Sur Linux : sudo apt install espeak-ng-data"
#             )

#         self._tts_engine = engine
#         logger.info("pyttsx3 initialisé (voix système)")

#     # ------------------------------------------------------------------
#     # Synthèse vocale — TOUJOURS bloquante dans le fil principal
#     # ------------------------------------------------------------------

#     def interrupt_and_speak(self, text: str) -> None:
#         """Coupe l'audio en cours PUIS parle. Réservé aux alertes STOP urgentes."""
#         self._stop_audio()
#         self.speak(text)

#     def _stop_audio(self) -> None:
#         """Arrête immédiatement la lecture audio (tous moteurs)."""
#         try:
#             if self.tts_backend in ("coqui", "piper"):
#                 import sounddevice as sd
#                 sd.stop()
#             elif self.tts_backend == "gtts":
#                 try:
#                     import pygame
#                     if pygame.mixer.get_init():
#                         pygame.mixer.music.stop()
#                 except Exception:
#                     pass
#         except Exception as exc:
#             logger.debug("_stop_audio : %s", exc)

#     @staticmethod
#     def _sanitize_tts(text: str) -> str:
#         """Nettoie le texte avant synthèse vocale.

#         Transformations appliquées dans l'ordre :
#         1. Blocs de code Markdown (``` … ```) → supprimés
#         2. Emphase Markdown (* ** _ __ ~ ~~)  → supprimée (le texte reste)
#         3. Titres Markdown (# ## ###…)         → supprimés (le texte reste)
#         4. Adresses web (http / https / ftp)   → remplacées par « lien »
#         5. Ponctuation non orale               → remplacée ou supprimée
#         6. Espaces multiples et lignes vides   → normalisés
#         """
#         import re

#         # 1. Blocs de code (``` … ```) et code en ligne (` … `)
#         text = re.sub(r'```.*?```', '', text, flags=re.DOTALL)
#         text = re.sub(r'`[^`]*`', '', text)

#         # 2. Emphase Markdown
#         text = re.sub(r'\*{1,3}|_{1,3}|~{1,2}', '', text)

#         # 3. Titres Markdown en début de ligne
#         text = re.sub(r'^\s*#{1,6}\s*', '', text, flags=re.MULTILINE)

#         # 4. Adresses web
#         text = re.sub(r'https?://\S+|ftp://\S+', 'lien', text)

#         # 5. Ponctuation non orale
#         text = re.sub(r'^\s*[-•–—]\s+', '', text, flags=re.MULTILINE)
#         text = re.sub(r'^\s*[\-|: ]{3,}\s*$', '', text, flags=re.MULTILINE)
#         text = re.sub(r'\|', ' ', text)
#         text = re.sub(r'[\\/@#$%^&{}\[\]<>=]', ' ', text)
#         text = re.sub(r'[(){}\[\]]', ' ', text)
#         text = re.sub(r'\.{2,}', ',', text)
#         text = re.sub(r'\s*[–—]\s*', ', ', text)
#         text = re.sub(r'\*+', '', text)
#         text = re.sub(r'_+', ' ', text)

#         # 6. Normalisation des espaces et des sauts de ligne
#         text = re.sub(r'\n+', ' ', text)
#         text = re.sub(r' {2,}', ' ', text)

#         return text.strip()

#     def speak(self, text: str, *, blocking: bool = True) -> None:
#         """Synthèse vocale en français natif.

#         blocking=True (par défaut) : retourne APRÈS la fin de la lecture.
#         blocking=False             : usage exceptionnel uniquement —
#                                      par exemple, phrases de patience émises
#                                      par PatienceManager pendant qu'un autre fil
#                                      attend le modèle de langage. Dans ce cas,
#                                      le microphone n'est pas sollicité en parallèle,
#                                      donc pas de risque d'écho capturé.
#         RÈGLE : ne JAMAIS appeler avec blocking=False juste avant écoute().
#         """
#         if not text or not text.strip():
#             return
#         text = self._sanitize_tts(text)
#         if not text:
#             return
#         logger.info("Synthèse [%s] : '%s'", self.tts_backend, text[:80])

#         dispatch = {
#             "coqui":   self._speak_coqui,
#             "piper":   self._speak_piper,
#             "gtts":    self._speak_gtts,
#             "pyttsx3": self._speak_pyttsx3,
#         }
#         fn = dispatch.get(self.tts_backend)
#         if fn is None:
#             logger.error("Moteur de synthèse inconnu : %s", self.tts_backend)
#             print("[Synthèse] " + text)
#             return
#         fn(text, blocking)

#     # ------------------------------------------------------------------
#     # Signaux d'ambiance — retour sonore court pendant les attentes
#     # ------------------------------------------------------------------
#     # Générés à la volée (sinusoïdes), aucune dépendance audio externe
#     # supplémentaire au-delà de sounddevice (déjà requis par coqui/piper).
#     # En cas d'indisponibilité : dégradation silencieuse, sans exception
#     # propagée ni affichage parasite — un signal manqué ne doit jamais
#     # bloquer le flux conversationnel.
#     # ------------------------------------------------------------------

#     _EARCON_PROFILES = {
#         # (fréquence Hz, durée s, amplitude) — profils courts et discrets
#         "patience_short":  (880.0, 0.10, 0.15),   # signal discret, attente courte
#         "patience_medium": (660.0, 0.15, 0.18),   # signal intermédiaire
#         "patience_long":   (440.0, 0.22, 0.20),   # signal grave, longue attente
#     }

#     def play_earcon(self, profile: str) -> None:
#         """Joue un signal d'ambiance court et non bloquant. Échec silencieux."""
#         params = self._EARCON_PROFILES.get(profile)
#         if params is None:
#             return
#         try:
#             threading.Thread(
#                 target=self._play_earcon_sync, args=(params,), daemon=True
#             ).start()
#         except Exception as exc:
#             logger.debug("play_earcon : %s", exc)

#     def _play_earcon_sync(self, params) -> None:
#         freq, duration, amplitude = params
#         try:
#             import sounddevice as sd
#             sample_rate = 22050
#             n_samples = int(sample_rate * duration)
#             tone = [
#                 amplitude * math.sin(2 * math.pi * freq * (i / sample_rate))
#                 for i in range(n_samples)
#             ]
#             sd.play(tone, sample_rate)
#             sd.wait()
#         except Exception as exc:
#             logger.debug("Signal d'ambiance indisponible (%s), ignoré", exc)

#     # ------------------------------------------------------------------
#     # Moteur Coqui — référence qualité
#     # ------------------------------------------------------------------

#     def _speak_coqui(self, text: str, blocking: bool) -> None:
#         tmp_path: Optional[str] = None
#         try:
#             import soundfile as sf
#             import sounddevice as sd

#             with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
#                 tmp_path = f.name

#             with self._lock_tts:
#                 self._coqui_model.tts_to_file(text=text, file_path=tmp_path)

#             data, sr = sf.read(tmp_path, dtype="float32")
#             if blocking:
#                 sd.play(data, sr)
#                 sd.wait()
#             else:
#                 sd.play(data, sr)

#         except Exception as exc:
#             logger.error("Coqui erreur : %s", exc)
#             print("[Synthèse] " + text)
#         finally:
#             if tmp_path and os.path.exists(tmp_path):
#                 try:
#                     os.unlink(tmp_path)
#                 except OSError:
#                     pass

#     # ------------------------------------------------------------------
#     # Moteur Piper — latence minimale
#     # ------------------------------------------------------------------

#     def _speak_piper(self, text: str, blocking: bool) -> None:
#         tmp_path: Optional[str] = None
#         try:
#             import subprocess
#             import soundfile as sf
#             import sounddevice as sd

#             with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
#                 tmp_path = f.name

#             result = subprocess.run(
#                 ["piper", "--model", self.piper_model_id, "--output_file", tmp_path],
#                 input=text.encode("utf-8"),
#                 capture_output=True,
#                 timeout=30,
#             )
#             if result.returncode != 0:
#                 raise RuntimeError(
#                     "piper code de retour=%d : %s" % (
#                         result.returncode, result.stderr.decode()
#                     )
#                 )

#             data, sr = sf.read(tmp_path, dtype="float32")
#             if blocking:
#                 sd.play(data, sr)
#                 sd.wait()
#             else:
#                 sd.play(data, sr)

#         except FileNotFoundError:
#             logger.error("Exécutable 'piper' introuvable. pip install piper-tts")
#             print("[Synthèse] " + text)
#         except Exception as exc:
#             logger.error("Piper erreur : %s", exc)
#             print("[Synthèse] " + text)
#         finally:
#             if tmp_path and os.path.exists(tmp_path):
#                 try:
#                     os.unlink(tmp_path)
#                 except OSError:
#                     pass

#     # ------------------------------------------------------------------
#     # Moteur Google Synthèse vocale — en ligne
#     # ------------------------------------------------------------------

#     def _speak_gtts(self, text: str, blocking: bool) -> None:
#         tmp_path: Optional[str] = None
#         try:
#             from gtts import gTTS
#             import pygame

#             tts = gTTS(text=text, lang=self.language, slow=False)
#             with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
#                 tmp_path = f.name
#             tts.save(tmp_path)

#             # Réinitialisation propre du mixeur à chaque appel
#             if pygame.mixer.get_init():
#                 pygame.mixer.quit()
#             pygame.mixer.init(frequency=22050, size=-16, channels=1, buffer=512)
#             pygame.mixer.music.load(tmp_path)
#             pygame.mixer.music.play()

#             if blocking:
#                 while pygame.mixer.music.get_busy():
#                     time.sleep(0.05)
#                 pygame.mixer.quit()

#         except Exception as exc:
#             logger.error("Google Synthèse vocale erreur : %s", exc)
#             print("[Synthèse] " + text)
#         finally:
#             if tmp_path and os.path.exists(tmp_path):
#                 try:
#                     time.sleep(0.1)
#                     os.unlink(tmp_path)
#                 except OSError:
#                     pass

#     # ------------------------------------------------------------------
#     # Moteur pyttsx3 — solution de secours ultime
#     # ------------------------------------------------------------------

#     def _speak_pyttsx3(self, text: str, blocking: bool) -> None:
#         with self._lock_tts:
#             try:
#                 self._tts_engine.say(text)
#                 if blocking:
#                     self._tts_engine.runAndWait()
#                 else:
#                     t = threading.Thread(
#                         target=self._tts_engine.runAndWait, daemon=True
#                     )
#                     t.start()
#             except Exception as exc:
#                 logger.error("pyttsx3 erreur : %s", exc)
#                 print("[Synthèse] " + text)

#     # ------------------------------------------------------------------
#     # Reconnaissance vocale — fragment avec détection automatique de voix
#     # ------------------------------------------------------------------

#     def listen_chunk(
#         self,
#         *,
#         pause_threshold:   float = STT_SILENCE_TIMEOUT,
#         phrase_time_limit: int   = STT_PHRASE_TIME_LIMIT,
#         listen_timeout:    float = STT_LISTEN_TIMEOUT,
#     ) -> str:
#         """Capture un fragment de parole et le transcrit.

#         Retourne :
#             Le texte transcrit (non vide).

#         Lève :
#             RuntimeError si la capture ou la transcription échoue,
#             ou si aucune voix n'est détectée dans le délai imparti.
#         """
#         import speech_recognition as sr

#         original = self._recognizer.pause_threshold
#         self._recognizer.pause_threshold = pause_threshold
#         tmp_path: Optional[str] = None

#         try:
#             with sr.Microphone() as src:
#                 logger.info(
#                     "Écoute (silence=%.1fs, max=%ds)...",
#                     pause_threshold, phrase_time_limit,
#                 )
#                 self._recognizer.adjust_for_ambient_noise(src, duration=STT_AMBIENT_DURATION)
#                 audio = self._recognizer.listen(
#                     src,
#                     timeout=listen_timeout,
#                     phrase_time_limit=phrase_time_limit,
#                 )

#             with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
#                 tmp_path = f.name
#                 f.write(audio.get_wav_data())

#             if self.stt_backend == "whisper":
#                 return self._transcribe_whisper(tmp_path)
#             else:
#                 return self._transcribe_google(audio)

#         except sr.WaitTimeoutError as exc:
#             raise RuntimeError("Aucune voix détectée dans le délai imparti") from exc

#         finally:
#             self._recognizer.pause_threshold = original
#             if tmp_path and os.path.exists(tmp_path):
#                 try:
#                     os.unlink(tmp_path)
#                 except OSError:
#                     pass

#     def listen_short(self, question: str, timeout: float = 8.0) -> str:
#         """Pose une question brève et attend une réponse courte.
#         Retourne une chaîne vide en cas d'absence de réponse (aucune exception propagée).
#         """
#         self.speak(question)
#         self.speak(pick("listening"))
#         try:
#             return self.listen_chunk(
#                 pause_threshold=1.5,
#                 phrase_time_limit=15,
#                 listen_timeout=timeout,
#             )
#         except RuntimeError as exc:
#             logger.info("listen_short : aucune réponse (%s)", exc)
#             return ""

#     def _transcribe_whisper(self, wav_path: str) -> str:
#         segments_gen, info = self._whisper_model.transcribe(
#             wav_path,
#             language=self.language,
#             beam_size=WHISPER_BEAM_SIZE,
#         )
#         logger.debug(
#             "Whisper : langue=%s (%.0f%%)",
#             info.language, info.language_probability * 100,
#         )
#         text = " ".join(seg.text.strip() for seg in segments_gen).strip()
#         if not text:
#             raise RuntimeError("La reconnaissance vocale n'a produit aucun texte")
#         logger.info("Fragment reconnu : '%s'", text[:100])
#         return text

#     def _transcribe_google(self, audio) -> str:
#         import speech_recognition as sr
#         lang = "fr-FR" if self.language == "fr" else (self.language + "-" + self.language.upper())
#         try:
#             text = self._recognizer.recognize_google(audio, language=lang)
#             logger.info("Reconnaissance Google : '%s'", text[:100])
#             return text
#         except sr.UnknownValueError:
#             raise RuntimeError("Reconnaissance Google : audio incompréhensible")
#         except sr.RequestError as exc:
#             raise RuntimeError("Reconnaissance Google : erreur de service : %s" % exc)

#     # ------------------------------------------------------------------
#     # Nettoyage
#     # ------------------------------------------------------------------

#     def close(self) -> None:
#         self._stop_audio()
#         if self._tts_engine is not None:
#             try:
#                 with self._lock_tts:
#                     self._tts_engine.stop()
#             except Exception:
#                 pass
#         logger.info("VoiceIO fermé")


# # ============================================================================
# # VRScenarioApp — orchestration principale
# # ============================================================================

# class VRScenarioApp:
#     """
#     Flux en deux phases :

#     PHASE 1 — Génération et présentation du scénario
#       - Saisie vocale du thème
#       - Le modèle de langage génère un scénario structuré
#       - Construction de la session de scénario
#       - Lecture du résumé oral par synthèse vocale

#     PHASE 2 — Questions et réponses supervisées
#       - L'utilisateur pose librement ses questions à voix haute
#       - Le modèle répond en s'appuyant sur le scénario généré
#       - Le superviseur évalue chaque échange : CONTINUER / CONSEIL / STOP
#       - Un mot de sortie clôt proprement la session

#     Gestion de la patience
#     ----------------------
#     Toute attente potentiellement longue (génération de scénario, appel
#     au modèle en questions-réponses) est encadrée par PatienceManager,
#     qui pilote automatiquement les signaux d'ambiance et les phrases de
#     transition selon la durée réelle d'attente.
#     """

#     def __init__(self, io: VoiceIO) -> None:
#         self.io = io
#         self.patience = PatienceManager(io)

#     def run(self) -> None:
#         self._welcome()
#         topic      = self._ask_topic()
#         config     = self._setup_llm()
#         supervisor = SupervisorLLM(config)

#         # -- Phase 1 : génération et présentation -------------------------
#         scenario_session = self._generate_and_announce(topic, config)

#         # -- Phase 2 : questions-réponses supervisées ---------------------
#         self._qa_loop(scenario_session, supervisor, config)

#         self._goodbye()

#     # ------------------------------------------------------------------
#     # Phase 1 : génération du scénario
#     # ------------------------------------------------------------------

#     def _welcome(self) -> None:
#         print("\n" + "=" * 60)
#         print("  APPLICATION VOCALE — SCÉNARIOS DE FORMATION EN RÉALITÉ VIRTUELLE")
#         print("=" * 60)
#         self.io.speak(
#             "Bienvenue dans votre assistant vocal de scénarios de formation. "
#             "Je vais générer un scénario à partir du thème que vous me donnerez, "
#             "vous en présenter les grandes lignes, "
#             "puis répondre à vos questions. "
#             "Dites terminer à tout moment pour clore la session."
#         )

#     def _ask_topic(self) -> str:
#         text = self.io.listen_short(
#             "Sur quel thème souhaitez-vous travailler ? "
#             "Vous pouvez me dire, par exemple : la consignation gaz, "
#             "la sécurité incendie, ou les premiers secours."
#         )
#         if not text:
#             text = "sécurité industrielle"
#             self.io.speak(
#                 "Je n'ai pas entendu de thème. "
#                 "Je vais utiliser la sécurité industrielle par défaut."
#             )
#         else:
#             self.io.speak("Très bien. Le thème retenu est : " + text + ".")
#         logger.info("Thème : '%s'", text)
#         print("\nThème : " + text)
#         return text

#     def _generate_and_announce(self, topic: str, config) -> "ScenarioSession | None":
#         """
#         Appelle le modèle pour générer le scénario, construit la session,
#         et lit le résumé oral.
#         Retourne None si la génération échoue (les questions-réponses restent possibles).

#         La génération peut prendre plusieurs secondes. Elle est encadrée par
#         PatienceManager qui gère automatiquement les signaux d'ambiance et
#         les phrases de transition selon la durée réelle d'attente.
#         """
#         print("\nGénération du scénario en cours…")

#         scenario_json: Dict[str, Any] = {}
#         scenario_text: str = ""

#         def _do_generate():
#             nonlocal scenario_text, scenario_json
#             try:
#                 from vr_scenario_lib.scenario import generate_scenario as lib_generate
#                 result = lib_generate(topic=topic, llm_config=config)
#                 if isinstance(result, tuple):
#                     scenario_text, scenario_json = result[0], result[1]
#                 else:
#                     scenario_text = getattr(result, "text", str(result))
#                     scenario_json = getattr(result, "json", {})
#                 logger.info(
#                     "Scénario généré via la bibliothèque (%d caractères)", len(scenario_text)
#                 )
#             except Exception as exc:
#                 logger.warning(
#                     "Bibliothèque indisponible : %s — génération directe", exc
#                 )
#                 scenario_json, scenario_text = self._generate_via_llm(topic, config)

#         self.patience.run_with_patience(_do_generate)

#         if not scenario_json and not scenario_text:
#             self.io.speak(
#                 "La génération du scénario n'a pas abouti. "
#                 "Vous pouvez néanmoins me poser vos questions directement."
#             )
#             return None

#         # -- Construction de la session -----------------------------------
#         now = datetime.now(timezone.utc).isoformat()
#         try:
#             from vr_scenario_lib.scenario_store import ScenarioSession
#             session = ScenarioSession(
#                 scenario_id   = str(uuid.uuid4()),
#                 topic         = topic,
#                 scenario_text = scenario_text,
#                 scenario_json = scenario_json,
#                 created_at    = now,
#                 updated_at    = now,
#             )
#             logger.info("Session créée (identifiant=%s)", session.scenario_id)
#         except Exception as exc:
#             logger.warning("Création de session impossible : %s", exc)
#             session = None

#         # -- Présentation vocale du scénario ------------------------------
#         self._announce_scenario(scenario_json, scenario_text)
#         return session

#     def _generate_via_llm(
#         self, topic: str, config
#     ) -> "tuple[Dict[str, Any], str]":
#         """
#         Appel direct au modèle pour générer le scénario.
#         Retourne ({}, "") en cas d'échec.
#         """
#         if config is None:
#             return self._fallback_static_scenario(topic)

#         user_msg = "Génère un scénario de formation en réalité virtuelle sur le thème : " + topic

#         try:
#             raw = self._call_llm_raw(
#                 system     = SCENARIO_GEN_SYSTEM,
#                 user       = user_msg,
#                 config     = config,
#                 max_tokens = SCENARIO_GEN_MAX_TOKENS,
#             )
#         except Exception as exc:
#             logger.error("Génération par le modèle échouée : %s", exc)
#             return self._fallback_static_scenario(topic)

#         try:
#             import re
#             m = re.search(r'\{.*\}', raw, re.DOTALL)
#             if not m:
#                 raise ValueError("Structure JSON introuvable")
#             obj = json.loads(m.group())
#         except Exception as exc:
#             logger.error("Analyse du scénario échouée : %s | brut=%s", exc, raw[:200])
#             return self._fallback_static_scenario(topic)

#         text = self._json_to_text(obj, topic)
#         return obj, text

#     @staticmethod
#     def _json_to_text(obj: Dict[str, Any], topic: str) -> str:
#         """Convertit le scénario structuré en texte lisible."""
#         lines = ["# SCÉNARIO DE FORMATION — " + topic.upper(), ""]
#         titre = obj.get("titre", topic)
#         lines += ["## " + titre, ""]

#         objectifs = obj.get("objectifs", [])
#         if objectifs:
#             lines.append("### Objectifs")
#             for o in objectifs:
#                 lines.append("- " + str(o))
#             lines.append("")

#         for etape in obj.get("grandes_lignes", []):
#             num    = etape.get("etape", "")
#             titre_e = etape.get("titre", "")
#             desc   = etape.get("description", "")
#             lines.append("### Étape %s : %s" % (num, titre_e))
#             lines.append(desc)
#             lines.append("")

#         procs = obj.get("procedures_cles", [])
#         if procs:
#             lines.append("### Procédures clés")
#             for p in procs:
#                 lines.append("- " + str(p))
#             lines.append("")

#         vigilance = obj.get("points_vigilance", [])
#         if vigilance:
#             lines.append("### Points de vigilance")
#             for v in vigilance:
#                 lines.append("- " + str(v))
#             lines.append("")

#         return "\n".join(lines)

#     @staticmethod
#     def _fallback_static_scenario(topic: str) -> "tuple[Dict[str, Any], str]":
#         """Scénario minimal si le modèle de langage est inaccessible."""
#         obj = {
#             "titre": "Scénario " + topic,
#             "objectifs": [
#                 "Comprendre les principes fondamentaux de " + topic,
#                 "Maîtriser les procédures de sécurité essentielles",
#                 "Réagir de façon appropriée aux situations d'urgence",
#             ],
#             "grandes_lignes": [
#                 {
#                     "etape": 1,
#                     "titre": "Préparation",
#                     "description": "Vérifier les équipements et les protections individuelles avant toute intervention.",
#                 },
#                 {
#                     "etape": 2,
#                     "titre": "Intervention",
#                     "description": "Appliquer les procédures standard en respectant les consignes de sécurité.",
#                 },
#                 {
#                     "etape": 3,
#                     "titre": "Clôture",
#                     "description": "Consigner les actions effectuées et signaler tout incident survenu.",
#                 },
#             ],
#             "procedures_cles": [
#                 "Vérifier les équipements avant toute intervention",
#                 "Respecter les périmètres de sécurité",
#                 "Alerter la hiérarchie en cas d'incident",
#             ],
#             "points_vigilance": [
#                 "Ne jamais intervenir seul",
#                 "Toujours porter les protections adaptées à la situation",
#             ],
#             "resume_oral": (
#                 "Ce scénario porte sur le thème " + topic + ". "
#                 "Il se déroule en trois étapes : la préparation du matériel, "
#                 "l'intervention selon les procédures standard, "
#                 "et la clôture avec consignation des actions effectuées."
#             ),
#         }
#         text = VRScenarioApp._json_to_text(obj, topic)
#         return obj, text

#     def _announce_scenario(self, scenario_json: Dict[str, Any], scenario_text: str) -> None:
#         # """Présente les grandes lignes du scénario à voix haute."""
#         # print("\n" + "=" * 60)
#         # print("  SCÉNARIO GÉNÉRÉ")
#         # print("=" * 60)
#         # print(scenario_text[:1200] + ("…" if len(scenario_text) > 1200 else ""))
#         print("\n" + "=" * 60)
#         print("  SCÉNARIO TEXTUEL")
#         print("=" * 60)
#         print(scenario_text)
#         print("=" * 60)
#         # --- AJOUT : Affichage du JSON de configuration généré ---
#         print("\n" + "=" * 60)
#         print("  SCÉNARIO GÉNÉRÉ (JSON)")
#         print("=" * 60)
#         print(json.dumps(scenario_json, indent=2, ensure_ascii=False))
#         print("=" * 60 + "\n")
#         # ---------------------------------------------------------
#         # Lecture du résumé oral (conçu pour la synthèse vocale, sans listes)
#         resume = scenario_json.get("resume_oral", "")
#         if not resume:
#             titre = scenario_json.get("titre", "le scénario")
#             etapes = scenario_json.get("grandes_lignes", [])
#             if etapes:
#                 noms = ", ".join(str(e.get("titre", "")) for e in etapes[:4])
#                 resume = (
#                     "Le scénario intitulé " + titre
#                     + " se déroule en " + str(len(etapes))
#                     + " étapes : " + noms + "."
#                 )
#             else:
#                 resume = "Le scénario " + titre + " vient d'être généré."

#         self.io.speak("Voici les grandes lignes de votre scénario.")
#         self.io.speak(resume)

#         # Points de vigilance, si présents
#         vigilance = scenario_json.get("points_vigilance", [])
#         if vigilance:
#             points = " et ".join(vigilance[:3])
#             self.io.speak("Les points de vigilance à retenir sont : " + points + ".")

#         self.io.speak(
#             "Le scénario est prêt. "
#             "Posez-moi vos questions quand vous voulez. "
#             "Dites terminer pour clore la session."
#         )

#     # ------------------------------------------------------------------
#     # Phase 2 : questions-réponses supervisées
#     # ------------------------------------------------------------------

#     def _qa_loop(
#         self,
#         scenario_session,   # ScenarioSession | None
#         supervisor: SupervisorLLM,
#         config,
#     ) -> None:
#         """Boucle de questions et réponses supervisées.

#         Gestion du silence en trois niveaux :
#           Niveau 1 — silence léger    : on relance l'écoute sans rien dire
#           Niveau 2 — relance douce    : après le premier délai, une phrase
#                                         courte rassure sans interroger
#           Niveau 3 — silence prolongé : après plusieurs délais, question
#                                         explicite pour continuer ou terminer
#         """
#         print("\n" + "-" * 60)
#         print("[ SESSION DE QUESTIONS — posez vos questions ]")
#         print("-" * 60)

#         narrator = NarratorSession(
#             topic=scenario_session.topic if scenario_session else "général"
#         )
#         consecutive_timeouts = 0
#         MAX_TIMEOUTS  = 3
#         SOFT_NUDGE_AT = 1

#         while True:

#             # ---- 1. Capture de la question ---------------------------------
#             self.io.speak(pick("listening"))
#             try:
#                 question = self.io.listen_chunk(
#                     pause_threshold   = STT_SILENCE_TIMEOUT,
#                     phrase_time_limit = STT_PHRASE_TIME_LIMIT,
#                     listen_timeout    = STT_LISTEN_TIMEOUT,
#                 )
#                 consecutive_timeouts = 0
#             except RuntimeError as exc:
#                 consecutive_timeouts += 1
#                 logger.info(
#                     "Délai Q&R %d/%d : %s", consecutive_timeouts, MAX_TIMEOUTS, exc
#                 )

#                 if consecutive_timeouts >= MAX_TIMEOUTS:
#                     if self._ask_continue_qa():
#                         consecutive_timeouts = 0
#                     else:
#                         break
#                 elif consecutive_timeouts == SOFT_NUDGE_AT:
#                     self.io.speak(pick("soft_nudge"))
#                 continue

#             # ---- 2. Détection d'un mot de sortie ---------------------------
#             if any(w in question.lower() for w in EXIT_WORDS):
#                 print("\nSortie Q&R : '%s'" % question)
#                 break

#             print("\n[Question] " + question)
#             narrator.add_chunk(question)

#             # ---- 3. Réponse du modèle (avec patience) ----------------------
#             answer = self.patience.run_with_patience(
#                 self._get_answer, question, scenario_session, config
#             )
#             print("[Réponse] " + answer)
#             self.io.speak(answer)

#             # ---- 4. Supervision de l'échange -------------------------------
#             exchange = "Question : " + question + "\nRéponse : " + answer
#             decision = supervisor.analyse(narrator, exchange)
#             logger.info(
#                 "Superviseur Q&R : %s | '%s'",
#                 decision.decision.value,
#                 decision.message[:60] if decision.message else "",
#             )

#             if decision.decision == Decision.CONSEIL:
#                 print("\n[CONSEIL] " + decision.message)
#                 self.io.speak(decision.message)

#             elif decision.decision == Decision.STOP:
#                 print("\n[STOP] " + decision.message)
#                 self.io.interrupt_and_speak(decision.message)
#                 if not self._handle_stop_qa():
#                     break

#     def _get_answer(self, question: str, scenario_session, config) -> str:
#         """
#         Obtient une réponse du modèle à la question posée.
#         Priorité : discuss_scenario() de la bibliothèque, puis appel direct, puis message de repli.
#         """
#         # Via la bibliothèque de scénarios
#         if scenario_session is not None and config is not None:
#             try:
#                 from vr_scenario_lib.scenario import discuss_scenario
#                 reply = discuss_scenario(
#                     session      = scenario_session,
#                     user_message = question,
#                     llm_config   = config,
#                 )
#                 if reply and reply.strip():
#                     return reply.strip()
#             except Exception as exc:
#                 logger.warning("discuss_scenario erreur : %s — appel direct", exc)

#         # Appel direct avec contexte du scénario
#         if config is not None:
#             context = (
#                 scenario_session.scenario_text[:800]
#                 if scenario_session and scenario_session.scenario_text
#                 else ""
#             )
#             user_msg = (
#                 ("Contexte du scénario :\n" + context + "\n\n" if context else "")
#                 + "Question de l'apprenant : " + question
#             )
#             try:
#                 return self._call_llm_raw(
#                     system     = QA_SYSTEM,
#                     user       = user_msg,
#                     config     = config,
#                     max_tokens = QA_MAX_TOKENS,
#                 ).strip()
#             except Exception as exc:
#                 logger.error("Appel direct Q&R erreur : %s", exc)

#         return (
#             "Je n'ai pas pu obtenir de réponse pour le moment. "
#             "Vous pouvez reformuler votre question ou consulter la documentation du scénario."
#         )

#     # ------------------------------------------------------------------
#     # Fonctions auxiliaires
#     # ------------------------------------------------------------------

#     @staticmethod
#     def _call_llm_raw(*, system: str, user: str, config, max_tokens: int) -> str:
#         """Appel unifié au modèle de langage : bibliothèque, puis appel direct."""
#         try:
#             from vr_scenario_lib.llm import call_llm
#             return call_llm(
#                 system=system, user=user,
#                 llm_config=config, max_tokens=max_tokens,
#             )
#         except ImportError:
#             pass

#         import urllib.request
#         payload = json.dumps({
#             "model":      getattr(config, "model", "gpt-3.5-turbo"),
#             "max_tokens": max_tokens,
#             "messages":   [
#                 {"role": "system", "content": system},
#                 {"role": "user",   "content": user},
#             ],
#         }).encode()
#         api_url = getattr(config, "api_url", "https://api.openai.com/v1/chat/completions")
#         token   = getattr(config, "token", "")
#         req = urllib.request.Request(
#             api_url, data=payload,
#             headers={
#                 "Content-Type":  "application/json",
#                 "Authorization": "Bearer " + token,
#             },
#         )
#         with urllib.request.urlopen(req, timeout=20) as resp:
#             data = json.loads(resp.read())
#         return data["choices"][0]["message"]["content"]

#     def _ask_continue_qa(self) -> bool:
#         text = self.io.listen_short(pick("no_response_continue_check"))
#         if not text:
#             return False
#         return any(
#             w in text.lower()
#             for w in {"oui", "yes", "continuer", "continue", "si", "d'accord", "bien sûr"}
#         )

#     def _handle_stop_qa(self) -> bool:
#         """Pause après une alerte STOP en phase questions-réponses. Retourne True pour reprendre."""
#         self.io.speak(
#             "La session est interrompue suite à cette alerte. "
#             "Dites reprendre pour continuer vos questions, "
#             "ou terminer pour clore la session."
#         )
#         text = ""
#         try:
#             text = self.io.listen_chunk(
#                 pause_threshold   = 2.0,
#                 phrase_time_limit = 10,
#                 listen_timeout    = 12,
#             )
#         except RuntimeError:
#             pass
#         if any(w in text.lower() for w in {"reprendre", "continuer", "oui", "yes", "d'accord"}):
#             self.io.speak("Très bien. Je reste à l'écoute de vos questions.")
#             return True
#         return False

#     def _goodbye(self) -> None:
#         self.io.speak(
#             "Merci pour cette session de formation. "
#             "J'espère que ce scénario vous a été utile. "
#             "À très bientôt."
#         )
#         print("\nAu revoir !\n")

#     # ------------------------------------------------------------------
#     # Configuration du modèle de langage
#     # ------------------------------------------------------------------

#     def _setup_llm(self):
#         try:
#             from vr_scenario_lib.config import build_llm_config
#             return build_llm_config()
#         except Exception as exc:
#             logger.warning(
#                 "Configuration du modèle indisponible : %s — mode dégradé (scénarios statiques)",
#                 exc,
#             )
#             return None


# # ============================================================================
# # Interface en ligne de commande
# # ============================================================================

# def _parse_args() -> argparse.Namespace:
#     p = argparse.ArgumentParser(
#         description=(
#             "Application vocale de supervision de scénarios de formation en réalité virtuelle"
#         ),
#         formatter_class=argparse.ArgumentDefaultsHelpFormatter,
#     )
#     p.add_argument(
#         "--stt-backend", default="whisper", choices=["whisper", "google"],
#         help="Moteur de reconnaissance vocale.",
#     )
#     p.add_argument(
#         "--tts-backend", default=TTS_DEFAULT_BACKEND,
#         choices=["coqui", "piper", "gtts", "pyttsx3"],
#         help=(
#             "Moteur de synthèse vocale. "
#             "Les options 'coqui' et 'piper' fonctionnent entièrement hors ligne."
#         ),
#     )
#     p.add_argument(
#         "--language", default="fr",
#         help="Code de langue au format ISO 639-1 (fr par défaut).",
#     )
#     p.add_argument(
#         "--whisper-model", default=WHISPER_DEFAULT_MODEL,
#         choices=["tiny", "base", "small", "medium", "large"],
#         help="Taille du modèle Whisper. L'option 'small' est recommandée pour le français.",
#     )
#     p.add_argument(
#         "--coqui-model", default=COQUI_MODEL_FR,
#         help="Identifiant du modèle Coqui.",
#     )
#     p.add_argument(
#         "--piper-model", default=PIPER_MODEL_FR,
#         help="Nom du modèle Piper (exemple : fr_FR-tom-medium).",
#     )
#     p.add_argument(
#         "--debug", action="store_true",
#         help="Active les journaux de débogage complets.",
#     )
#     return p.parse_args()


# def main() -> None:
#     args = _parse_args()
#     if args.debug:
#         logging.getLogger().setLevel(logging.DEBUG)

#     io = VoiceIO(
#         stt_backend   = args.stt_backend,
#         tts_backend   = args.tts_backend,
#         language      = args.language,
#         whisper_model = args.whisper_model,
#         coqui_model   = args.coqui_model,
#         piper_model   = args.piper_model,
#     )
#     app = VRScenarioApp(io)
#     try:
#         app.run()
#     except KeyboardInterrupt:
#         print("\nSession interrompue par l'utilisateur.")
#     finally:
#         io.close()


# if __name__ == "__main__":
#     main()



# """
# Application vocale de supervision de scénarios de formation en réalité virtuelle.
# Version entreprise — standards industriels.

# RÔLE DE L'APPLICATION
# ----------------------
# L'utilisateur décrit librement un scénario de réalité virtuelle à voix haute.
# L'application écoute en continu, transcrit par fragments avec détection de voix,
# et soumet chaque fragment à un superviseur linguistique qui peut :
#   - CONTINUER  : rester silencieux (écoute neutre)
#   - CONSEIL    : intervenir poliment pour formuler un conseil
#   - STOP       : interrompre fermement pour signaler une erreur critique

# Architecture
# ------------
# VoiceIO          : reconnaissance vocale (Faster Whisper + VAD SpeechRecognition) + synthèse vocale française native.
# SupervisorLLM    : analyse chaque fragment, décide CONTINUER / CONSEIL / STOP.
# NarratorSession  : accumule la transcription, maintient le contexte du scénario.
# VRScenarioApp    : orchestration métier (initialisation + boucle de narration supervisée).
# PatienceManager  : retour sonore pendant les temps de traitement (signaux d'ambiance + phrases de transition).

# Moteurs de synthèse vocale française (ordre de priorité automatique)
# --------------------------------------------------------------------
# 1. coqui   -- Coqui VITS tts_models/fr/mai/tacotron2-DDC : voix neurale hors ligne, haute qualité
# 2. piper   -- Piper fr_FR-tom-medium                      : voix neurale hors ligne, très rapide
# 3. gtts    -- Google Synthèse vocale                      : voix en ligne, qualité maximale
# 4. pyttsx3 -- espeak-fr                                   : synthèse de base, sans dépendances

# Usage :
#     python app_vocal.py                            # détection automatique du meilleur moteur disponible
#     python app_vocal.py --tts-backend coqui        # Coqui VITS (hors ligne, haute qualité)
#     python app_vocal.py --tts-backend piper        # Piper (hors ligne, très rapide)
#     python app_vocal.py --tts-backend gtts         # Google Synthèse vocale (en ligne)
#     python app_vocal.py --stt-backend google       # Google Reconnaissance vocale (en ligne)
#     python app_vocal.py --whisper-model small      # meilleure précision de reconnaissance
#     python app_vocal.py --debug                    # journaux de débogage complets
# """

# from __future__ import annotations

# import argparse
# import json
# import logging
# import math
# import os
# import random
# import struct
# import sys
# import tempfile
# import threading
# import time
# import uuid
# from dataclasses import dataclass, field
# from datetime import datetime, timezone
# from enum import Enum
# from typing import Any, Dict, List, Optional

# # ---------------------------------------------------------------------------
# # Journalisation
# # ---------------------------------------------------------------------------
# logging.basicConfig(
#     level=logging.INFO,
#     format="%(asctime)s | %(name)-36s | %(levelname)-8s | %(message)s",
#     datefmt="%H:%M:%S",
# )
# logger = logging.getLogger(__name__)

# sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# # ============================================================================
# # Constantes
# # ============================================================================

# STT_LISTEN_TIMEOUT    = 8
# STT_PHRASE_TIME_LIMIT = 20          # durée maximale d'un fragment de narration
# STT_SILENCE_TIMEOUT   = 2.0         # silence détecté → fin du fragment
# STT_AMBIENT_DURATION  = 0.5
# TTS_SPEECH_RATE       = 145
# TTS_VOLUME            = 0.92
# WHISPER_DEFAULT_MODEL = "base"
# WHISPER_BEAM_SIZE     = 5

# # Mots déclencheurs de fin de session
# # Rédigés pour être naturels à l'oral et fiables à la transcription
# EXIT_WORDS = {"quitter", "terminer", "au revoir", "fin", "arrêter", "c'est tout"}

# # Capture du thème — confirmation orale obligatoire (limite les scénarios générés
# # sur un thème mal compris par la reconnaissance vocale)
# TOPIC_MAX_ATTEMPTS = 3
# TOPIC_CONFIRM_YES  = {"oui", "yes", "exact", "correct", "c'est ça", "d'accord", "affirmatif"}
# TOPIC_CONFIRM_NO   = {"non", "no", "faux", "incorrect", "pas ça", "négatif"}

# # Moteurs de synthèse vocale française native
# TTS_DEFAULT_BACKEND   = "coqui"
# TTS_FALLBACK_CHAIN    = ["coqui", "piper", "gtts", "pyttsx3"]

# # Coqui : voix féminine Maï, accent français métropolitain soigné
# COQUI_MODEL_FR    = "tts_models/fr/mai/tacotron2-DDC"
# COQUI_SAMPLE_RATE = 22050

# # Piper : voix masculine Tom, accent français métropolitain naturel
# PIPER_MODEL_FR    = "fr_FR-tom-medium"
# PIPER_SAMPLE_RATE = 22050

# # Superviseur — instructions système
# SUPERVISOR_MAX_TOKENS = 256
# SUPERVISOR_SYSTEM = (
#     "Tu es un superviseur expert en sécurité de la réalité virtuelle et en procédures industrielles. "
#     "L'utilisateur décrit à voix haute un scénario de formation en réalité virtuelle. "
#     "Tu reçois des fragments de sa narration en temps réel.\n\n"
#     "Analyse le dernier fragment dans son contexte et réponds UNIQUEMENT avec un objet JSON :\n"
#     '{"decision": "CONTINUER" | "CONSEIL" | "STOP", "message": "<texte à dire, vide si CONTINUER>"}\n\n'
#     "Règles strictes :\n"
#     "- CONTINUER  : narration correcte, cohérente, sans danger. Message vide obligatoire.\n"
#     "- CONSEIL    : amélioration possible. Message court, positif, concret. Deux phrases maximum.\n"
#     "- STOP       : erreur critique de procédure, danger réel, incohérence grave. "
#     "Message direct et précis. Commence par 'Attention : '.\n"
#     "Ne jamais inventer de contexte non mentionné. Rester factuel."
# )

# # Génération de scénario — instructions système
# SCENARIO_GEN_MAX_TOKENS = 1024
# SCENARIO_GEN_SYSTEM = (
#     "Tu es un expert en conception de scénarios de formation en réalité virtuelle industrielle. "
#     "À partir d'un thème, génère un scénario structuré en JSON uniquement, sans aucun texte avant ou après.\n\n"
#     "Format JSON attendu (respecte exactement ces clés) :\n"
#     '{\n'
#     '  "titre": "Titre court du scénario",\n'
#     '  "objectifs": ["objectif 1", "objectif 2", "objectif 3"],\n'
#     '  "grandes_lignes": [\n'
#     '    {"etape": 1, "titre": "Titre de l\'étape", "description": "Description concise"},\n'
#     '    ...\n'
#     '  ],\n'
#     '  "procedures_cles": ["procédure 1", "procédure 2"],\n'
#     '  "points_vigilance": ["point 1", "point 2"],\n'
#     '  "resume_oral": "Texte fluide de trois à quatre phrases pour lecture vocale. Pas de listes, pas de symboles."\n'
#     '}\n\n'
#     "Le champ resume_oral doit être lisible à voix haute sans aucun accroc : pas de tirets, "
#     "pas de parenthèses, pas d'abréviations, pas de sigles. Quatre phrases au maximum."
# )

# # Questions-réponses — instructions système
# QA_MAX_TOKENS    = 180          # réduit : force la concision dès la génération
# QA_MAX_SENTENCES = 2            # filet de sécurité appliqué après coup (cf. _enforce_max_sentences)
# QA_SYSTEM = (
#     "Tu es un formateur expert qui aide un apprenant à comprendre un scénario de formation en réalité virtuelle. "
#     "Tu réponds aux questions en t'appuyant exclusivement sur le scénario fourni. "
#     "Réponse impérativement courte : une phrase si possible, deux phrases maximum. "
#     "Va droit à l'information utile. "
#     "Pas de listes, pas de tirets, pas de symboles, aucun mot ou formule de remplissage "
#     "(par exemple : en fait, donc, voilà, eh bien, du coup, en gros, extra). "
#     "Parle directement à l'apprenant, avec chaleur et précision."
# )

# # Appel au modèle de langage — robustesse réseau (standard industriel : retry + backoff)
# LLM_CALL_MAX_RETRIES     = 2     # tentatives supplémentaires après l'essai initial
# LLM_CALL_RETRY_BACKOFF_S = 1.5   # délai de base entre tentatives (croissance linéaire)

# # Locutions de remplissage à éliminer des réponses orales (filet de sécurité post-génération)
# FILLER_PATTERNS_FR = [
#     r"\ben fait\b,?\s*",
#     r"\bdonc\b,?\s*",
#     r"\bvoil[aà]\b,?\s*",
#     r"\beh bien\b,?\s*",
#     r"\bdu coup\b,?\s*",
#     r"\ben gros\b,?\s*",
#     r"\ben quelque sorte\b,?\s*",
#     r"\bpour ainsi dire\b,?\s*",
#     r"\b[aà] vrai dire\b,?\s*",
#     r"\bdisons que\b,?\s*",
#     r"\bil faut savoir que\b,?\s*",
#     r"\bextra\b\s*[!.,]?\s*",
#     r"^\s*alors,?\s*",
# ]


# # ============================================================================
# # Bibliothèque de phrases système
# # ----------------------------------------------------------------------------
# # Chaque entrée regroupe plusieurs formulations d'une même situation récurrente.
# # La fonction pick() tire une variante aléatoire à chaque appel, ce qui réduit
# # sensiblement la fatigue auditive lors de longues sessions.
# #
# # Principes de rédaction appliqués :
# #   - Phrases courtes, musicalité naturelle, rythme parlé
# #   - Pas de sigles ni d'anglicismes difficiles à prononcer
# #   - Pas de virgules superflues (pause TTS mal placée)
# #   - Finales ouvertes ou légèrement montantes (intonation invitante)
# #   - Chaleur professionnelle — ni trop formel ni trop familier
# # ============================================================================

# CACHED_PHRASES_FR: Dict[str, List[str]] = {

#     # Invitation à parler — brève, neutre, non répétitive
#     "listening": [
#         "Je vous écoute.",
#         "À vous.",
#         "Allez-y.",
#         "Je suis prêt.",
#         "La parole est à vous.",
#     ],

#     # Accusé de réception très court
#     "ack_short": [
#         "Bien reçu.",
#         "Compris.",
#         "Noté.",
#         "Entendu.",
#     ],

#     # Attente courte (1 à 3 secondes) — rien de verbal, juste un signal d'ambiance
#     # Ces phrases ne sont pas utilisées directement : le niveau 1 est traité
#     # uniquement par earcon, sans parole, pour ne pas alourdir les courtes attentes.
#     "thinking_short": [
#         "Un instant.",
#         "Je vérifie.",
#     ],

#     # Attente moyenne (3 à 10 secondes) — une phrase rassurante, pas d'explication
#     "thinking_medium": [
#         "Je prépare votre réponse.",
#         "Je consulte le scénario.",
#         "Je rassemble les éléments.",
#         "Je cherche la bonne information.",
#         "Je réfléchis à votre question.",
#     ],

#     # Attente longue (10 à 20 secondes) — on reconnaît que ça prend du temps
#     "thinking_long": [
#         "La question est détaillée, je finalise ma réponse.",
#         "Cela demande un peu plus de réflexion. Je suis sur le sujet.",
#         "Je creuse la question. Encore un court instant.",
#         "Je vérifie tous les éléments. Merci de votre patience.",
#     ],

#     # Attente très longue (au-delà de 20 secondes) — ton calme, pas d'alarme
#     "thinking_very_long": [
#         "Je suis toujours en train de traiter votre demande.",
#         "Le traitement prend un peu plus de temps que prévu. Je reste sur le sujet.",
#         "Toujours en cours. Je reviens vers vous très bientôt.",
#     ],

#     # Relance douce après un premier silence — sans interroger explicitement
#     "soft_nudge": [
#         "Je reste disponible si vous avez une question.",
#         "Prenez votre temps. Je vous écoute quand vous êtes prêt.",
#         "Pas de précipitation. Je suis là.",
#         "Vous pouvez continuer quand vous le souhaitez.",
#     ],

#     # Question explicite après un silence prolongé (oui / non)
#     "no_response_continue_check": [
#         "Je n'entends plus rien. Souhaitez-vous continuer la session ? "
#         "Dites oui pour continuer, ou non pour terminer.",
#         "Il y a un long silence. Voulez-vous poursuivre ? "
#         "Répondez oui ou non.",
#     ],
# }


# def pick(key: str) -> str:
#     """Tire aléatoirement une variante de phrase système pour réduire la répétition."""
#     options = CACHED_PHRASES_FR.get(key)
#     if not options:
#         return ""
#     return random.choice(options)


# # ============================================================================
# # Décision + NarratorSession
# # ============================================================================

# class Decision(Enum):
#     CONTINUER = "CONTINUER"
#     CONSEIL   = "CONSEIL"
#     STOP      = "STOP"


# @dataclass
# class SupervisorDecision:
#     decision: Decision = Decision.CONTINUER
#     message:  str      = ""

#     def must_speak(self) -> bool:
#         return self.decision in (Decision.CONSEIL, Decision.STOP)


# @dataclass
# class NarratorSession:
#     """Accumule la transcription et maintient le contexte pour le superviseur."""
#     topic:     str
#     chunks:    List[str] = field(default_factory=list)
#     full_text: str       = ""

#     def add_chunk(self, text: str) -> None:
#         self.chunks.append(text)
#         self.full_text = " ".join(self.chunks)

#     def context_window(self, n: int = 5) -> str:
#         return " ".join(self.chunks[-n:])

#     def summary(self) -> str:
#         return "%d séquence(s), environ %d mots" % (len(self.chunks), len(self.full_text.split()))


# # ============================================================================
# # PatienceManager — retour sonore pendant les temps de traitement
# # ----------------------------------------------------------------------------
# # Stratégie à paliers calibrée sur la durée d'attente réelle :
# #
# #   Moins de 1 s    : rien (imperceptible)
# #   De 1 à 3 s      : signal d'ambiance discret seul (pas de phrase —
# #                     évite la surcharge verbale sur les attentes courantes)
# #   De 3 à 10 s     : signal d'ambiance + courte phrase de transition
# #   Au-delà de 10 s : signal grave + phrase "longue attente", puis rappel
# #                     toutes les 12 s pour éviter le silence total anxiogène
# #
# # Le suivi tourne dans un fil d'exécution dédié pendant l'appel bloquant
# # au modèle de langage. Il s'arrête proprement (threading.Event) dès que
# # le résultat est disponible.
# # ============================================================================

# class PatienceManager:
#     """Pilote les signaux d'ambiance et les phrases de patience selon la durée réelle d'attente."""

#     LEVEL_SHORT_S     = 1.0    # moins de 1 s : rien
#     LEVEL_MEDIUM_S    = 3.0    # 1 à 3 s : signal seul
#     LEVEL_LONG_S      = 10.0   # 3 à 10 s : signal + phrase courte
#     LEVEL_VERY_LONG_S = 20.0   # au-delà de 10 s : signal grave + phrase longue

#     def __init__(self, io: "VoiceIO") -> None:
#         self.io = io
#         self._stop_event = threading.Event()
#         self._thread: Optional[threading.Thread] = None

#     def start(self) -> None:
#         self._stop_event.clear()
#         self._thread = threading.Thread(target=self._run, daemon=True)
#         self._thread.start()

#     def stop(self) -> None:
#         self._stop_event.set()
#         if self._thread is not None:
#             self._thread.join(timeout=2.0)
#             self._thread = None

#     def _run(self) -> None:
#         start = time.monotonic()
#         announced_medium    = False
#         announced_long      = False
#         announced_very_long = False

#         while not self._stop_event.is_set():
#             elapsed = time.monotonic() - start

#             if elapsed >= self.LEVEL_MEDIUM_S and not announced_medium:
#                 announced_medium = True
#                 self.io.play_earcon("patience_short")

#             if elapsed >= self.LEVEL_LONG_S and not announced_long:
#                 announced_long = True
#                 self.io.play_earcon("patience_medium")
#                 self.io.speak(pick("thinking_medium"), blocking=False)

#             if elapsed >= self.LEVEL_VERY_LONG_S and not announced_very_long:
#                 announced_very_long = True
#                 self.io.play_earcon("patience_long")
#                 self.io.speak(pick("thinking_long"), blocking=False)

#             # Rappel périodique au-delà du seuil très long
#             if announced_very_long and elapsed >= self.LEVEL_VERY_LONG_S + 12.0:
#                 self.io.speak(pick("thinking_very_long"), blocking=False)
#                 start -= 12.0  # reprogramme le prochain rappel dans 12 s

#             self._stop_event.wait(timeout=0.25)

#     def run_with_patience(self, fn, *args, **kwargs):
#         """Exécute fn(*args, **kwargs) en pilotant le retour sonore de patience."""
#         self.start()
#         try:
#             return fn(*args, **kwargs)
#         finally:
#             self.stop()


# # ============================================================================
# # SupervisorLLM
# # ============================================================================

# class SupervisorLLM:
#     """Analyse les fragments de narration et produit des décisions de supervision."""

#     def __init__(self, config) -> None:
#         self._config = config
#         self._lock   = threading.Lock()

#     def analyse(self, session: NarratorSession, new_chunk: str) -> SupervisorDecision:
#         if self._config is None:
#             return SupervisorDecision()

#         user_msg = (
#             "Thème du scénario : %s\n\n"
#             "Contexte (narration précédente) :\n%s\n\n"
#             "Nouveau fragment :\n%s"
#         ) % (session.topic, session.context_window(), new_chunk)

#         try:
#             with self._lock:
#                 raw = self._call_llm(user_msg)
#             return self._parse(raw)
#         except Exception as exc:
#             logger.warning("SupervisorLLM erreur : %s", exc)
#             return SupervisorDecision()

#     def _call_llm(self, user_msg: str) -> str:
#         # Tentative via la bibliothèque de scénarios
#         try:
#             from vr_scenario_lib.llm import call_llm
#             return call_llm(
#                 system=SUPERVISOR_SYSTEM,
#                 user=user_msg,
#                 llm_config=self._config,
#                 max_tokens=SUPERVISOR_MAX_TOKENS,
#             )
#         except ImportError:
#             pass

#         # Appel direct compatible avec l'interface de l'API de langage
#         import json
#         import urllib.request

#         payload = json.dumps({
#             "model":      getattr(self._config, "model", "gpt-3.5-turbo"),
#             "max_tokens": SUPERVISOR_MAX_TOKENS,
#             "messages":   [
#                 {"role": "system", "content": SUPERVISOR_SYSTEM},
#                 {"role": "user",   "content": user_msg},
#             ],
#         }).encode()
#         api_url = getattr(self._config, "api_url", "https://api.openai.com/v1/chat/completions")
#         token   = getattr(self._config, "token", "")
#         req = urllib.request.Request(
#             api_url,
#             data=payload,
#             headers={
#                 "Content-Type":  "application/json",
#                 "Authorization": "Bearer " + token,
#             },
#         )
#         with urllib.request.urlopen(req, timeout=15) as resp:
#             data = json.loads(resp.read())
#         return data["choices"][0]["message"]["content"]

#     def _parse(self, raw: str) -> SupervisorDecision:
#         import json
#         import re
#         m = re.search(r'\{.*\}', raw, re.DOTALL)
#         if not m:
#             logger.warning("SupervisorLLM : structure JSON introuvable dans '%s'", raw[:120])
#             return SupervisorDecision()
#         obj = json.loads(m.group())
#         try:
#             dec = Decision(obj.get("decision", "CONTINUER").upper())
#         except ValueError:
#             dec = Decision.CONTINUER
#         return SupervisorDecision(decision=dec, message=obj.get("message", "").strip())


# # ============================================================================
# # VoiceIO
# # ============================================================================

# class VoiceIO:
#     """Couche basse — reconnaissance vocale et synthèse vocale.

#     Principes fondamentaux
#     ----------------------
#     1. speak() est TOUJOURS bloquant dans le fil principal.
#        Une synthèse non bloquante avant écoute = écho capturé par le moteur de
#        reconnaissance.
#     2. Le microphone n'est jamais ouvert pendant la synthèse vocale.
#     3. L'enregistrement utilise la détection automatique de voix, pas une durée fixe.
#     4. interrupt_and_speak() coupe l'audio en cours avant de parler (alertes STOP).
#     5. play_earcon() est toujours non bloquant et très court (moins de 400 ms) :
#        il ne doit jamais retarder le flux conversationnel.
#     """

#     def __init__(
#         self,
#         stt_backend:   str = "whisper",
#         tts_backend:   str = TTS_DEFAULT_BACKEND,
#         language:      str = "fr",
#         whisper_model: str = WHISPER_DEFAULT_MODEL,
#         coqui_model:   str = COQUI_MODEL_FR,
#         piper_model:   str = PIPER_MODEL_FR,
#     ) -> None:
#         self.stt_backend      = stt_backend
#         self.tts_backend      = tts_backend
#         self.language         = language
#         self.whisper_model_id = whisper_model
#         self.coqui_model_id   = coqui_model
#         self.piper_model_id   = piper_model

#         self._recognizer    = None
#         self._whisper_model = None
#         self._tts_engine    = None
#         self._coqui_model   = None
#         self._lock_tts      = threading.Lock()

#         self._init()

#     # ------------------------------------------------------------------
#     # Initialisation
#     # ------------------------------------------------------------------

#     def _init(self) -> None:
#         self._init_stt()
#         self._init_tts()
#         logger.info(
#             "VoiceIO prêt — Reconnaissance : %s | Synthèse : %s | Langue : %s",
#             self.stt_backend, self.tts_backend, self.language,
#         )

#     def _init_stt(self) -> None:
#         try:
#             import speech_recognition as sr
#             self._recognizer = sr.Recognizer()
#             self._recognizer.energy_threshold         = 4000
#             self._recognizer.pause_threshold          = STT_SILENCE_TIMEOUT
#             self._recognizer.dynamic_energy_threshold = True
#         except ImportError:
#             raise RuntimeError(
#                 "Module SpeechRecognition manquant. "
#                 "Installez-le avec : pip install SpeechRecognition PyAudio"
#             )
#         if self.stt_backend == "whisper":
#             self._whisper_model = self._load_whisper()

#     # def _load_whisper(self) -> object:
#     #     try:
#     #         from faster_whisper import WhisperModel
#     #         logger.info("Chargement du modèle Faster Whisper '%s'...", self.whisper_model_id)
#     #         model = WhisperModel(
#     #             self.whisper_model_id,
#     #             device="cpu",
#     #             compute_type="int8",
#     #         )
#     #         logger.info("Faster Whisper prêt")
#     #         return model
#     #     except ImportError:
#     #         raise RuntimeError(
#     #             "Module faster-whisper manquant. Installez-le avec : pip install faster-whisper"
#     #         )
#     def _load_whisper(self) -> object:
#         try:
#             from faster_whisper import WhisperModel
#         except ImportError:
#             raise RuntimeError(
#                 "Module faster-whisper manquant. Installez-le avec : pip install faster-whisper"
#             )

#         logger.info("Chargement du modèle Faster Whisper '%s'...", self.whisper_model_id)
        
#         # Liste ordonnée de types de calcul à tester sur CPU
#         compute_types = ["int8", "int8_float32", "float32"]
#         last_exception = None
        
#         for c_type in compute_types:
#             try:
#                 logger.info("Tentative d'initialisation de WhisperModel (compute_type=%s)...", c_type)
#                 model = WhisperModel(
#                     self.whisper_model_id,
#                     device="cpu",
#                     compute_type=c_type,
#                 )
#                 logger.info("Faster Whisper prêt avec compute_type=%s", c_type)
#                 return model
#             except Exception as exc:
#                 logger.warning(
#                     "Échec d'initialisation de Whisper avec compute_type=%s : %s", 
#                     c_type, exc
#                 )
#                 last_exception = exc

#         # Si toutes les tentatives échouent, nous informons clairement l'utilisateur des pistes de résolution
#         raise RuntimeError(
#             "Impossible d'initialiser WhisperModel sur le processeur (CPU).\n"
#             "Causes courantes :\n"
#             "1. Runtimes MS Visual C++ manquants. Installez le package redistribuable Visual C++ X64.\n"
#             "2. Problème d'accès aux DLL de ctranslate2.\n"
#             "Vous pouvez essayer de lancer l'application avec le moteur en ligne : --stt-backend google"
#         ) from last_exception
    
#     def _init_tts(self) -> None:
#         chain = (
#             [self.tts_backend]
#             + [b for b in TTS_FALLBACK_CHAIN if b != self.tts_backend]
#         )
#         for backend in chain:
#             try:
#                 if backend == "coqui":
#                     self._init_coqui()
#                 elif backend == "piper":
#                     self._init_piper()
#                 elif backend == "gtts":
#                     self._init_gtts()
#                 elif backend == "pyttsx3":
#                     self._init_pyttsx3()
#                 else:
#                     continue
#                 self.tts_backend = backend
#                 logger.info("Moteur de synthèse actif : %s", backend)
#                 return
#             except Exception as exc:
#                 logger.warning(
#                     "Moteur '%s' indisponible : %s — essai du suivant", backend, exc
#                 )

#         raise RuntimeError(
#             "Aucun moteur de synthèse vocale disponible. "
#             "Installez au minimum : pip install coqui-tts sounddevice soundfile"
#         )

#     # ------------------------------------------------------------------
#     # Initialisation Coqui VITS — voix neurale française hors ligne
#     # ------------------------------------------------------------------

#     def _init_coqui(self) -> None:
#         try:
#             from TTS.api import TTS as CoquiTTS
#             import sounddevice  # noqa: F401
#             import soundfile    # noqa: F401
#         except ImportError:
#             raise RuntimeError(
#                 "Module Coqui manquant. Installez-le avec : pip install coqui-tts sounddevice soundfile"
#             )
#         logger.info("Chargement de Coqui '%s'...", self.coqui_model_id)
#         self._coqui_model = CoquiTTS(
#             model_name=self.coqui_model_id,
#             progress_bar=False,
#             gpu=False,
#         )
#         logger.info("Coqui prêt")

#     # ------------------------------------------------------------------
#     # Initialisation Piper — voix neurale française hors ligne, très rapide
#     # ------------------------------------------------------------------

#     def _init_piper(self) -> None:
#         try:
#             import piper  # noqa: F401
#         except ImportError:
#             raise RuntimeError("Module piper-tts manquant. Installez-le avec : pip install piper-tts")
#         logger.info("Piper disponible — modèle '%s'", self.piper_model_id)

#     # ------------------------------------------------------------------
#     # Initialisation Google Synthèse vocale — en ligne
#     # ------------------------------------------------------------------

#     def _init_gtts(self) -> None:
#         try:
#             import gtts    # noqa: F401
#             import pygame  # noqa: F401
#         except ImportError:
#             raise RuntimeError(
#                 "Modules gTTS ou pygame manquants. Installez-les avec : pip install gTTS pygame"
#             )
#         logger.info("Google Synthèse vocale initialisée")

#     # ------------------------------------------------------------------
#     # Initialisation pyttsx3 — solution de secours ultime
#     # ------------------------------------------------------------------

#     def _init_pyttsx3(self) -> None:
#         try:
#             import pyttsx3
#         except ImportError:
#             raise RuntimeError(
#                 "Module pyttsx3 manquant. Installez-le avec : pip install pyttsx3"
#             )

#         engine = pyttsx3.init()
#         engine.setProperty("rate",   TTS_SPEECH_RATE)
#         engine.setProperty("volume", TTS_VOLUME)

#         fr_voice_found = False
#         # Priorité 1 : voix fr_FR espeak-ng (accent français métropolitain)
#         # Priorité 2 : toute voix contenant "french" ou "fr" dans le nom ou l'identifiant
#         for priority in ("fr_FR", "fr-FR", "french", "fr"):
#             for v in engine.getProperty("voices"):
#                 name_lower = v.name.lower()
#                 id_lower   = v.id.lower()
#                 if priority.lower() in id_lower or priority.lower() in name_lower:
#                     engine.setProperty("voice", v.id)
#                     logger.info(
#                         "pyttsx3 : voix française sélectionnée : %s (%s)", v.name, v.id
#                     )
#                     fr_voice_found = True
#                     break
#             if fr_voice_found:
#                 break

#         if not fr_voice_found:
#             logger.warning(
#                 "Aucune voix française trouvée dans pyttsx3. "
#                 "Sur Linux : sudo apt install espeak-ng-data"
#             )

#         self._tts_engine = engine
#         logger.info("pyttsx3 initialisé (voix système)")

#     # ------------------------------------------------------------------
#     # Synthèse vocale — TOUJOURS bloquante dans le fil principal
#     # ------------------------------------------------------------------

#     def interrupt_and_speak(self, text: str) -> None:
#         """Coupe l'audio en cours PUIS parle. Réservé aux alertes STOP urgentes."""
#         self._stop_audio()
#         self.speak(text)

#     def _stop_audio(self) -> None:
#         """Arrête immédiatement la lecture audio (tous moteurs)."""
#         try:
#             if self.tts_backend in ("coqui", "piper"):
#                 import sounddevice as sd
#                 sd.stop()
#             elif self.tts_backend == "gtts":
#                 try:
#                     import pygame
#                     if pygame.mixer.get_init():
#                         pygame.mixer.music.stop()
#                 except Exception:
#                     pass
#         except Exception as exc:
#             logger.debug("_stop_audio : %s", exc)

#     @staticmethod
#     def _sanitize_tts(text: str) -> str:
#         """Nettoie le texte avant synthèse vocale.

#         Transformations appliquées dans l'ordre :
#         1. Blocs de code Markdown (``` … ```) → supprimés
#         2. Emphase Markdown (* ** _ __ ~ ~~)  → supprimée (le texte reste)
#         3. Titres Markdown (# ## ###…)         → supprimés (le texte reste)
#         4. Adresses web (http / https / ftp)   → remplacées par « lien »
#         5. Ponctuation non orale               → remplacée ou supprimée
#         6. Espaces multiples et lignes vides   → normalisés
#         """
#         import re

#         # 1. Blocs de code (``` … ```) et code en ligne (` … `)
#         text = re.sub(r'```.*?```', '', text, flags=re.DOTALL)
#         text = re.sub(r'`[^`]*`', '', text)

#         # 2. Emphase Markdown
#         text = re.sub(r'\*{1,3}|_{1,3}|~{1,2}', '', text)

#         # 3. Titres Markdown en début de ligne
#         text = re.sub(r'^\s*#{1,6}\s*', '', text, flags=re.MULTILINE)

#         # 4. Adresses web
#         text = re.sub(r'https?://\S+|ftp://\S+', 'lien', text)

#         # 5. Ponctuation non orale
#         text = re.sub(r'^\s*[-•–—]\s+', '', text, flags=re.MULTILINE)
#         text = re.sub(r'^\s*[\-|: ]{3,}\s*$', '', text, flags=re.MULTILINE)
#         text = re.sub(r'\|', ' ', text)
#         text = re.sub(r'[\\/@#$%^&{}\[\]<>=]', ' ', text)
#         text = re.sub(r'[(){}\[\]]', ' ', text)
#         text = re.sub(r'\.{2,}', ',', text)
#         text = re.sub(r'\s*[–—]\s*', ', ', text)
#         text = re.sub(r'\*+', '', text)
#         text = re.sub(r'_+', ' ', text)

#         # 6. Normalisation des espaces et des sauts de ligne
#         text = re.sub(r'\n+', ' ', text)
#         text = re.sub(r' {2,}', ' ', text)

#         return text.strip()

#     def speak(self, text: str, *, blocking: bool = True) -> None:
#         """Synthèse vocale en français natif.

#         blocking=True (par défaut) : retourne APRÈS la fin de la lecture.
#         blocking=False             : usage exceptionnel uniquement —
#                                      par exemple, phrases de patience émises
#                                      par PatienceManager pendant qu'un autre fil
#                                      attend le modèle de langage. Dans ce cas,
#                                      le microphone n'est pas sollicité en parallèle,
#                                      donc pas de risque d'écho capturé.
#         RÈGLE : ne JAMAIS appeler avec blocking=False juste avant écoute().
#         """
#         if not text or not text.strip():
#             return
#         text = self._sanitize_tts(text)
#         if not text:
#             return
#         logger.info("Synthèse [%s] : '%s'", self.tts_backend, text[:80])

#         dispatch = {
#             "coqui":   self._speak_coqui,
#             "piper":   self._speak_piper,
#             "gtts":    self._speak_gtts,
#             "pyttsx3": self._speak_pyttsx3,
#         }
#         fn = dispatch.get(self.tts_backend)
#         if fn is None:
#             logger.error("Moteur de synthèse inconnu : %s", self.tts_backend)
#             print("[Synthèse] " + text)
#             return
#         fn(text, blocking)

#     # ------------------------------------------------------------------
#     # Signaux d'ambiance — retour sonore court pendant les attentes
#     # ------------------------------------------------------------------
#     # Générés à la volée (sinusoïdes), aucune dépendance audio externe
#     # supplémentaire au-delà de sounddevice (déjà requis par coqui/piper).
#     # En cas d'indisponibilité : dégradation silencieuse, sans exception
#     # propagée ni affichage parasite — un signal manqué ne doit jamais
#     # bloquer le flux conversationnel.
#     # ------------------------------------------------------------------

#     _EARCON_PROFILES = {
#         # (fréquence Hz, durée s, amplitude) — profils courts et discrets
#         "patience_short":  (880.0, 0.10, 0.15),   # signal discret, attente courte
#         "patience_medium": (660.0, 0.15, 0.18),   # signal intermédiaire
#         "patience_long":   (440.0, 0.22, 0.20),   # signal grave, longue attente
#     }

#     def play_earcon(self, profile: str) -> None:
#         """Joue un signal d'ambiance court et non bloquant. Échec silencieux."""
#         params = self._EARCON_PROFILES.get(profile)
#         if params is None:
#             return
#         try:
#             threading.Thread(
#                 target=self._play_earcon_sync, args=(params,), daemon=True
#             ).start()
#         except Exception as exc:
#             logger.debug("play_earcon : %s", exc)

#     def _play_earcon_sync(self, params) -> None:
#         freq, duration, amplitude = params
#         try:
#             import sounddevice as sd
#             sample_rate = 22050
#             n_samples = int(sample_rate * duration)
#             tone = [
#                 amplitude * math.sin(2 * math.pi * freq * (i / sample_rate))
#                 for i in range(n_samples)
#             ]
#             sd.play(tone, sample_rate)
#             sd.wait()
#         except Exception as exc:
#             logger.debug("Signal d'ambiance indisponible (%s), ignoré", exc)

#     # ------------------------------------------------------------------
#     # Moteur Coqui — référence qualité
#     # ------------------------------------------------------------------

#     def _speak_coqui(self, text: str, blocking: bool) -> None:
#         tmp_path: Optional[str] = None
#         try:
#             import soundfile as sf
#             import sounddevice as sd

#             with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
#                 tmp_path = f.name

#             with self._lock_tts:
#                 self._coqui_model.tts_to_file(text=text, file_path=tmp_path)

#             data, sr = sf.read(tmp_path, dtype="float32")
#             if blocking:
#                 sd.play(data, sr)
#                 sd.wait()
#             else:
#                 sd.play(data, sr)

#         except Exception as exc:
#             logger.error("Coqui erreur : %s", exc)
#             print("[Synthèse] " + text)
#         finally:
#             if tmp_path and os.path.exists(tmp_path):
#                 try:
#                     os.unlink(tmp_path)
#                 except OSError:
#                     pass

#     # ------------------------------------------------------------------
#     # Moteur Piper — latence minimale
#     # ------------------------------------------------------------------

#     def _speak_piper(self, text: str, blocking: bool) -> None:
#         tmp_path: Optional[str] = None
#         try:
#             import subprocess
#             import soundfile as sf
#             import sounddevice as sd

#             with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
#                 tmp_path = f.name

#             result = subprocess.run(
#                 ["piper", "--model", self.piper_model_id, "--output_file", tmp_path],
#                 input=text.encode("utf-8"),
#                 capture_output=True,
#                 timeout=30,
#             )
#             if result.returncode != 0:
#                 raise RuntimeError(
#                     "piper code de retour=%d : %s" % (
#                         result.returncode, result.stderr.decode()
#                     )
#                 )

#             data, sr = sf.read(tmp_path, dtype="float32")
#             if blocking:
#                 sd.play(data, sr)
#                 sd.wait()
#             else:
#                 sd.play(data, sr)

#         except FileNotFoundError:
#             logger.error("Exécutable 'piper' introuvable. pip install piper-tts")
#             print("[Synthèse] " + text)
#         except Exception as exc:
#             logger.error("Piper erreur : %s", exc)
#             print("[Synthèse] " + text)
#         finally:
#             if tmp_path and os.path.exists(tmp_path):
#                 try:
#                     os.unlink(tmp_path)
#                 except OSError:
#                     pass

#     # ------------------------------------------------------------------
#     # Moteur Google Synthèse vocale — en ligne
#     # ------------------------------------------------------------------

#     def _speak_gtts(self, text: str, blocking: bool) -> None:
#         tmp_path: Optional[str] = None
#         try:
#             from gtts import gTTS
#             import pygame

#             tts = gTTS(text=text, lang=self.language, slow=False)
#             with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
#                 tmp_path = f.name
#             tts.save(tmp_path)

#             # Réinitialisation propre du mixeur à chaque appel
#             if pygame.mixer.get_init():
#                 pygame.mixer.quit()
#             pygame.mixer.init(frequency=22050, size=-16, channels=1, buffer=512)
#             pygame.mixer.music.load(tmp_path)
#             pygame.mixer.music.play()

#             if blocking:
#                 while pygame.mixer.music.get_busy():
#                     time.sleep(0.05)
#                 pygame.mixer.quit()

#         except Exception as exc:
#             logger.error("Google Synthèse vocale erreur : %s", exc)
#             print("[Synthèse] " + text)
#         finally:
#             if tmp_path and os.path.exists(tmp_path):
#                 try:
#                     time.sleep(0.1)
#                     os.unlink(tmp_path)
#                 except OSError:
#                     pass

#     # ------------------------------------------------------------------
#     # Moteur pyttsx3 — solution de secours ultime
#     # ------------------------------------------------------------------

#     def _speak_pyttsx3(self, text: str, blocking: bool) -> None:
#         with self._lock_tts:
#             try:
#                 self._tts_engine.say(text)
#                 if blocking:
#                     self._tts_engine.runAndWait()
#                 else:
#                     t = threading.Thread(
#                         target=self._tts_engine.runAndWait, daemon=True
#                     )
#                     t.start()
#             except Exception as exc:
#                 logger.error("pyttsx3 erreur : %s", exc)
#                 print("[Synthèse] " + text)

#     # ------------------------------------------------------------------
#     # Reconnaissance vocale — fragment avec détection automatique de voix
#     # ------------------------------------------------------------------

#     def listen_chunk(
#         self,
#         *,
#         pause_threshold:   float = STT_SILENCE_TIMEOUT,
#         phrase_time_limit: int   = STT_PHRASE_TIME_LIMIT,
#         listen_timeout:    float = STT_LISTEN_TIMEOUT,
#     ) -> str:
#         """Capture un fragment de parole et le transcrit.

#         Retourne :
#             Le texte transcrit (non vide).

#         Lève :
#             RuntimeError si la capture ou la transcription échoue,
#             ou si aucune voix n'est détectée dans le délai imparti.
#         """
#         import speech_recognition as sr

#         original = self._recognizer.pause_threshold
#         self._recognizer.pause_threshold = pause_threshold
#         tmp_path: Optional[str] = None

#         try:
#             with sr.Microphone() as src:
#                 logger.info(
#                     "Écoute (silence=%.1fs, max=%ds)...",
#                     pause_threshold, phrase_time_limit,
#                 )
#                 self._recognizer.adjust_for_ambient_noise(src, duration=STT_AMBIENT_DURATION)
#                 audio = self._recognizer.listen(
#                     src,
#                     timeout=listen_timeout,
#                     phrase_time_limit=phrase_time_limit,
#                 )

#             with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
#                 tmp_path = f.name
#                 f.write(audio.get_wav_data())

#             if self.stt_backend == "whisper":
#                 return self._transcribe_whisper(tmp_path)
#             else:
#                 return self._transcribe_google(audio)

#         except sr.WaitTimeoutError as exc:
#             raise RuntimeError("Aucune voix détectée dans le délai imparti") from exc

#         finally:
#             self._recognizer.pause_threshold = original
#             if tmp_path and os.path.exists(tmp_path):
#                 try:
#                     os.unlink(tmp_path)
#                 except OSError:
#                     pass

#     def listen_short(self, question: str, timeout: float = 8.0) -> str:
#         """Pose une question brève et attend une réponse courte.
#         Retourne une chaîne vide en cas d'absence de réponse (aucune exception propagée).
#         """
#         self.speak(question)
#         self.speak(pick("listening"))
#         try:
#             return self.listen_chunk(
#                 pause_threshold=1.5,
#                 phrase_time_limit=15,
#                 listen_timeout=timeout,
#             )
#         except RuntimeError as exc:
#             logger.info("listen_short : aucune réponse (%s)", exc)
#             return ""

#     def _transcribe_whisper(self, wav_path: str) -> str:
#         segments_gen, info = self._whisper_model.transcribe(
#             wav_path,
#             language=self.language,
#             beam_size=WHISPER_BEAM_SIZE,
#         )
#         logger.debug(
#             "Whisper : langue=%s (%.0f%%)",
#             info.language, info.language_probability * 100,
#         )
#         text = " ".join(seg.text.strip() for seg in segments_gen).strip()
#         if not text:
#             raise RuntimeError("La reconnaissance vocale n'a produit aucun texte")
#         logger.info("Fragment reconnu : '%s'", text[:100])
#         return text

#     def _transcribe_google(self, audio) -> str:
#         import speech_recognition as sr
#         lang = "fr-FR" if self.language == "fr" else (self.language + "-" + self.language.upper())
#         try:
#             text = self._recognizer.recognize_google(audio, language=lang)
#             logger.info("Reconnaissance Google : '%s'", text[:100])
#             return text
#         except sr.UnknownValueError:
#             raise RuntimeError("Reconnaissance Google : audio incompréhensible")
#         except sr.RequestError as exc:
#             raise RuntimeError("Reconnaissance Google : erreur de service : %s" % exc)

#     # ------------------------------------------------------------------
#     # Nettoyage
#     # ------------------------------------------------------------------

#     def close(self) -> None:
#         self._stop_audio()
#         if self._tts_engine is not None:
#             try:
#                 with self._lock_tts:
#                     self._tts_engine.stop()
#             except Exception:
#                 pass
#         logger.info("VoiceIO fermé")


# # ============================================================================
# # VRScenarioApp — orchestration principale
# # ============================================================================

# class VRScenarioApp:
#     """
#     Flux en deux phases :

#     PHASE 1 — Génération et présentation du scénario
#       - Saisie vocale du thème
#       - Le modèle de langage génère un scénario structuré
#       - Construction de la session de scénario
#       - Lecture du résumé oral par synthèse vocale

#     PHASE 2 — Questions et réponses supervisées
#       - L'utilisateur pose librement ses questions à voix haute
#       - Le modèle répond en s'appuyant sur le scénario généré
#       - Le superviseur évalue chaque échange : CONTINUER / CONSEIL / STOP
#       - Un mot de sortie clôt proprement la session

#     Gestion de la patience
#     ----------------------
#     Toute attente potentiellement longue (génération de scénario, appel
#     au modèle en questions-réponses) est encadrée par PatienceManager,
#     qui pilote automatiquement les signaux d'ambiance et les phrases de
#     transition selon la durée réelle d'attente.
#     """

#     def __init__(self, io: VoiceIO) -> None:
#         self.io = io
#         self.patience = PatienceManager(io)

#     def run(self) -> None:
#         self._welcome()
#         topic      = self._ask_topic()
#         config     = self._setup_llm()
#         supervisor = SupervisorLLM(config)

#         # -- Phase 1 : génération et présentation -------------------------
#         scenario_session = self._generate_and_announce(topic, config)

#         # -- Phase 2 : questions-réponses supervisées ---------------------
#         self._qa_loop(scenario_session, supervisor, config)

#         self._goodbye()

#     # ------------------------------------------------------------------
#     # Phase 1 : génération du scénario
#     # ------------------------------------------------------------------

#     def _welcome(self) -> None:
#         print("\n" + "=" * 60)
#         print("  APPLICATION VOCALE — SCÉNARIOS DE FORMATION EN RÉALITÉ VIRTUELLE")
#         print("=" * 60)
#         self.io.speak(
#             "Bienvenue dans votre assistant vocal de scénarios de formation. "
#             "Je vais générer un scénario à partir du thème que vous me donnerez, "
#             "vous en présenter les grandes lignes, "
#             "puis répondre à vos questions. "
#             "Dites terminer à tout moment pour clore la session."
#         )

#     def _ask_topic(self) -> str:
#         """Capture le thème par la voix avec confirmation orale explicite.

#         La reconnaissance vocale peut mal comprendre le thème prononcé
#         (homophones, bruit ambiant, accent). Générer un scénario complet sur
#         un thème erroné coûte cher en temps et en confiance utilisateur :
#         on confirme donc systématiquement avant de poursuivre.

#         Stratégie :
#           1. Capture du thème (écoute courte, déjà tolérante au silence).
#           2. Confirmation orale explicite ("Le thème retenu est X, correct ?").
#           3. Nouvelle tentative si infirmé, absent ou ambigu — jusqu'à
#              TOPIC_MAX_ATTEMPTS.
#           4. Repli sur un thème par défaut si aucune confirmation n'est obtenue
#              (dégradation silencieuse : la session continue malgré tout).

#         Toute erreur inattendue de la couche vocale (microphone, moteur STT)
#         est absorbée localement : un échec de capture du thème ne doit jamais
#         interrompre la session.
#         """
#         prompt = (
#             "Sur quel thème souhaitez-vous travailler ? "
#             "Vous pouvez me dire, par exemple : la consignation gaz, "
#             "la sécurité incendie, ou les premiers secours."
#         )
#         for attempt in range(1, TOPIC_MAX_ATTEMPTS + 1):
#             try:
#                 text = self.io.listen_short(prompt)
#             except Exception as exc:
#                 logger.warning(
#                     "Capture du thème échouée (tentative %d/%d) : %s",
#                     attempt, TOPIC_MAX_ATTEMPTS, exc,
#                 )
#                 text = ""

#             if text and self._confirm_topic(text):
#                 self.io.speak("Très bien. Le thème retenu est : " + text + ".")
#                 logger.info("Thème confirmé : '%s'", text)
#                 print("\nThème : " + text)
#                 return text

#             logger.info(
#                 "Thème non confirmé (tentative %d/%d) : '%s'",
#                 attempt, TOPIC_MAX_ATTEMPTS, text,
#             )
#             if attempt < TOPIC_MAX_ATTEMPTS:
#                 prompt = "Je vous écoute à nouveau. Quel est le thème souhaité ?"
#                 self.io.speak("D'accord, reprenons.")

#         text = "sécurité industrielle"
#         self.io.speak(
#             "Je n'arrive pas à confirmer le thème. "
#             "Je vais utiliser la sécurité industrielle par défaut."
#         )
#         logger.info("Thème : repli par défaut '%s'", text)
#         print("\nThème : " + text)
#         return text

#     def _confirm_topic(self, topic: str) -> bool:
#         """Demande une confirmation orale explicite du thème compris.

#         Retourne False par défaut (réponse absente, ambiguë, ou erreur de capture) :
#         en cas de doute, on retente plutôt que de générer un scénario hors sujet.
#         """
#         try:
#             answer = self.io.listen_short(
#                 "Le thème retenu est : " + topic + ". Est-ce correct ? Dites oui ou non."
#             ).lower()
#         except Exception as exc:
#             logger.debug("_confirm_topic : %s", exc)
#             return False
#         if any(w in answer for w in TOPIC_CONFIRM_NO):
#             return False
#         return any(w in answer for w in TOPIC_CONFIRM_YES)

#     def _generate_and_announce(self, topic: str, config) -> "ScenarioSession | None":
#         """
#         Appelle le modèle pour générer le scénario, construit la session,
#         et lit le résumé oral.
#         Retourne None si la génération échoue (les questions-réponses restent possibles).

#         La génération peut prendre plusieurs secondes. Elle est encadrée par
#         PatienceManager qui gère automatiquement les signaux d'ambiance et
#         les phrases de transition selon la durée réelle d'attente.
#         """
#         print("\nGénération du scénario en cours…")

#         scenario_json: Dict[str, Any] = {}
#         scenario_text: str = ""

#         def _do_generate():
#             nonlocal scenario_text, scenario_json
#             try:
#                 from vr_scenario_lib.scenario import generate_scenario as lib_generate
#                 result = lib_generate(topic=topic, llm_config=config)
#                 if isinstance(result, tuple):
#                     scenario_text, scenario_json = result[0], result[1]
#                 else:
#                     scenario_text = getattr(result, "text", str(result))
#                     scenario_json = getattr(result, "json", {})
#                 logger.info(
#                     "Scénario généré via la bibliothèque (%d caractères)", len(scenario_text)
#                 )
#             except Exception as exc:
#                 logger.warning(
#                     "Bibliothèque indisponible : %s — génération directe", exc
#                 )
#                 scenario_json, scenario_text = self._generate_via_llm(topic, config)

#         self.patience.run_with_patience(_do_generate)

#         if not scenario_json and not scenario_text:
#             self.io.speak(
#                 "La génération du scénario n'a pas abouti. "
#                 "Vous pouvez néanmoins me poser vos questions directement."
#             )
#             return None

#         # -- Construction de la session -----------------------------------
#         now = datetime.now(timezone.utc).isoformat()
#         try:
#             from vr_scenario_lib.scenario_store import ScenarioSession
#             session = ScenarioSession(
#                 scenario_id   = str(uuid.uuid4()),
#                 topic         = topic,
#                 scenario_text = scenario_text,
#                 scenario_json = scenario_json,
#                 created_at    = now,
#                 updated_at    = now,
#             )
#             logger.info("Session créée (identifiant=%s)", session.scenario_id)
#         except Exception as exc:
#             logger.warning("Création de session impossible : %s", exc)
#             session = None

#         # -- Présentation vocale du scénario ------------------------------
#         self._announce_scenario(scenario_json, scenario_text)
#         return session

#     def _generate_via_llm(
#         self, topic: str, config
#     ) -> "tuple[Dict[str, Any], str]":
#         """
#         Appel direct au modèle pour générer le scénario.
#         Retourne ({}, "") en cas d'échec.
#         """
#         if config is None:
#             return self._fallback_static_scenario(topic)

#         user_msg = "Génère un scénario de formation en réalité virtuelle sur le thème : " + topic

#         try:
#             raw = self._call_llm_raw(
#                 system     = SCENARIO_GEN_SYSTEM,
#                 user       = user_msg,
#                 config     = config,
#                 max_tokens = SCENARIO_GEN_MAX_TOKENS,
#             )
#         except Exception as exc:
#             logger.error("Génération par le modèle échouée : %s", exc)
#             return self._fallback_static_scenario(topic)

#         try:
#             import re
#             m = re.search(r'\{.*\}', raw, re.DOTALL)
#             if not m:
#                 raise ValueError("Structure JSON introuvable")
#             obj = json.loads(m.group())
#         except Exception as exc:
#             logger.error("Analyse du scénario échouée : %s | brut=%s", exc, raw[:200])
#             return self._fallback_static_scenario(topic)

#         text = self._json_to_text(obj, topic)
#         return obj, text

#     @staticmethod
#     def _json_to_text(obj: Dict[str, Any], topic: str) -> str:
#         """Convertit le scénario structuré en texte lisible."""
#         lines = ["# SCÉNARIO DE FORMATION — " + topic.upper(), ""]
#         titre = obj.get("titre", topic)
#         lines += ["## " + titre, ""]

#         objectifs = obj.get("objectifs", [])
#         if objectifs:
#             lines.append("### Objectifs")
#             for o in objectifs:
#                 lines.append("- " + str(o))
#             lines.append("")

#         for etape in obj.get("grandes_lignes", []):
#             num    = etape.get("etape", "")
#             titre_e = etape.get("titre", "")
#             desc   = etape.get("description", "")
#             lines.append("### Étape %s : %s" % (num, titre_e))
#             lines.append(desc)
#             lines.append("")

#         procs = obj.get("procedures_cles", [])
#         if procs:
#             lines.append("### Procédures clés")
#             for p in procs:
#                 lines.append("- " + str(p))
#             lines.append("")

#         vigilance = obj.get("points_vigilance", [])
#         if vigilance:
#             lines.append("### Points de vigilance")
#             for v in vigilance:
#                 lines.append("- " + str(v))
#             lines.append("")

#         return "\n".join(lines)

#     @staticmethod
#     def _fallback_static_scenario(topic: str) -> "tuple[Dict[str, Any], str]":
#         """Scénario minimal si le modèle de langage est inaccessible."""
#         obj = {
#             "titre": "Scénario " + topic,
#             "objectifs": [
#                 "Comprendre les principes fondamentaux de " + topic,
#                 "Maîtriser les procédures de sécurité essentielles",
#                 "Réagir de façon appropriée aux situations d'urgence",
#             ],
#             "grandes_lignes": [
#                 {
#                     "etape": 1,
#                     "titre": "Préparation",
#                     "description": "Vérifier les équipements et les protections individuelles avant toute intervention.",
#                 },
#                 {
#                     "etape": 2,
#                     "titre": "Intervention",
#                     "description": "Appliquer les procédures standard en respectant les consignes de sécurité.",
#                 },
#                 {
#                     "etape": 3,
#                     "titre": "Clôture",
#                     "description": "Consigner les actions effectuées et signaler tout incident survenu.",
#                 },
#             ],
#             "procedures_cles": [
#                 "Vérifier les équipements avant toute intervention",
#                 "Respecter les périmètres de sécurité",
#                 "Alerter la hiérarchie en cas d'incident",
#             ],
#             "points_vigilance": [
#                 "Ne jamais intervenir seul",
#                 "Toujours porter les protections adaptées à la situation",
#             ],
#             "resume_oral": (
#                 "Ce scénario porte sur le thème " + topic + ". "
#                 "Il se déroule en trois étapes : la préparation du matériel, "
#                 "l'intervention selon les procédures standard, "
#                 "et la clôture avec consignation des actions effectuées."
#             ),
#         }
#         text = VRScenarioApp._json_to_text(obj, topic)
#         return obj, text

#     def _announce_scenario(self, scenario_json: Dict[str, Any], scenario_text: str) -> None:
#         # """Présente les grandes lignes du scénario à voix haute."""
#         # print("\n" + "=" * 60)
#         # print("  SCÉNARIO GÉNÉRÉ")
#         # print("=" * 60)
#         # print(scenario_text[:1200] + ("…" if len(scenario_text) > 1200 else ""))
#         print("\n" + "=" * 60)
#         print("  SCÉNARIO TEXTUEL")
#         print("=" * 60)
#         print(scenario_text)
#         print("=" * 60)
#         # --- AJOUT : Affichage du JSON de configuration généré ---
#         print("\n" + "=" * 60)
#         print("  SCÉNARIO GÉNÉRÉ (JSON)")
#         print("=" * 60)
#         print(json.dumps(scenario_json, indent=2, ensure_ascii=False))
#         print("=" * 60 + "\n")
#         # ---------------------------------------------------------
#         # Lecture du résumé oral (conçu pour la synthèse vocale, sans listes)
#         resume = scenario_json.get("resume_oral", "")
#         if not resume:
#             titre = scenario_json.get("titre", "le scénario")
#             etapes = scenario_json.get("grandes_lignes", [])
#             if etapes:
#                 noms = ", ".join(str(e.get("titre", "")) for e in etapes[:4])
#                 resume = (
#                     "Le scénario intitulé " + titre
#                     + " se déroule en " + str(len(etapes))
#                     + " étapes : " + noms + "."
#                 )
#             else:
#                 resume = "Le scénario " + titre + " vient d'être généré."

#         self.io.speak("Voici les grandes lignes de votre scénario.")
#         self.io.speak(resume)

#         # Points de vigilance, si présents
#         vigilance = scenario_json.get("points_vigilance", [])
#         if vigilance:
#             points = " et ".join(vigilance[:3])
#             self.io.speak("Les points de vigilance à retenir sont : " + points + ".")

#         self.io.speak(
#             "Le scénario est prêt. "
#             "Posez-moi vos questions quand vous voulez. "
#             "Dites terminer pour clore la session."
#         )

#     # ------------------------------------------------------------------
#     # Phase 2 : questions-réponses supervisées
#     # ------------------------------------------------------------------

#     def _qa_loop(
#         self,
#         scenario_session,   # ScenarioSession | None
#         supervisor: SupervisorLLM,
#         config,
#     ) -> None:
#         """Boucle de questions et réponses supervisées.

#         Gestion du silence en trois niveaux :
#           Niveau 1 — silence léger    : on relance l'écoute sans rien dire
#           Niveau 2 — relance douce    : après le premier délai, une phrase
#                                         courte rassure sans interroger
#           Niveau 3 — silence prolongé : après plusieurs délais, question
#                                         explicite pour continuer ou terminer
#         """
#         print("\n" + "-" * 60)
#         print("[ SESSION DE QUESTIONS — posez vos questions ]")
#         print("-" * 60)

#         narrator = NarratorSession(
#             topic=scenario_session.topic if scenario_session else "général"
#         )
#         consecutive_timeouts = 0
#         MAX_TIMEOUTS  = 3
#         SOFT_NUDGE_AT = 1

#         while True:

#             # ---- 1. Capture de la question ---------------------------------
#             self.io.speak(pick("listening"))
#             try:
#                 question = self.io.listen_chunk(
#                     pause_threshold   = STT_SILENCE_TIMEOUT,
#                     phrase_time_limit = STT_PHRASE_TIME_LIMIT,
#                     listen_timeout    = STT_LISTEN_TIMEOUT,
#                 )
#                 consecutive_timeouts = 0
#             except RuntimeError as exc:
#                 consecutive_timeouts += 1
#                 logger.info(
#                     "Délai Q&R %d/%d : %s", consecutive_timeouts, MAX_TIMEOUTS, exc
#                 )

#                 if consecutive_timeouts >= MAX_TIMEOUTS:
#                     if self._ask_continue_qa():
#                         consecutive_timeouts = 0
#                     else:
#                         break
#                 elif consecutive_timeouts == SOFT_NUDGE_AT:
#                     self.io.speak(pick("soft_nudge"))
#                 continue

#             # ---- 2. Détection d'un mot de sortie ---------------------------
#             if any(w in question.lower() for w in EXIT_WORDS):
#                 print("\nSortie Q&R : '%s'" % question)
#                 break

#             print("\n[Question] " + question)
#             narrator.add_chunk(question)

#             # ---- 3. Réponse du modèle (avec patience) ----------------------
#             answer = self.patience.run_with_patience(
#                 self._get_answer, question, scenario_session, config
#             )
#             print("[Réponse] " + answer)
#             self.io.speak(answer)

#             # ---- 4. Supervision de l'échange -------------------------------
#             exchange = "Question : " + question + "\nRéponse : " + answer
#             decision = supervisor.analyse(narrator, exchange)
#             logger.info(
#                 "Superviseur Q&R : %s | '%s'",
#                 decision.decision.value,
#                 decision.message[:60] if decision.message else "",
#             )

#             if decision.decision == Decision.CONSEIL:
#                 print("\n[CONSEIL] " + decision.message)
#                 self.io.speak(decision.message)

#             elif decision.decision == Decision.STOP:
#                 print("\n[STOP] " + decision.message)
#                 self.io.interrupt_and_speak(decision.message)
#                 if not self._handle_stop_qa():
#                     break

#     @staticmethod
#     def _strip_filler_words(text: str) -> str:
#         """Supprime les locutions de remplissage les plus courantes (cf. FILLER_PATTERNS_FR).

#         Dégradation silencieuse : en cas d'erreur de traitement, le texte original
#         est retourné inchangé plutôt que de propager une exception pour un simple
#         nettoyage cosmétique (standard de robustesse : ne jamais casser la session
#         vocale pour une amélioration non critique).
#         """
#         if not text:
#             return text
#         try:
#             import re
#             cleaned = text
#             for pattern in FILLER_PATTERNS_FR:
#                 cleaned = re.sub(pattern, "", cleaned, flags=re.IGNORECASE | re.MULTILINE)
#             cleaned = re.sub(r"\s{2,}", " ", cleaned).strip()
#             cleaned = re.sub(r"^[,.]\s*", "", cleaned)
#             if cleaned and cleaned[0].islower():
#                 cleaned = cleaned[0].upper() + cleaned[1:]
#             return cleaned if cleaned else text
#         except Exception as exc:
#             logger.debug("_strip_filler_words : %s", exc)
#             return text

#     @staticmethod
#     def _enforce_max_sentences(text: str, max_sentences: int = QA_MAX_SENTENCES) -> str:
#         """Filet de sécurité : tronque la réponse si le modèle ignore la consigne de concision."""
#         if not text:
#             return text
#         try:
#             import re
#             sentences = [s for s in re.split(r'(?<=[.!?])\s+', text.strip()) if s]
#             if len(sentences) <= max_sentences:
#                 return text
#             return " ".join(sentences[:max_sentences])
#         except Exception as exc:
#             logger.debug("_enforce_max_sentences : %s", exc)
#             return text

#     def _get_answer(self, question: str, scenario_session, config) -> str:
#         """
#         Obtient une réponse du modèle à la question posée.
#         Priorité : discuss_scenario() de la bibliothèque, puis appel direct, puis message de repli.
#         Toute réponse exploitable passe par les filets de sécurité de concision
#         (suppression des mots de remplissage, plafond de phrases) avant d'être renvoyée.
#         """
#         # Via la bibliothèque de scénarios
#         if scenario_session is not None and config is not None:
#             try:
#                 from vr_scenario_lib.scenario import discuss_scenario
#                 reply = discuss_scenario(
#                     session      = scenario_session,
#                     user_message = question,
#                     llm_config   = config,
#                 )
#                 if reply and reply.strip():
#                     reply = self._strip_filler_words(reply.strip())
#                     return self._enforce_max_sentences(reply)
#             except Exception as exc:
#                 logger.warning("discuss_scenario erreur : %s — appel direct", exc)

#         # Appel direct avec contexte du scénario
#         if config is not None:
#             context = (
#                 scenario_session.scenario_text[:800]
#                 if scenario_session and scenario_session.scenario_text
#                 else ""
#             )
#             user_msg = (
#                 ("Contexte du scénario :\n" + context + "\n\n" if context else "")
#                 + "Question de l'apprenant : " + question
#             )
#             try:
#                 reply = self._call_llm_raw(
#                     system     = QA_SYSTEM,
#                     user       = user_msg,
#                     config     = config,
#                     max_tokens = QA_MAX_TOKENS,
#                 ).strip()
#                 reply = self._strip_filler_words(reply)
#                 return self._enforce_max_sentences(reply)
#             except Exception as exc:
#                 logger.error("Appel direct Q&R erreur : %s", exc)

#         return (
#             "Je n'ai pas pu obtenir de réponse pour le moment. "
#             "Vous pouvez reformuler votre question ou consulter la documentation du scénario."
#         )

#     # ------------------------------------------------------------------
#     # Fonctions auxiliaires
#     # ------------------------------------------------------------------

#     @staticmethod
#     def _call_llm_raw(*, system: str, user: str, config, max_tokens: int) -> str:
#         """Appel unifié au modèle de langage : bibliothèque, puis appel direct avec retry.

#         L'appel HTTP direct est retenté jusqu'à LLM_CALL_MAX_RETRIES fois en cas
#         d'erreur réseau, de timeout ou de réponse malformée, avec un délai croissant
#         entre tentatives (backoff linéaire). Lève RuntimeError si toutes les
#         tentatives échouent, pour que l'appelant applique son propre repli.
#         """
#         try:
#             from vr_scenario_lib.llm import call_llm
#             return call_llm(
#                 system=system, user=user,
#                 llm_config=config, max_tokens=max_tokens,
#             )
#         except ImportError:
#             pass

#         import urllib.request
#         import urllib.error

#         payload = json.dumps({
#             "model":      getattr(config, "model", "gpt-3.5-turbo"),
#             "max_tokens": max_tokens,
#             "messages":   [
#                 {"role": "system", "content": system},
#                 {"role": "user",   "content": user},
#             ],
#         }).encode()
#         api_url = getattr(config, "api_url", "https://api.openai.com/v1/chat/completions")
#         token   = getattr(config, "token", "")
#         req = urllib.request.Request(
#             api_url, data=payload,
#             headers={
#                 "Content-Type":  "application/json",
#                 "Authorization": "Bearer " + token,
#             },
#         )

#         last_exc: Optional[Exception] = None
#         total_attempts = LLM_CALL_MAX_RETRIES + 1
#         for attempt in range(1, total_attempts + 1):
#             try:
#                 with urllib.request.urlopen(req, timeout=20) as resp:
#                     data = json.loads(resp.read())
#                 return data["choices"][0]["message"]["content"]
#             except (urllib.error.URLError, TimeoutError, ValueError, KeyError) as exc:
#                 last_exc = exc
#                 logger.warning(
#                     "Appel LLM échoué (tentative %d/%d) : %s", attempt, total_attempts, exc
#                 )
#                 if attempt < total_attempts:
#                     time.sleep(LLM_CALL_RETRY_BACKOFF_S * attempt)

#         raise RuntimeError(
#             "Appel au modèle de langage impossible après %d tentative(s)" % total_attempts
#         ) from last_exc

#     def _ask_continue_qa(self) -> bool:
#         text = self.io.listen_short(pick("no_response_continue_check"))
#         if not text:
#             return False
#         return any(
#             w in text.lower()
#             for w in {"oui", "yes", "continuer", "continue", "si", "d'accord", "bien sûr"}
#         )

#     def _handle_stop_qa(self) -> bool:
#         """Pause après une alerte STOP en phase questions-réponses. Retourne True pour reprendre."""
#         self.io.speak(
#             "La session est interrompue suite à cette alerte. "
#             "Dites reprendre pour continuer vos questions, "
#             "ou terminer pour clore la session."
#         )
#         text = ""
#         try:
#             text = self.io.listen_chunk(
#                 pause_threshold   = 2.0,
#                 phrase_time_limit = 10,
#                 listen_timeout    = 12,
#             )
#         except RuntimeError:
#             pass
#         if any(w in text.lower() for w in {"reprendre", "continuer", "oui", "yes", "d'accord"}):
#             self.io.speak("Très bien. Je reste à l'écoute de vos questions.")
#             return True
#         return False

#     def _goodbye(self) -> None:
#         self.io.speak(
#             "Merci pour cette session de formation. "
#             "J'espère que ce scénario vous a été utile. "
#             "À très bientôt."
#         )
#         print("\nAu revoir !\n")

#     # ------------------------------------------------------------------
#     # Configuration du modèle de langage
#     # ------------------------------------------------------------------

#     def _setup_llm(self):
#         try:
#             from vr_scenario_lib.config import build_llm_config
#             return build_llm_config()
#         except Exception as exc:
#             logger.warning(
#                 "Configuration du modèle indisponible : %s — mode dégradé (scénarios statiques)",
#                 exc,
#             )
#             return None


# # ============================================================================
# # Interface en ligne de commande
# # ============================================================================

# def _parse_args() -> argparse.Namespace:
#     p = argparse.ArgumentParser(
#         description=(
#             "Application vocale de supervision de scénarios de formation en réalité virtuelle"
#         ),
#         formatter_class=argparse.ArgumentDefaultsHelpFormatter,
#     )
#     p.add_argument(
#         "--stt-backend", default="whisper", choices=["whisper", "google"],
#         help="Moteur de reconnaissance vocale.",
#     )
#     p.add_argument(
#         "--tts-backend", default=TTS_DEFAULT_BACKEND,
#         choices=["coqui", "piper", "gtts", "pyttsx3"],
#         help=(
#             "Moteur de synthèse vocale. "
#             "Les options 'coqui' et 'piper' fonctionnent entièrement hors ligne."
#         ),
#     )
#     p.add_argument(
#         "--language", default="fr",
#         help="Code de langue au format ISO 639-1 (fr par défaut).",
#     )
#     p.add_argument(
#         "--whisper-model", default=WHISPER_DEFAULT_MODEL,
#         choices=["tiny", "base", "small", "medium", "large"],
#         help="Taille du modèle Whisper. L'option 'small' est recommandée pour le français.",
#     )
#     p.add_argument(
#         "--coqui-model", default=COQUI_MODEL_FR,
#         help="Identifiant du modèle Coqui.",
#     )
#     p.add_argument(
#         "--piper-model", default=PIPER_MODEL_FR,
#         help="Nom du modèle Piper (exemple : fr_FR-tom-medium).",
#     )
#     p.add_argument(
#         "--debug", action="store_true",
#         help="Active les journaux de débogage complets.",
#     )
#     return p.parse_args()


# def main() -> None:
#     args = _parse_args()
#     if args.debug:
#         logging.getLogger().setLevel(logging.DEBUG)

#     io = VoiceIO(
#         stt_backend   = args.stt_backend,
#         tts_backend   = args.tts_backend,
#         language      = args.language,
#         whisper_model = args.whisper_model,
#         coqui_model   = args.coqui_model,
#         piper_model   = args.piper_model,
#     )
#     app = VRScenarioApp(io)
#     try:
#         app.run()
#     except KeyboardInterrupt:
#         print("\nSession interrompue par l'utilisateur.")
#     finally:
#         io.close()


# if __name__ == "__main__":
#     main()



# """
# Application vocale de supervision de scénarios de formation en réalité virtuelle.
# Version entreprise — standards industriels.

# RÔLE DE L'APPLICATION
# ----------------------
# L'utilisateur décrit librement un scénario de réalité virtuelle à voix haute.
# L'application écoute en continu, transcrit par fragments avec détection de voix,
# et soumet chaque fragment à un superviseur linguistique qui peut :
#   - CONTINUER  : rester silencieux (écoute neutre)
#   - CONSEIL    : intervenir poliment pour formuler un conseil
#   - STOP       : interrompre fermement pour signaler une erreur critique

# Architecture
# ------------
# VoiceIO          : reconnaissance vocale (Faster Whisper + VAD SpeechRecognition) + synthèse vocale française native.
# SupervisorLLM    : analyse chaque fragment, décide CONTINUER / CONSEIL / STOP.
# NarratorSession  : accumule la transcription, maintient le contexte du scénario.
# VRScenarioApp    : orchestration métier (initialisation + boucle de narration supervisée).
# PatienceManager  : retour sonore pendant les temps de traitement (signaux d'ambiance + phrases de transition).

# Moteurs de synthèse vocale française (ordre de priorité automatique)
# --------------------------------------------------------------------
# 1. coqui   -- Coqui VITS tts_models/fr/mai/tacotron2-DDC : voix neurale hors ligne, haute qualité
# 2. piper   -- Piper fr_FR-tom-medium                      : voix neurale hors ligne, très rapide
# 3. gtts    -- Google Synthèse vocale                      : voix en ligne, qualité maximale
# 4. pyttsx3 -- espeak-fr                                   : synthèse de base, sans dépendances

# Usage :
#     python app_vocal.py                            # détection automatique du meilleur moteur disponible
#     python app_vocal.py --tts-backend coqui        # Coqui VITS (hors ligne, haute qualité)
#     python app_vocal.py --tts-backend piper        # Piper (hors ligne, très rapide)
#     python app_vocal.py --tts-backend gtts         # Google Synthèse vocale (en ligne)
#     python app_vocal.py --stt-backend google       # Google Reconnaissance vocale (en ligne)
#     python app_vocal.py --whisper-model small      # meilleure précision de reconnaissance
#     python app_vocal.py --debug                    # journaux de débogage complets
# """

# from __future__ import annotations

# import argparse
# import json
# import logging
# import math
# import os
# import random
# import struct
# import sys
# import tempfile
# import threading
# import time
# import uuid
# from dataclasses import dataclass, field
# from datetime import datetime, timezone
# from enum import Enum
# from typing import Any, Dict, List, Optional

# # ---------------------------------------------------------------------------
# # Journalisation
# # ---------------------------------------------------------------------------
# logging.basicConfig(
#     level=logging.INFO,
#     format="%(asctime)s | %(name)-36s | %(levelname)-8s | %(message)s",
#     datefmt="%H:%M:%S",
# )
# logger = logging.getLogger(__name__)

# sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# # ============================================================================
# # Constantes
# # ============================================================================

# STT_LISTEN_TIMEOUT    = 8
# STT_PHRASE_TIME_LIMIT = 20          # durée maximale d'un fragment de narration
# STT_SILENCE_TIMEOUT   = 2.0         # silence détecté → fin du fragment
# STT_AMBIENT_DURATION  = 0.5
# TTS_TO_STT_SETTLE_S   = 0.3         # pause après la synthèse vocale, avant calibration du micro
#                                      # (laisse l'écho de la synthèse se dissiper — sinon les
#                                      # réponses courtes comme "oui" sont mal captées)
# TTS_SPEECH_RATE       = 145
# TTS_VOLUME            = 0.92
# WHISPER_DEFAULT_MODEL = "base"
# WHISPER_BEAM_SIZE     = 5

# # Biais lexical Whisper pour la capture du thème : un thème prononcé est un
# # fragment de 2 à 4 mots SANS contexte (contrairement aux questions en Q&R,
# # plus longues, où le modèle peut s'appuyer sur la phrase pour se corriger).
# # initial_prompt oriente la transcription vers le vocabulaire attendu —
# # technique standard pour fiabiliser la reconnaissance de termes techniques courts.
# WHISPER_TOPIC_PROMPT = (
#     "Thèmes de formation en réalité virtuelle industrielle : consignation gaz, "
#     "consignation électrique, sécurité incendie, premiers secours, travail en hauteur, "
#     "espace confiné, risque chimique, manutention, procédures de sécurité."
# )

# # Mots déclencheurs de fin de session
# # Rédigés pour être naturels à l'oral et fiables à la transcription
# EXIT_WORDS = {"quitter", "terminer", "au revoir", "fin", "arrêter", "c'est tout"}

# # Capture du thème — confirmation orale obligatoire (limite les scénarios générés
# # sur un thème mal compris par la reconnaissance vocale)
# TOPIC_MAX_ATTEMPTS         = 3
# TOPIC_CONFIRM_MAX_ATTEMPTS = 2   # un "oui"/"non" isolé est plus dur à transcrire qu'une phrase :
#                                   # on retente la question de confirmation seule avant d'abandonner
# TOPIC_CONFIRM_YES  = {"oui", "ouais", "yes", "exact", "correct", "c'est ça", "d'accord", "affirmatif"}
# TOPIC_CONFIRM_NO   = {"non", "no", "faux", "incorrect", "pas ça", "négatif"}


# # Moteurs de synthèse vocale française native
# TTS_DEFAULT_BACKEND   = "coqui"
# TTS_FALLBACK_CHAIN    = ["coqui", "piper", "gtts", "pyttsx3"]

# # Coqui : voix féminine Maï, accent français métropolitain soigné
# COQUI_MODEL_FR    = "tts_models/fr/mai/tacotron2-DDC"
# COQUI_SAMPLE_RATE = 22050

# # Piper : voix masculine Tom, accent français métropolitain naturel
# PIPER_MODEL_FR    = "fr_FR-tom-medium"
# PIPER_SAMPLE_RATE = 22050

# # Superviseur — instructions système
# SUPERVISOR_MAX_TOKENS = 256
# SUPERVISOR_SYSTEM = (
#     "Tu es un superviseur expert en sécurité de la réalité virtuelle et en procédures industrielles. "
#     "L'utilisateur décrit à voix haute un scénario de formation en réalité virtuelle. "
#     "Tu reçois des fragments de sa narration en temps réel.\n\n"
#     "Analyse le dernier fragment dans son contexte et réponds UNIQUEMENT avec un objet JSON :\n"
#     '{"decision": "CONTINUER" | "CONSEIL" | "STOP", "message": "<texte à dire, vide si CONTINUER>"}\n\n'
#     "Règles strictes :\n"
#     "- CONTINUER  : narration correcte, cohérente, sans danger. Message vide obligatoire.\n"
#     "- CONSEIL    : amélioration possible. Message court, positif, concret. Deux phrases maximum.\n"
#     "- STOP       : erreur critique de procédure, danger réel, incohérence grave. "
#     "Message direct et précis. Commence par 'Attention : '.\n"
#     "Ne jamais inventer de contexte non mentionné. Rester factuel."
# )

# # Génération de scénario — instructions système
# SCENARIO_GEN_MAX_TOKENS = 1024
# SCENARIO_GEN_SYSTEM = (
#     "Tu es un expert en conception de scénarios de formation en réalité virtuelle industrielle. "
#     "À partir d'un thème, génère un scénario structuré en JSON uniquement, sans aucun texte avant ou après.\n\n"
#     "Format JSON attendu (respecte exactement ces clés) :\n"
#     '{\n'
#     '  "titre": "Titre court du scénario",\n'
#     '  "objectifs": ["objectif 1", "objectif 2", "objectif 3"],\n'
#     '  "grandes_lignes": [\n'
#     '    {"etape": 1, "titre": "Titre de l\'étape", "description": "Description concise"},\n'
#     '    ...\n'
#     '  ],\n'
#     '  "procedures_cles": ["procédure 1", "procédure 2"],\n'
#     '  "points_vigilance": ["point 1", "point 2"],\n'
#     '  "resume_oral": "Texte fluide de trois à quatre phrases pour lecture vocale. Pas de listes, pas de symboles."\n'
#     '}\n\n'
#     "Le champ resume_oral doit être lisible à voix haute sans aucun accroc : pas de tirets, "
#     "pas de parenthèses, pas d'abréviations, pas de sigles. Quatre phrases au maximum."
# )

# # Questions-réponses — instructions système
# QA_MAX_TOKENS    = 180          # réduit : force la concision dès la génération
# QA_MAX_SENTENCES = 2            # filet de sécurité appliqué après coup (cf. _enforce_max_sentences)
# QA_SYSTEM = (
#     "Tu es un formateur expert qui aide un apprenant à comprendre un scénario de formation en réalité virtuelle. "
#     "Tu réponds aux questions en t'appuyant exclusivement sur le scénario fourni. "
#     "Réponse impérativement courte : une phrase si possible, deux phrases maximum. "
#     "Va droit à l'information utile. "
#     "Pas de listes, pas de tirets, pas de symboles, aucun mot ou formule de remplissage "
#     "(par exemple : en fait, donc, voilà, eh bien, du coup, en gros, extra). "
#     "Parle directement à l'apprenant, avec chaleur et précision."
# )

# # Appel au modèle de langage — robustesse réseau (standard industriel : retry + backoff)
# LLM_CALL_MAX_RETRIES     = 2     # tentatives supplémentaires après l'essai initial
# LLM_CALL_RETRY_BACKOFF_S = 1.5   # délai de base entre tentatives (croissance linéaire)

# # Locutions de remplissage à éliminer des réponses orales (filet de sécurité post-génération)
# FILLER_PATTERNS_FR = [
#     r"\ben fait\b,?\s*",
#     r"\bdonc\b,?\s*",
#     r"\bvoil[aà]\b,?\s*",
#     r"\beh bien\b,?\s*",
#     r"\bdu coup\b,?\s*",
#     r"\ben gros\b,?\s*",
#     r"\ben quelque sorte\b,?\s*",
#     r"\bpour ainsi dire\b,?\s*",
#     r"\b[aà] vrai dire\b,?\s*",
#     r"\bdisons que\b,?\s*",
#     r"\bil faut savoir que\b,?\s*",
#     r"\bextra\b\s*[!.,]?\s*",
#     r"^\s*alors,?\s*",
# ]


# # ============================================================================
# # Bibliothèque de phrases système
# # ----------------------------------------------------------------------------
# # Chaque entrée regroupe plusieurs formulations d'une même situation récurrente.
# # La fonction pick() tire une variante aléatoire à chaque appel, ce qui réduit
# # sensiblement la fatigue auditive lors de longues sessions.
# #
# # Principes de rédaction appliqués :
# #   - Phrases courtes, musicalité naturelle, rythme parlé
# #   - Pas de sigles ni d'anglicismes difficiles à prononcer
# #   - Pas de virgules superflues (pause TTS mal placée)
# #   - Finales ouvertes ou légèrement montantes (intonation invitante)
# #   - Chaleur professionnelle — ni trop formel ni trop familier
# # ============================================================================

# CACHED_PHRASES_FR: Dict[str, List[str]] = {

#     # Invitation à parler — brève, neutre, non répétitive
#     "listening": [
#         "Je vous écoute.",
#         "À vous.",
#         "Allez-y.",
#         "Je suis prêt.",
#         "La parole est à vous.",
#     ],

#     # Accusé de réception très court
#     "ack_short": [
#         "Bien reçu.",
#         "Compris.",
#         "Noté.",
#         "Entendu.",
#     ],

#     # Attente courte (1 à 3 secondes) — rien de verbal, juste un signal d'ambiance
#     # Ces phrases ne sont pas utilisées directement : le niveau 1 est traité
#     # uniquement par earcon, sans parole, pour ne pas alourdir les courtes attentes.
#     "thinking_short": [
#         "Un instant.",
#         "Je vérifie.",
#     ],

#     # Attente moyenne (3 à 10 secondes) — une phrase rassurante, pas d'explication
#     "thinking_medium": [
#         "Je prépare votre réponse.",
#         "Je consulte le scénario.",
#         "Je rassemble les éléments.",
#         "Je cherche la bonne information.",
#         "Je réfléchis à votre question.",
#     ],

#     # Attente longue (10 à 20 secondes) — on reconnaît que ça prend du temps
#     "thinking_long": [
#         "La question est détaillée, je finalise ma réponse.",
#         "Cela demande un peu plus de réflexion. Je suis sur le sujet.",
#         "Je creuse la question. Encore un court instant.",
#         "Je vérifie tous les éléments. Merci de votre patience.",
#     ],

#     # Attente très longue (au-delà de 20 secondes) — ton calme, pas d'alarme
#     "thinking_very_long": [
#         "Je suis toujours en train de traiter votre demande.",
#         "Le traitement prend un peu plus de temps que prévu. Je reste sur le sujet.",
#         "Toujours en cours. Je reviens vers vous très bientôt.",
#     ],

#     # Relance douce après un premier silence — sans interroger explicitement
#     "soft_nudge": [
#         "Je reste disponible si vous avez une question.",
#         "Prenez votre temps. Je vous écoute quand vous êtes prêt.",
#         "Pas de précipitation. Je suis là.",
#         "Vous pouvez continuer quand vous le souhaitez.",
#     ],

#     # Question explicite après un silence prolongé (oui / non)
#     "no_response_continue_check": [
#         "Je n'entends plus rien. Souhaitez-vous continuer la session ? "
#         "Dites oui pour continuer, ou non pour terminer.",
#         "Il y a un long silence. Voulez-vous poursuivre ? "
#         "Répondez oui ou non.",
#     ],
# }


# def pick(key: str) -> str:
#     """Tire aléatoirement une variante de phrase système pour réduire la répétition."""
#     options = CACHED_PHRASES_FR.get(key)
#     if not options:
#         return ""
#     return random.choice(options)


# # ============================================================================
# # Décision + NarratorSession
# # ============================================================================

# class Decision(Enum):
#     CONTINUER = "CONTINUER"
#     CONSEIL   = "CONSEIL"
#     STOP      = "STOP"


# @dataclass
# class SupervisorDecision:
#     decision: Decision = Decision.CONTINUER
#     message:  str      = ""

#     def must_speak(self) -> bool:
#         return self.decision in (Decision.CONSEIL, Decision.STOP)


# @dataclass
# class NarratorSession:
#     """Accumule la transcription et maintient le contexte pour le superviseur."""
#     topic:     str
#     chunks:    List[str] = field(default_factory=list)
#     full_text: str       = ""

#     def add_chunk(self, text: str) -> None:
#         self.chunks.append(text)
#         self.full_text = " ".join(self.chunks)

#     def context_window(self, n: int = 5) -> str:
#         return " ".join(self.chunks[-n:])

#     def summary(self) -> str:
#         return "%d séquence(s), environ %d mots" % (len(self.chunks), len(self.full_text.split()))


# # ============================================================================
# # PatienceManager — retour sonore pendant les temps de traitement
# # ----------------------------------------------------------------------------
# # Stratégie à paliers calibrée sur la durée d'attente réelle :
# #
# #   Moins de 1 s    : rien (imperceptible)
# #   De 1 à 3 s      : signal d'ambiance discret seul (pas de phrase —
# #                     évite la surcharge verbale sur les attentes courantes)
# #   De 3 à 10 s     : signal d'ambiance + courte phrase de transition
# #   Au-delà de 10 s : signal grave + phrase "longue attente", puis rappel
# #                     toutes les 12 s pour éviter le silence total anxiogène
# #
# # Le suivi tourne dans un fil d'exécution dédié pendant l'appel bloquant
# # au modèle de langage. Il s'arrête proprement (threading.Event) dès que
# # le résultat est disponible.
# # ============================================================================

# class PatienceManager:
#     """Pilote les signaux d'ambiance et les phrases de patience selon la durée réelle d'attente."""

#     LEVEL_SHORT_S     = 1.0    # moins de 1 s : rien
#     LEVEL_MEDIUM_S    = 3.0    # 1 à 3 s : signal seul
#     LEVEL_LONG_S      = 10.0   # 3 à 10 s : signal + phrase courte
#     LEVEL_VERY_LONG_S = 20.0   # au-delà de 10 s : signal grave + phrase longue

#     def __init__(self, io: "VoiceIO") -> None:
#         self.io = io
#         self._stop_event = threading.Event()
#         self._thread: Optional[threading.Thread] = None

#     def start(self) -> None:
#         self._stop_event.clear()
#         self._thread = threading.Thread(target=self._run, daemon=True)
#         self._thread.start()

#     def stop(self) -> None:
#         self._stop_event.set()
#         if self._thread is not None:
#             self._thread.join(timeout=2.0)
#             self._thread = None

#     def _run(self) -> None:
#         start = time.monotonic()
#         announced_medium    = False
#         announced_long      = False
#         announced_very_long = False

#         while not self._stop_event.is_set():
#             elapsed = time.monotonic() - start

#             if elapsed >= self.LEVEL_MEDIUM_S and not announced_medium:
#                 announced_medium = True
#                 self.io.play_earcon("patience_short")

#             if elapsed >= self.LEVEL_LONG_S and not announced_long:
#                 announced_long = True
#                 self.io.play_earcon("patience_medium")
#                 self.io.speak(pick("thinking_medium"), blocking=False)

#             if elapsed >= self.LEVEL_VERY_LONG_S and not announced_very_long:
#                 announced_very_long = True
#                 self.io.play_earcon("patience_long")
#                 self.io.speak(pick("thinking_long"), blocking=False)

#             # Rappel périodique au-delà du seuil très long
#             if announced_very_long and elapsed >= self.LEVEL_VERY_LONG_S + 12.0:
#                 self.io.speak(pick("thinking_very_long"), blocking=False)
#                 start -= 12.0  # reprogramme le prochain rappel dans 12 s

#             self._stop_event.wait(timeout=0.25)

#     def run_with_patience(self, fn, *args, **kwargs):
#         """Exécute fn(*args, **kwargs) en pilotant le retour sonore de patience."""
#         self.start()
#         try:
#             return fn(*args, **kwargs)
#         finally:
#             self.stop()


# # ============================================================================
# # SupervisorLLM
# # ============================================================================

# class SupervisorLLM:
#     """Analyse les fragments de narration et produit des décisions de supervision."""

#     def __init__(self, config) -> None:
#         self._config = config
#         self._lock   = threading.Lock()

#     def analyse(self, session: NarratorSession, new_chunk: str) -> SupervisorDecision:
#         if self._config is None:
#             return SupervisorDecision()

#         user_msg = (
#             "Thème du scénario : %s\n\n"
#             "Contexte (narration précédente) :\n%s\n\n"
#             "Nouveau fragment :\n%s"
#         ) % (session.topic, session.context_window(), new_chunk)

#         try:
#             with self._lock:
#                 raw = self._call_llm(user_msg)
#             return self._parse(raw)
#         except Exception as exc:
#             logger.warning("SupervisorLLM erreur : %s", exc)
#             return SupervisorDecision()

#     def _call_llm(self, user_msg: str) -> str:
#         # Tentative via la bibliothèque de scénarios
#         try:
#             from vr_scenario_lib.llm import call_llm
#             return call_llm(
#                 system=SUPERVISOR_SYSTEM,
#                 user=user_msg,
#                 llm_config=self._config,
#                 max_tokens=SUPERVISOR_MAX_TOKENS,
#             )
#         except ImportError:
#             pass

#         # Appel direct compatible avec l'interface de l'API de langage
#         import json
#         import urllib.request

#         payload = json.dumps({
#             "model":      getattr(self._config, "model", "gpt-3.5-turbo"),
#             "max_tokens": SUPERVISOR_MAX_TOKENS,
#             "messages":   [
#                 {"role": "system", "content": SUPERVISOR_SYSTEM},
#                 {"role": "user",   "content": user_msg},
#             ],
#         }).encode()
#         api_url = getattr(self._config, "api_url", "https://api.openai.com/v1/chat/completions")
#         token   = getattr(self._config, "token", "")
#         req = urllib.request.Request(
#             api_url,
#             data=payload,
#             headers={
#                 "Content-Type":  "application/json",
#                 "Authorization": "Bearer " + token,
#             },
#         )
#         with urllib.request.urlopen(req, timeout=15) as resp:
#             data = json.loads(resp.read())
#         return data["choices"][0]["message"]["content"]

#     def _parse(self, raw: str) -> SupervisorDecision:
#         import json
#         import re
#         m = re.search(r'\{.*\}', raw, re.DOTALL)
#         if not m:
#             logger.warning("SupervisorLLM : structure JSON introuvable dans '%s'", raw[:120])
#             return SupervisorDecision()
#         obj = json.loads(m.group())
#         try:
#             dec = Decision(obj.get("decision", "CONTINUER").upper())
#         except ValueError:
#             dec = Decision.CONTINUER
#         return SupervisorDecision(decision=dec, message=obj.get("message", "").strip())


# # ============================================================================
# # VoiceIO
# # ============================================================================

# class VoiceIO:
#     """Couche basse — reconnaissance vocale et synthèse vocale.

#     Principes fondamentaux
#     ----------------------
#     1. speak() est TOUJOURS bloquant dans le fil principal.
#        Une synthèse non bloquante avant écoute = écho capturé par le moteur de
#        reconnaissance.
#     2. Le microphone n'est jamais ouvert pendant la synthèse vocale.
#     3. L'enregistrement utilise la détection automatique de voix, pas une durée fixe.
#     4. interrupt_and_speak() coupe l'audio en cours avant de parler (alertes STOP).
#     5. play_earcon() est toujours non bloquant et très court (moins de 400 ms) :
#        il ne doit jamais retarder le flux conversationnel.
#     """

#     def __init__(
#         self,
#         stt_backend:   str = "whisper",
#         tts_backend:   str = TTS_DEFAULT_BACKEND,
#         language:      str = "fr",
#         whisper_model: str = WHISPER_DEFAULT_MODEL,
#         coqui_model:   str = COQUI_MODEL_FR,
#         piper_model:   str = PIPER_MODEL_FR,
#     ) -> None:
#         self.stt_backend      = stt_backend
#         self.tts_backend      = tts_backend
#         self.language         = language
#         self.whisper_model_id = whisper_model
#         self.coqui_model_id   = coqui_model
#         self.piper_model_id   = piper_model

#         self._recognizer    = None
#         self._whisper_model = None
#         self._tts_engine    = None
#         self._coqui_model   = None
#         self._lock_tts      = threading.Lock()

#         self._init()

#     # ------------------------------------------------------------------
#     # Initialisation
#     # ------------------------------------------------------------------

#     def _init(self) -> None:
#         self._init_stt()
#         self._init_tts()
#         logger.info(
#             "VoiceIO prêt — Reconnaissance : %s | Synthèse : %s | Langue : %s",
#             self.stt_backend, self.tts_backend, self.language,
#         )

#     def _init_stt(self) -> None:
#         try:
#             import speech_recognition as sr
#             self._recognizer = sr.Recognizer()
#             self._recognizer.energy_threshold         = 4000
#             self._recognizer.pause_threshold          = STT_SILENCE_TIMEOUT
#             self._recognizer.dynamic_energy_threshold = True
#         except ImportError:
#             raise RuntimeError(
#                 "Module SpeechRecognition manquant. "
#                 "Installez-le avec : pip install SpeechRecognition PyAudio"
#             )
#         if self.stt_backend == "whisper":
#             self._whisper_model = self._load_whisper()

#     def _load_whisper(self) -> object:
#         try:
#             from faster_whisper import WhisperModel
#             logger.info("Chargement du modèle Faster Whisper '%s'...", self.whisper_model_id)
#             model = WhisperModel(
#                 self.whisper_model_id,
#                 device="cpu",
#                 compute_type="int8",
#             )
#             logger.info("Faster Whisper prêt")
#             return model
#         except ImportError:
#             raise RuntimeError(
#                 "Module faster-whisper manquant. Installez-le avec : pip install faster-whisper"
#             )

#     def _init_tts(self) -> None:
#         chain = (
#             [self.tts_backend]
#             + [b for b in TTS_FALLBACK_CHAIN if b != self.tts_backend]
#         )
#         for backend in chain:
#             try:
#                 if backend == "coqui":
#                     self._init_coqui()
#                 elif backend == "piper":
#                     self._init_piper()
#                 elif backend == "gtts":
#                     self._init_gtts()
#                 elif backend == "pyttsx3":
#                     self._init_pyttsx3()
#                 else:
#                     continue
#                 self.tts_backend = backend
#                 logger.info("Moteur de synthèse actif : %s", backend)
#                 return
#             except Exception as exc:
#                 logger.warning(
#                     "Moteur '%s' indisponible : %s — essai du suivant", backend, exc
#                 )

#         raise RuntimeError(
#             "Aucun moteur de synthèse vocale disponible. "
#             "Installez au minimum : pip install coqui-tts sounddevice soundfile"
#         )

#     # ------------------------------------------------------------------
#     # Initialisation Coqui VITS — voix neurale française hors ligne
#     # ------------------------------------------------------------------

#     def _init_coqui(self) -> None:
#         try:
#             from TTS.api import TTS as CoquiTTS
#             import sounddevice  # noqa: F401
#             import soundfile    # noqa: F401
#         except ImportError:
#             raise RuntimeError(
#                 "Module Coqui manquant. Installez-le avec : pip install coqui-tts sounddevice soundfile"
#             )
#         logger.info("Chargement de Coqui '%s'...", self.coqui_model_id)
#         self._coqui_model = CoquiTTS(
#             model_name=self.coqui_model_id,
#             progress_bar=False,
#             gpu=False,
#         )
#         logger.info("Coqui prêt")

#     # ------------------------------------------------------------------
#     # Initialisation Piper — voix neurale française hors ligne, très rapide
#     # ------------------------------------------------------------------

#     def _init_piper(self) -> None:
#         try:
#             import piper  # noqa: F401
#         except ImportError:
#             raise RuntimeError("Module piper-tts manquant. Installez-le avec : pip install piper-tts")
#         logger.info("Piper disponible — modèle '%s'", self.piper_model_id)

#     # ------------------------------------------------------------------
#     # Initialisation Google Synthèse vocale — en ligne
#     # ------------------------------------------------------------------

#     def _init_gtts(self) -> None:
#         try:
#             import gtts    # noqa: F401
#             import pygame  # noqa: F401
#         except ImportError:
#             raise RuntimeError(
#                 "Modules gTTS ou pygame manquants. Installez-les avec : pip install gTTS pygame"
#             )
#         logger.info("Google Synthèse vocale initialisée")

#     # ------------------------------------------------------------------
#     # Initialisation pyttsx3 — solution de secours ultime
#     # ------------------------------------------------------------------

#     def _init_pyttsx3(self) -> None:
#         try:
#             import pyttsx3
#         except ImportError:
#             raise RuntimeError(
#                 "Module pyttsx3 manquant. Installez-le avec : pip install pyttsx3"
#             )

#         engine = pyttsx3.init()
#         engine.setProperty("rate",   TTS_SPEECH_RATE)
#         engine.setProperty("volume", TTS_VOLUME)

#         fr_voice_found = False
#         # Priorité 1 : voix fr_FR espeak-ng (accent français métropolitain)
#         # Priorité 2 : toute voix contenant "french" ou "fr" dans le nom ou l'identifiant
#         for priority in ("fr_FR", "fr-FR", "french", "fr"):
#             for v in engine.getProperty("voices"):
#                 name_lower = v.name.lower()
#                 id_lower   = v.id.lower()
#                 if priority.lower() in id_lower or priority.lower() in name_lower:
#                     engine.setProperty("voice", v.id)
#                     logger.info(
#                         "pyttsx3 : voix française sélectionnée : %s (%s)", v.name, v.id
#                     )
#                     fr_voice_found = True
#                     break
#             if fr_voice_found:
#                 break

#         if not fr_voice_found:
#             logger.warning(
#                 "Aucune voix française trouvée dans pyttsx3. "
#                 "Sur Linux : sudo apt install espeak-ng-data"
#             )

#         self._tts_engine = engine
#         logger.info("pyttsx3 initialisé (voix système)")

#     # ------------------------------------------------------------------
#     # Synthèse vocale — TOUJOURS bloquante dans le fil principal
#     # ------------------------------------------------------------------

#     def interrupt_and_speak(self, text: str) -> None:
#         """Coupe l'audio en cours PUIS parle. Réservé aux alertes STOP urgentes."""
#         self._stop_audio()
#         self.speak(text)

#     def _stop_audio(self) -> None:
#         """Arrête immédiatement la lecture audio (tous moteurs)."""
#         try:
#             if self.tts_backend in ("coqui", "piper"):
#                 import sounddevice as sd
#                 sd.stop()
#             elif self.tts_backend == "gtts":
#                 try:
#                     import pygame
#                     if pygame.mixer.get_init():
#                         pygame.mixer.music.stop()
#                 except Exception:
#                     pass
#         except Exception as exc:
#             logger.debug("_stop_audio : %s", exc)

#     @staticmethod
#     def _sanitize_tts(text: str) -> str:
#         """Nettoie le texte avant synthèse vocale.

#         Transformations appliquées dans l'ordre :
#         1. Blocs de code Markdown (``` … ```) → supprimés
#         2. Emphase Markdown (* ** _ __ ~ ~~)  → supprimée (le texte reste)
#         3. Titres Markdown (# ## ###…)         → supprimés (le texte reste)
#         4. Adresses web (http / https / ftp)   → remplacées par « lien »
#         5. Ponctuation non orale               → remplacée ou supprimée
#         6. Espaces multiples et lignes vides   → normalisés
#         """
#         import re

#         # 1. Blocs de code (``` … ```) et code en ligne (` … `)
#         text = re.sub(r'```.*?```', '', text, flags=re.DOTALL)
#         text = re.sub(r'`[^`]*`', '', text)

#         # 2. Emphase Markdown
#         text = re.sub(r'\*{1,3}|_{1,3}|~{1,2}', '', text)

#         # 3. Titres Markdown en début de ligne
#         text = re.sub(r'^\s*#{1,6}\s*', '', text, flags=re.MULTILINE)

#         # 4. Adresses web
#         text = re.sub(r'https?://\S+|ftp://\S+', 'lien', text)

#         # 5. Ponctuation non orale
#         text = re.sub(r'^\s*[-•–—]\s+', '', text, flags=re.MULTILINE)
#         text = re.sub(r'^\s*[\-|: ]{3,}\s*$', '', text, flags=re.MULTILINE)
#         text = re.sub(r'\|', ' ', text)
#         text = re.sub(r'[\\/@#$%^&{}\[\]<>=]', ' ', text)
#         text = re.sub(r'[(){}\[\]]', ' ', text)
#         text = re.sub(r'\.{2,}', ',', text)
#         text = re.sub(r'\s*[–—]\s*', ', ', text)
#         text = re.sub(r'\*+', '', text)
#         text = re.sub(r'_+', ' ', text)

#         # 6. Normalisation des espaces et des sauts de ligne
#         text = re.sub(r'\n+', ' ', text)
#         text = re.sub(r' {2,}', ' ', text)

#         return text.strip()

#     def speak(self, text: str, *, blocking: bool = True) -> None:
#         """Synthèse vocale en français natif.

#         blocking=True (par défaut) : retourne APRÈS la fin de la lecture.
#         blocking=False             : usage exceptionnel uniquement —
#                                      par exemple, phrases de patience émises
#                                      par PatienceManager pendant qu'un autre fil
#                                      attend le modèle de langage. Dans ce cas,
#                                      le microphone n'est pas sollicité en parallèle,
#                                      donc pas de risque d'écho capturé.
#         RÈGLE : ne JAMAIS appeler avec blocking=False juste avant écoute().
#         """
#         if not text or not text.strip():
#             return
#         text = self._sanitize_tts(text)
#         if not text:
#             return
#         logger.info("Synthèse [%s] : '%s'", self.tts_backend, text[:80])

#         dispatch = {
#             "coqui":   self._speak_coqui,
#             "piper":   self._speak_piper,
#             "gtts":    self._speak_gtts,
#             "pyttsx3": self._speak_pyttsx3,
#         }
#         fn = dispatch.get(self.tts_backend)
#         if fn is None:
#             logger.error("Moteur de synthèse inconnu : %s", self.tts_backend)
#             print("[Synthèse] " + text)
#             return
#         fn(text, blocking)

#     # ------------------------------------------------------------------
#     # Signaux d'ambiance — retour sonore court pendant les attentes
#     # ------------------------------------------------------------------
#     # Générés à la volée (sinusoïdes), aucune dépendance audio externe
#     # supplémentaire au-delà de sounddevice (déjà requis par coqui/piper).
#     # En cas d'indisponibilité : dégradation silencieuse, sans exception
#     # propagée ni affichage parasite — un signal manqué ne doit jamais
#     # bloquer le flux conversationnel.
#     # ------------------------------------------------------------------

#     _EARCON_PROFILES = {
#         # (fréquence Hz, durée s, amplitude) — profils courts et discrets
#         "patience_short":  (880.0, 0.10, 0.15),   # signal discret, attente courte
#         "patience_medium": (660.0, 0.15, 0.18),   # signal intermédiaire
#         "patience_long":   (440.0, 0.22, 0.20),   # signal grave, longue attente
#     }

#     def play_earcon(self, profile: str) -> None:
#         """Joue un signal d'ambiance court et non bloquant. Échec silencieux."""
#         params = self._EARCON_PROFILES.get(profile)
#         if params is None:
#             return
#         try:
#             threading.Thread(
#                 target=self._play_earcon_sync, args=(params,), daemon=True
#             ).start()
#         except Exception as exc:
#             logger.debug("play_earcon : %s", exc)

#     def _play_earcon_sync(self, params) -> None:
#         freq, duration, amplitude = params
#         try:
#             import sounddevice as sd
#             sample_rate = 22050
#             n_samples = int(sample_rate * duration)
#             tone = [
#                 amplitude * math.sin(2 * math.pi * freq * (i / sample_rate))
#                 for i in range(n_samples)
#             ]
#             sd.play(tone, sample_rate)
#             sd.wait()
#         except Exception as exc:
#             logger.debug("Signal d'ambiance indisponible (%s), ignoré", exc)

#     # ------------------------------------------------------------------
#     # Moteur Coqui — référence qualité
#     # ------------------------------------------------------------------

#     def _speak_coqui(self, text: str, blocking: bool) -> None:
#         tmp_path: Optional[str] = None
#         try:
#             import soundfile as sf
#             import sounddevice as sd

#             with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
#                 tmp_path = f.name

#             with self._lock_tts:
#                 self._coqui_model.tts_to_file(text=text, file_path=tmp_path)

#             data, sr = sf.read(tmp_path, dtype="float32")
#             if blocking:
#                 sd.play(data, sr)
#                 sd.wait()
#             else:
#                 sd.play(data, sr)

#         except Exception as exc:
#             logger.error("Coqui erreur : %s", exc)
#             print("[Synthèse] " + text)
#         finally:
#             if tmp_path and os.path.exists(tmp_path):
#                 try:
#                     os.unlink(tmp_path)
#                 except OSError:
#                     pass

#     # ------------------------------------------------------------------
#     # Moteur Piper — latence minimale
#     # ------------------------------------------------------------------

#     def _speak_piper(self, text: str, blocking: bool) -> None:
#         tmp_path: Optional[str] = None
#         try:
#             import subprocess
#             import soundfile as sf
#             import sounddevice as sd

#             with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
#                 tmp_path = f.name

#             result = subprocess.run(
#                 ["piper", "--model", self.piper_model_id, "--output_file", tmp_path],
#                 input=text.encode("utf-8"),
#                 capture_output=True,
#                 timeout=30,
#             )
#             if result.returncode != 0:
#                 raise RuntimeError(
#                     "piper code de retour=%d : %s" % (
#                         result.returncode, result.stderr.decode()
#                     )
#                 )

#             data, sr = sf.read(tmp_path, dtype="float32")
#             if blocking:
#                 sd.play(data, sr)
#                 sd.wait()
#             else:
#                 sd.play(data, sr)

#         except FileNotFoundError:
#             logger.error("Exécutable 'piper' introuvable. pip install piper-tts")
#             print("[Synthèse] " + text)
#         except Exception as exc:
#             logger.error("Piper erreur : %s", exc)
#             print("[Synthèse] " + text)
#         finally:
#             if tmp_path and os.path.exists(tmp_path):
#                 try:
#                     os.unlink(tmp_path)
#                 except OSError:
#                     pass

#     # ------------------------------------------------------------------
#     # Moteur Google Synthèse vocale — en ligne
#     # ------------------------------------------------------------------

#     def _speak_gtts(self, text: str, blocking: bool) -> None:
#         tmp_path: Optional[str] = None
#         try:
#             from gtts import gTTS
#             import pygame

#             tts = gTTS(text=text, lang=self.language, slow=False)
#             with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
#                 tmp_path = f.name
#             tts.save(tmp_path)

#             # Réinitialisation propre du mixeur à chaque appel
#             if pygame.mixer.get_init():
#                 pygame.mixer.quit()
#             pygame.mixer.init(frequency=22050, size=-16, channels=1, buffer=512)
#             pygame.mixer.music.load(tmp_path)
#             pygame.mixer.music.play()

#             if blocking:
#                 while pygame.mixer.music.get_busy():
#                     time.sleep(0.05)
#                 pygame.mixer.quit()

#         except Exception as exc:
#             logger.error("Google Synthèse vocale erreur : %s", exc)
#             print("[Synthèse] " + text)
#         finally:
#             if tmp_path and os.path.exists(tmp_path):
#                 try:
#                     time.sleep(0.1)
#                     os.unlink(tmp_path)
#                 except OSError:
#                     pass

#     # ------------------------------------------------------------------
#     # Moteur pyttsx3 — solution de secours ultime
#     # ------------------------------------------------------------------

#     def _speak_pyttsx3(self, text: str, blocking: bool) -> None:
#         with self._lock_tts:
#             try:
#                 self._tts_engine.say(text)
#                 if blocking:
#                     self._tts_engine.runAndWait()
#                 else:
#                     t = threading.Thread(
#                         target=self._tts_engine.runAndWait, daemon=True
#                     )
#                     t.start()
#             except Exception as exc:
#                 logger.error("pyttsx3 erreur : %s", exc)
#                 print("[Synthèse] " + text)

#     # ------------------------------------------------------------------
#     # Reconnaissance vocale — fragment avec détection automatique de voix
#     # ------------------------------------------------------------------

#     def listen_chunk(
#         self,
#         *,
#         pause_threshold:   float = STT_SILENCE_TIMEOUT,
#         phrase_time_limit: int   = STT_PHRASE_TIME_LIMIT,
#         listen_timeout:    float = STT_LISTEN_TIMEOUT,
#         initial_prompt:    Optional[str] = None,
#     ) -> str:
#         """Capture un fragment de parole et le transcrit.

#         initial_prompt (Whisper uniquement) : biais lexical optionnel pour
#         orienter la transcription vers un vocabulaire attendu (ex. thèmes
#         techniques courts, sans contexte de phrase). Ignoré sur le moteur Google.

#         Retourne :
#             Le texte transcrit (non vide).

#         Lève :
#             RuntimeError si la capture ou la transcription échoue,
#             ou si aucune voix n'est détectée dans le délai imparti.
#         """
#         import speech_recognition as sr

#         original = self._recognizer.pause_threshold
#         self._recognizer.pause_threshold = pause_threshold
#         tmp_path: Optional[str] = None

#         try:
#             with sr.Microphone() as src:
#                 logger.info(
#                     "Écoute (silence=%.1fs, max=%ds)...",
#                     pause_threshold, phrase_time_limit,
#                 )
#                 self._recognizer.adjust_for_ambient_noise(src, duration=STT_AMBIENT_DURATION)
#                 audio = self._recognizer.listen(
#                     src,
#                     timeout=listen_timeout,
#                     phrase_time_limit=phrase_time_limit,
#                 )

#             with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
#                 tmp_path = f.name
#                 f.write(audio.get_wav_data())

#             if self.stt_backend == "whisper":
#                 return self._transcribe_whisper(tmp_path, initial_prompt=initial_prompt)
#             else:
#                 return self._transcribe_google(audio)

#         except sr.WaitTimeoutError as exc:
#             raise RuntimeError("Aucune voix détectée dans le délai imparti") from exc

#         finally:
#             self._recognizer.pause_threshold = original
#             if tmp_path and os.path.exists(tmp_path):
#                 try:
#                     os.unlink(tmp_path)
#                 except OSError:
#                     pass

#     def listen_short(self, question: str, timeout: float = 8.0, initial_prompt: Optional[str] = None) -> str:
#         """Pose une question brève et attend une réponse courte.
#         Retourne une chaîne vide en cas d'absence de réponse (aucune exception propagée).

#         Utilise les mêmes seuils d'écoute que la boucle de questions-réponses
#         (déjà fiables en usage réel) plutôt que des seuils plus courts : un silence
#         de coupure trop bref clipe une prononciation hésitante (thème technique,
#         mot inhabituel) ou un simple "oui" arrivant juste après la synthèse vocale.

#         initial_prompt : transmis à Whisper pour biaiser la reconnaissance vers
#         un vocabulaire attendu (cf. listen_chunk).
#         """
#         self.speak(question)
#         self.speak(pick("listening"))
#         time.sleep(TTS_TO_STT_SETTLE_S)  # laisse l'écho de la synthèse se dissiper avant calibration du micro
#         try:
#             return self.listen_chunk(
#                 pause_threshold=STT_SILENCE_TIMEOUT,
#                 phrase_time_limit=STT_PHRASE_TIME_LIMIT,
#                 listen_timeout=timeout,
#                 initial_prompt=initial_prompt,
#             )
#         except RuntimeError as exc:
#             logger.info("listen_short : aucune réponse (%s)", exc)
#             return ""

#     def _transcribe_whisper(self, wav_path: str, initial_prompt: Optional[str] = None) -> str:
#         try:
#             segments_gen, info = self._whisper_model.transcribe(
#                 wav_path,
#                 language=self.language,
#                 beam_size=WHISPER_BEAM_SIZE,
#                 initial_prompt=initial_prompt,
#             )
#         except TypeError:
#             # Repli : version de faster-whisper ne supportant pas initial_prompt
#             logger.debug(
#                 "Whisper : 'initial_prompt' non supporté par cette version, "
#                 "repli sans biais lexical"
#             )
#             segments_gen, info = self._whisper_model.transcribe(
#                 wav_path,
#                 language=self.language,
#                 beam_size=WHISPER_BEAM_SIZE,
#             )
#         logger.debug(
#             "Whisper : langue=%s (%.0f%%)",
#             info.language, info.language_probability * 100,
#         )
#         text = " ".join(seg.text.strip() for seg in segments_gen).strip()
#         if not text:
#             raise RuntimeError("La reconnaissance vocale n'a produit aucun texte")
#         logger.info("Fragment reconnu : '%s'", text[:100])
#         return text

#     def _transcribe_google(self, audio) -> str:
#         import speech_recognition as sr
#         lang = "fr-FR" if self.language == "fr" else (self.language + "-" + self.language.upper())
#         try:
#             text = self._recognizer.recognize_google(audio, language=lang)
#             logger.info("Reconnaissance Google : '%s'", text[:100])
#             return text
#         except sr.UnknownValueError:
#             raise RuntimeError("Reconnaissance Google : audio incompréhensible")
#         except sr.RequestError as exc:
#             raise RuntimeError("Reconnaissance Google : erreur de service : %s" % exc)

#     # ------------------------------------------------------------------
#     # Nettoyage
#     # ------------------------------------------------------------------

#     def close(self) -> None:
#         self._stop_audio()
#         if self._tts_engine is not None:
#             try:
#                 with self._lock_tts:
#                     self._tts_engine.stop()
#             except Exception:
#                 pass
#         logger.info("VoiceIO fermé")


# # ============================================================================
# # VRScenarioApp — orchestration principale
# # ============================================================================

# class VRScenarioApp:
#     """
#     Flux en deux phases :

#     PHASE 1 — Génération et présentation du scénario
#       - Saisie vocale du thème
#       - Le modèle de langage génère un scénario structuré
#       - Construction de la session de scénario
#       - Lecture du résumé oral par synthèse vocale

#     PHASE 2 — Questions et réponses supervisées
#       - L'utilisateur pose librement ses questions à voix haute
#       - Le modèle répond en s'appuyant sur le scénario généré
#       - Le superviseur évalue chaque échange : CONTINUER / CONSEIL / STOP
#       - Un mot de sortie clôt proprement la session

#     Gestion de la patience
#     ----------------------
#     Toute attente potentiellement longue (génération de scénario, appel
#     au modèle en questions-réponses) est encadrée par PatienceManager,
#     qui pilote automatiquement les signaux d'ambiance et les phrases de
#     transition selon la durée réelle d'attente.
#     """

#     def __init__(self, io: VoiceIO) -> None:
#         self.io = io
#         self.patience = PatienceManager(io)

#     def run(self) -> None:
#         self._welcome()
#         topic      = self._ask_topic()
#         config     = self._setup_llm()
#         supervisor = SupervisorLLM(config)

#         # -- Phase 1 : génération et présentation -------------------------
#         scenario_session = self._generate_and_announce(topic, config)

#         # -- Phase 2 : questions-réponses supervisées ---------------------
#         self._qa_loop(scenario_session, supervisor, config)

#         self._goodbye()

#     # ------------------------------------------------------------------
#     # Phase 1 : génération du scénario
#     # ------------------------------------------------------------------

#     def _welcome(self) -> None:
#         print("\n" + "=" * 60)
#         print("  APPLICATION VOCALE — SCÉNARIOS DE FORMATION EN RÉALITÉ VIRTUELLE")
#         print("=" * 60)
#         self.io.speak(
#             "Bienvenue dans votre assistant vocal de scénarios de formation. "
#             "Je vais générer un scénario à partir du thème que vous me donnerez, "
#             "vous en présenter les grandes lignes, "
#             "puis répondre à vos questions. "
#             "Dites terminer à tout moment pour clore la session."
#         )

#     def _ask_topic(self) -> str:
#         """Capture le thème par la voix avec confirmation orale explicite.

#         La reconnaissance vocale peut mal comprendre le thème prononcé
#         (homophones, bruit ambiant, accent). Générer un scénario complet sur
#         un thème erroné coûte cher en temps et en confiance utilisateur :
#         on confirme donc systématiquement avant de poursuivre.

#         Stratégie :
#           1. Capture du thème (écoute courte, déjà tolérante au silence).
#           2. Confirmation orale explicite ("Le thème retenu est X, correct ?").
#           3. Nouvelle tentative si infirmé, absent ou ambigu — jusqu'à
#              TOPIC_MAX_ATTEMPTS.
#           4. Repli sur un thème par défaut si aucune confirmation n'est obtenue
#              (dégradation silencieuse : la session continue malgré tout).

#         Toute erreur inattendue de la couche vocale (microphone, moteur STT)
#         est absorbée localement : un échec de capture du thème ne doit jamais
#         interrompre la session.
#         """
#         prompt = (
#             "Sur quel thème souhaitez-vous travailler ? "
#             "Vous pouvez me dire, par exemple : la consignation gaz, "
#             "la sécurité incendie, ou les premiers secours."
#         )
#         for attempt in range(1, TOPIC_MAX_ATTEMPTS + 1):
#             try:
#                 text = self.io.listen_short(prompt, initial_prompt=WHISPER_TOPIC_PROMPT)
#             except Exception as exc:
#                 logger.warning(
#                     "Capture du thème échouée (tentative %d/%d) : %s",
#                     attempt, TOPIC_MAX_ATTEMPTS, exc,
#                 )
#                 text = ""

#             if text and self._confirm_topic(text):
#                 self.io.speak("Très bien. Le thème retenu est : " + text + ".")
#                 logger.info("Thème confirmé : '%s'", text)
#                 print("\nThème : " + text)
#                 return text

#             logger.info(
#                 "Thème non confirmé (tentative %d/%d) : '%s'",
#                 attempt, TOPIC_MAX_ATTEMPTS, text,
#             )
#             if attempt < TOPIC_MAX_ATTEMPTS:
#                 prompt = "Je vous écoute à nouveau. Quel est le thème souhaité ?"
#                 self.io.speak("D'accord, reprenons.")

#         text = "sécurité industrielle"
#         self.io.speak(
#             "Je n'arrive pas à confirmer le thème. "
#             "Je vais utiliser la sécurité industrielle par défaut."
#         )
#         logger.info("Thème : repli par défaut '%s'", text)
#         print("\nThème : " + text)
#         return text

#     def _confirm_topic(self, topic: str) -> bool:
#         """Demande une confirmation orale explicite du thème compris.

#         Un "oui"/"non" isolé est plus difficile à transcrire correctement qu'une
#         phrase complète (peu de contexte pour le modèle de reconnaissance). On
#         retente donc la question de confirmation elle-même, jusqu'à
#         TOPIC_CONFIRM_MAX_ATTEMPTS fois, avant de conclure à une non-confirmation —
#         plutôt que de forcer l'utilisateur à reprononcer tout le thème pour un
#         simple aléa de reconnaissance sur "oui".
#         """
#         question = "Le thème retenu est : " + topic + ". Est-ce correct ? Dites oui ou non."
#         for attempt in range(1, TOPIC_CONFIRM_MAX_ATTEMPTS + 1):
#             try:
#                 answer = self.io.listen_short(question).lower()
#             except Exception as exc:
#                 logger.debug(
#                     "_confirm_topic (tentative %d/%d) : %s",
#                     attempt, TOPIC_CONFIRM_MAX_ATTEMPTS, exc,
#                 )
#                 answer = ""

#             if any(w in answer for w in TOPIC_CONFIRM_NO):
#                 return False
#             if any(w in answer for w in TOPIC_CONFIRM_YES):
#                 return True

#             if attempt < TOPIC_CONFIRM_MAX_ATTEMPTS:
#                 question = "Je n'ai pas compris. Dites simplement oui, ou non."

#         return False

#     def _generate_and_announce(self, topic: str, config) -> "ScenarioSession | None":
#         """
#         Appelle le modèle pour générer le scénario, construit la session,
#         et lit le résumé oral.
#         Retourne None si la génération échoue (les questions-réponses restent possibles).

#         La génération peut prendre plusieurs secondes. Elle est encadrée par
#         PatienceManager qui gère automatiquement les signaux d'ambiance et
#         les phrases de transition selon la durée réelle d'attente.
#         """
#         print("\nGénération du scénario en cours…")

#         scenario_json: Dict[str, Any] = {}
#         scenario_text: str = ""

#         def _do_generate():
#             nonlocal scenario_text, scenario_json
#             try:
#                 from vr_scenario_lib.scenario import generate_scenario as lib_generate
#                 result = lib_generate(topic=topic, llm_config=config)
#                 if isinstance(result, tuple):
#                     scenario_text, scenario_json = result[0], result[1]
#                 else:
#                     scenario_text = getattr(result, "text", str(result))
#                     scenario_json = getattr(result, "json", {})
#                 logger.info(
#                     "Scénario généré via la bibliothèque (%d caractères)", len(scenario_text)
#                 )
#             except Exception as exc:
#                 logger.warning(
#                     "Bibliothèque indisponible : %s — génération directe", exc
#                 )
#                 scenario_json, scenario_text = self._generate_via_llm(topic, config)

#         self.patience.run_with_patience(_do_generate)

#         if not scenario_json and not scenario_text:
#             self.io.speak(
#                 "La génération du scénario n'a pas abouti. "
#                 "Vous pouvez néanmoins me poser vos questions directement."
#             )
#             return None

#         # -- Construction de la session -----------------------------------
#         now = datetime.now(timezone.utc).isoformat()
#         try:
#             from vr_scenario_lib.scenario_store import ScenarioSession
#             session = ScenarioSession(
#                 scenario_id   = str(uuid.uuid4()),
#                 topic         = topic,
#                 scenario_text = scenario_text,
#                 scenario_json = scenario_json,
#                 created_at    = now,
#                 updated_at    = now,
#             )
#             logger.info("Session créée (identifiant=%s)", session.scenario_id)
#         except Exception as exc:
#             logger.warning("Création de session impossible : %s", exc)
#             session = None

#         # -- Présentation vocale du scénario ------------------------------
#         self._announce_scenario(scenario_json, scenario_text)
#         return session

#     def _generate_via_llm(
#         self, topic: str, config
#     ) -> "tuple[Dict[str, Any], str]":
#         """
#         Appel direct au modèle pour générer le scénario.
#         Retourne ({}, "") en cas d'échec.
#         """
#         if config is None:
#             return self._fallback_static_scenario(topic)

#         user_msg = "Génère un scénario de formation en réalité virtuelle sur le thème : " + topic

#         try:
#             raw = self._call_llm_raw(
#                 system     = SCENARIO_GEN_SYSTEM,
#                 user       = user_msg,
#                 config     = config,
#                 max_tokens = SCENARIO_GEN_MAX_TOKENS,
#             )
#         except Exception as exc:
#             logger.error("Génération par le modèle échouée : %s", exc)
#             return self._fallback_static_scenario(topic)

#         try:
#             import re
#             m = re.search(r'\{.*\}', raw, re.DOTALL)
#             if not m:
#                 raise ValueError("Structure JSON introuvable")
#             obj = json.loads(m.group())
#         except Exception as exc:
#             logger.error("Analyse du scénario échouée : %s | brut=%s", exc, raw[:200])
#             return self._fallback_static_scenario(topic)

#         text = self._json_to_text(obj, topic)
#         return obj, text

#     @staticmethod
#     def _json_to_text(obj: Dict[str, Any], topic: str) -> str:
#         """Convertit le scénario structuré en texte lisible."""
#         lines = ["# SCÉNARIO DE FORMATION — " + topic.upper(), ""]
#         titre = obj.get("titre", topic)
#         lines += ["## " + titre, ""]

#         objectifs = obj.get("objectifs", [])
#         if objectifs:
#             lines.append("### Objectifs")
#             for o in objectifs:
#                 lines.append("- " + str(o))
#             lines.append("")

#         for etape in obj.get("grandes_lignes", []):
#             num    = etape.get("etape", "")
#             titre_e = etape.get("titre", "")
#             desc   = etape.get("description", "")
#             lines.append("### Étape %s : %s" % (num, titre_e))
#             lines.append(desc)
#             lines.append("")

#         procs = obj.get("procedures_cles", [])
#         if procs:
#             lines.append("### Procédures clés")
#             for p in procs:
#                 lines.append("- " + str(p))
#             lines.append("")

#         vigilance = obj.get("points_vigilance", [])
#         if vigilance:
#             lines.append("### Points de vigilance")
#             for v in vigilance:
#                 lines.append("- " + str(v))
#             lines.append("")

#         return "\n".join(lines)

#     @staticmethod
#     def _fallback_static_scenario(topic: str) -> "tuple[Dict[str, Any], str]":
#         """Scénario minimal si le modèle de langage est inaccessible."""
#         obj = {
#             "titre": "Scénario " + topic,
#             "objectifs": [
#                 "Comprendre les principes fondamentaux de " + topic,
#                 "Maîtriser les procédures de sécurité essentielles",
#                 "Réagir de façon appropriée aux situations d'urgence",
#             ],
#             "grandes_lignes": [
#                 {
#                     "etape": 1,
#                     "titre": "Préparation",
#                     "description": "Vérifier les équipements et les protections individuelles avant toute intervention.",
#                 },
#                 {
#                     "etape": 2,
#                     "titre": "Intervention",
#                     "description": "Appliquer les procédures standard en respectant les consignes de sécurité.",
#                 },
#                 {
#                     "etape": 3,
#                     "titre": "Clôture",
#                     "description": "Consigner les actions effectuées et signaler tout incident survenu.",
#                 },
#             ],
#             "procedures_cles": [
#                 "Vérifier les équipements avant toute intervention",
#                 "Respecter les périmètres de sécurité",
#                 "Alerter la hiérarchie en cas d'incident",
#             ],
#             "points_vigilance": [
#                 "Ne jamais intervenir seul",
#                 "Toujours porter les protections adaptées à la situation",
#             ],
#             "resume_oral": (
#                 "Ce scénario porte sur le thème " + topic + ". "
#                 "Il se déroule en trois étapes : la préparation du matériel, "
#                 "l'intervention selon les procédures standard, "
#                 "et la clôture avec consignation des actions effectuées."
#             ),
#         }
#         text = VRScenarioApp._json_to_text(obj, topic)
#         return obj, text

#     def _announce_scenario(self, scenario_json: Dict[str, Any], scenario_text: str) -> None:
#         # """Présente les grandes lignes du scénario à voix haute."""
#         # print("\n" + "=" * 60)
#         # print("  SCÉNARIO GÉNÉRÉ")
#         # print("=" * 60)
#         # print(scenario_text[:1200] + ("…" if len(scenario_text) > 1200 else ""))
#         print("\n" + "=" * 60)
#         print("  SCÉNARIO TEXTUEL")
#         print("=" * 60)
#         print(scenario_text)
#         print("=" * 60)
#         # --- AJOUT : Affichage du JSON de configuration généré ---
#         print("\n" + "=" * 60)
#         print("  SCÉNARIO GÉNÉRÉ (JSON)")
#         print("=" * 60)
#         print(json.dumps(scenario_json, indent=2, ensure_ascii=False))
#         print("=" * 60 + "\n")
#         # ---------------------------------------------------------
#         # Lecture du résumé oral (conçu pour la synthèse vocale, sans listes)
#         resume = scenario_json.get("resume_oral", "")
#         if not resume:
#             titre = scenario_json.get("titre", "le scénario")
#             etapes = scenario_json.get("grandes_lignes", [])
#             if etapes:
#                 noms = ", ".join(str(e.get("titre", "")) for e in etapes[:4])
#                 resume = (
#                     "Le scénario intitulé " + titre
#                     + " se déroule en " + str(len(etapes))
#                     + " étapes : " + noms + "."
#                 )
#             else:
#                 resume = "Le scénario " + titre + " vient d'être généré."

#         self.io.speak("Voici les grandes lignes de votre scénario.")
#         self.io.speak(resume)

#         # Points de vigilance, si présents
#         vigilance = scenario_json.get("points_vigilance", [])
#         if vigilance:
#             points = " et ".join(vigilance[:3])
#             self.io.speak("Les points de vigilance à retenir sont : " + points + ".")

#         self.io.speak(
#             "Le scénario est prêt. "
#             "Posez-moi vos questions quand vous voulez. "
#             "Dites terminer pour clore la session."
#         )

#     # ------------------------------------------------------------------
#     # Phase 2 : questions-réponses supervisées
#     # ------------------------------------------------------------------

#     def _qa_loop(
#         self,
#         scenario_session,   # ScenarioSession | None
#         supervisor: SupervisorLLM,
#         config,
#     ) -> None:
#         """Boucle de questions et réponses supervisées.

#         Gestion du silence en trois niveaux :
#           Niveau 1 — silence léger    : on relance l'écoute sans rien dire
#           Niveau 2 — relance douce    : après le premier délai, une phrase
#                                         courte rassure sans interroger
#           Niveau 3 — silence prolongé : après plusieurs délais, question
#                                         explicite pour continuer ou terminer
#         """
#         print("\n" + "-" * 60)
#         print("[ SESSION DE QUESTIONS — posez vos questions ]")
#         print("-" * 60)

#         narrator = NarratorSession(
#             topic=scenario_session.topic if scenario_session else "général"
#         )
#         consecutive_timeouts = 0
#         MAX_TIMEOUTS  = 3
#         SOFT_NUDGE_AT = 1

#         while True:

#             # ---- 1. Capture de la question ---------------------------------
#             self.io.speak(pick("listening"))
#             try:
#                 question = self.io.listen_chunk(
#                     pause_threshold   = STT_SILENCE_TIMEOUT,
#                     phrase_time_limit = STT_PHRASE_TIME_LIMIT,
#                     listen_timeout    = STT_LISTEN_TIMEOUT,
#                 )
#                 consecutive_timeouts = 0
#             except RuntimeError as exc:
#                 consecutive_timeouts += 1
#                 logger.info(
#                     "Délai Q&R %d/%d : %s", consecutive_timeouts, MAX_TIMEOUTS, exc
#                 )

#                 if consecutive_timeouts >= MAX_TIMEOUTS:
#                     if self._ask_continue_qa():
#                         consecutive_timeouts = 0
#                     else:
#                         break
#                 elif consecutive_timeouts == SOFT_NUDGE_AT:
#                     self.io.speak(pick("soft_nudge"))
#                 continue

#             # ---- 2. Détection d'un mot de sortie ---------------------------
#             if any(w in question.lower() for w in EXIT_WORDS):
#                 print("\nSortie Q&R : '%s'" % question)
#                 break

#             print("\n[Question] " + question)
#             narrator.add_chunk(question)

#             # ---- 3. Réponse du modèle (avec patience) ----------------------
#             answer = self.patience.run_with_patience(
#                 self._get_answer, question, scenario_session, config
#             )
#             print("[Réponse] " + answer)
#             self.io.speak(answer)

#             # ---- 4. Supervision de l'échange -------------------------------
#             exchange = "Question : " + question + "\nRéponse : " + answer
#             decision = supervisor.analyse(narrator, exchange)
#             logger.info(
#                 "Superviseur Q&R : %s | '%s'",
#                 decision.decision.value,
#                 decision.message[:60] if decision.message else "",
#             )

#             if decision.decision == Decision.CONSEIL:
#                 print("\n[CONSEIL] " + decision.message)
#                 self.io.speak(decision.message)

#             elif decision.decision == Decision.STOP:
#                 print("\n[STOP] " + decision.message)
#                 self.io.interrupt_and_speak(decision.message)
#                 if not self._handle_stop_qa():
#                     break

#     @staticmethod
#     def _strip_filler_words(text: str) -> str:
#         """Supprime les locutions de remplissage les plus courantes (cf. FILLER_PATTERNS_FR).

#         Dégradation silencieuse : en cas d'erreur de traitement, le texte original
#         est retourné inchangé plutôt que de propager une exception pour un simple
#         nettoyage cosmétique (standard de robustesse : ne jamais casser la session
#         vocale pour une amélioration non critique).
#         """
#         if not text:
#             return text
#         try:
#             import re
#             cleaned = text
#             for pattern in FILLER_PATTERNS_FR:
#                 cleaned = re.sub(pattern, "", cleaned, flags=re.IGNORECASE | re.MULTILINE)
#             cleaned = re.sub(r"\s{2,}", " ", cleaned).strip()
#             cleaned = re.sub(r"^[,.]\s*", "", cleaned)
#             if cleaned and cleaned[0].islower():
#                 cleaned = cleaned[0].upper() + cleaned[1:]
#             return cleaned if cleaned else text
#         except Exception as exc:
#             logger.debug("_strip_filler_words : %s", exc)
#             return text

#     @staticmethod
#     def _enforce_max_sentences(text: str, max_sentences: int = QA_MAX_SENTENCES) -> str:
#         """Filet de sécurité : tronque la réponse si le modèle ignore la consigne de concision."""
#         if not text:
#             return text
#         try:
#             import re
#             sentences = [s for s in re.split(r'(?<=[.!?])\s+', text.strip()) if s]
#             if len(sentences) <= max_sentences:
#                 return text
#             return " ".join(sentences[:max_sentences])
#         except Exception as exc:
#             logger.debug("_enforce_max_sentences : %s", exc)
#             return text

#     def _get_answer(self, question: str, scenario_session, config) -> str:
#         """
#         Obtient une réponse du modèle à la question posée.
#         Priorité : discuss_scenario() de la bibliothèque, puis appel direct, puis message de repli.
#         Toute réponse exploitable passe par les filets de sécurité de concision
#         (suppression des mots de remplissage, plafond de phrases) avant d'être renvoyée.
#         """
#         # Via la bibliothèque de scénarios
#         if scenario_session is not None and config is not None:
#             try:
#                 from vr_scenario_lib.scenario import discuss_scenario
#                 reply = discuss_scenario(
#                     session      = scenario_session,
#                     user_message = question,
#                     llm_config   = config,
#                 )
#                 if reply and reply.strip():
#                     reply = self._strip_filler_words(reply.strip())
#                     return self._enforce_max_sentences(reply)
#             except Exception as exc:
#                 logger.warning("discuss_scenario erreur : %s — appel direct", exc)

#         # Appel direct avec contexte du scénario
#         if config is not None:
#             context = (
#                 scenario_session.scenario_text[:800]
#                 if scenario_session and scenario_session.scenario_text
#                 else ""
#             )
#             user_msg = (
#                 ("Contexte du scénario :\n" + context + "\n\n" if context else "")
#                 + "Question de l'apprenant : " + question
#             )
#             try:
#                 reply = self._call_llm_raw(
#                     system     = QA_SYSTEM,
#                     user       = user_msg,
#                     config     = config,
#                     max_tokens = QA_MAX_TOKENS,
#                 ).strip()
#                 reply = self._strip_filler_words(reply)
#                 return self._enforce_max_sentences(reply)
#             except Exception as exc:
#                 logger.error("Appel direct Q&R erreur : %s", exc)

#         return (
#             "Je n'ai pas pu obtenir de réponse pour le moment. "
#             "Vous pouvez reformuler votre question ou consulter la documentation du scénario."
#         )

#     # ------------------------------------------------------------------
#     # Fonctions auxiliaires
#     # ------------------------------------------------------------------

#     @staticmethod
#     def _call_llm_raw(*, system: str, user: str, config, max_tokens: int) -> str:
#         """Appel unifié au modèle de langage : bibliothèque, puis appel direct avec retry.

#         L'appel HTTP direct est retenté jusqu'à LLM_CALL_MAX_RETRIES fois en cas
#         d'erreur réseau, de timeout ou de réponse malformée, avec un délai croissant
#         entre tentatives (backoff linéaire). Lève RuntimeError si toutes les
#         tentatives échouent, pour que l'appelant applique son propre repli.
#         """
#         try:
#             from vr_scenario_lib.llm import call_llm
#             return call_llm(
#                 system=system, user=user,
#                 llm_config=config, max_tokens=max_tokens,
#             )
#         except ImportError:
#             pass

#         import urllib.request
#         import urllib.error

#         payload = json.dumps({
#             "model":      getattr(config, "model", "gpt-3.5-turbo"),
#             "max_tokens": max_tokens,
#             "messages":   [
#                 {"role": "system", "content": system},
#                 {"role": "user",   "content": user},
#             ],
#         }).encode()
#         api_url = getattr(config, "api_url", "https://api.openai.com/v1/chat/completions")
#         token   = getattr(config, "token", "")
#         req = urllib.request.Request(
#             api_url, data=payload,
#             headers={
#                 "Content-Type":  "application/json",
#                 "Authorization": "Bearer " + token,
#             },
#         )

#         last_exc: Optional[Exception] = None
#         total_attempts = LLM_CALL_MAX_RETRIES + 1
#         for attempt in range(1, total_attempts + 1):
#             try:
#                 with urllib.request.urlopen(req, timeout=20) as resp:
#                     data = json.loads(resp.read())
#                 return data["choices"][0]["message"]["content"]
#             except (urllib.error.URLError, TimeoutError, ValueError, KeyError) as exc:
#                 last_exc = exc
#                 logger.warning(
#                     "Appel LLM échoué (tentative %d/%d) : %s", attempt, total_attempts, exc
#                 )
#                 if attempt < total_attempts:
#                     time.sleep(LLM_CALL_RETRY_BACKOFF_S * attempt)

#         raise RuntimeError(
#             "Appel au modèle de langage impossible après %d tentative(s)" % total_attempts
#         ) from last_exc

#     def _ask_continue_qa(self) -> bool:
#         text = self.io.listen_short(pick("no_response_continue_check"))
#         if not text:
#             return False
#         return any(
#             w in text.lower()
#             for w in {"oui", "yes", "continuer", "continue", "si", "d'accord", "bien sûr"}
#         )

#     def _handle_stop_qa(self) -> bool:
#         """Pause après une alerte STOP en phase questions-réponses. Retourne True pour reprendre."""
#         self.io.speak(
#             "La session est interrompue suite à cette alerte. "
#             "Dites reprendre pour continuer vos questions, "
#             "ou terminer pour clore la session."
#         )
#         text = ""
#         try:
#             text = self.io.listen_chunk(
#                 pause_threshold   = 2.0,
#                 phrase_time_limit = 10,
#                 listen_timeout    = 12,
#             )
#         except RuntimeError:
#             pass
#         if any(w in text.lower() for w in {"reprendre", "continuer", "oui", "yes", "d'accord"}):
#             self.io.speak("Très bien. Je reste à l'écoute de vos questions.")
#             return True
#         return False

#     def _goodbye(self) -> None:
#         self.io.speak(
#             "Merci pour cette session de formation. "
#             "J'espère que ce scénario vous a été utile. "
#             "À très bientôt."
#         )
#         print("\nAu revoir !\n")

#     # ------------------------------------------------------------------
#     # Configuration du modèle de langage
#     # ------------------------------------------------------------------

#     def _setup_llm(self):
#         try:
#             from vr_scenario_lib.config import build_llm_config
#             return build_llm_config()
#         except Exception as exc:
#             logger.warning(
#                 "Configuration du modèle indisponible : %s — mode dégradé (scénarios statiques)",
#                 exc,
#             )
#             return None


# # ============================================================================
# # Interface en ligne de commande
# # ============================================================================

# def _parse_args() -> argparse.Namespace:
#     p = argparse.ArgumentParser(
#         description=(
#             "Application vocale de supervision de scénarios de formation en réalité virtuelle"
#         ),
#         formatter_class=argparse.ArgumentDefaultsHelpFormatter,
#     )
#     p.add_argument(
#         "--stt-backend", default="whisper", choices=["whisper", "google"],
#         help="Moteur de reconnaissance vocale.",
#     )
#     p.add_argument(
#         "--tts-backend", default=TTS_DEFAULT_BACKEND,
#         choices=["coqui", "piper", "gtts", "pyttsx3"],
#         help=(
#             "Moteur de synthèse vocale. "
#             "Les options 'coqui' et 'piper' fonctionnent entièrement hors ligne."
#         ),
#     )
#     p.add_argument(
#         "--language", default="fr",
#         help="Code de langue au format ISO 639-1 (fr par défaut).",
#     )
#     p.add_argument(
#         "--whisper-model", default=WHISPER_DEFAULT_MODEL,
#         choices=["tiny", "base", "small", "medium", "large"],
#         help="Taille du modèle Whisper. L'option 'small' est recommandée pour le français.",
#     )
#     p.add_argument(
#         "--coqui-model", default=COQUI_MODEL_FR,
#         help="Identifiant du modèle Coqui.",
#     )
#     p.add_argument(
#         "--piper-model", default=PIPER_MODEL_FR,
#         help="Nom du modèle Piper (exemple : fr_FR-tom-medium).",
#     )
#     p.add_argument(
#         "--debug", action="store_true",
#         help="Active les journaux de débogage complets.",
#     )
#     return p.parse_args()


# def main() -> None:
#     args = _parse_args()
#     if args.debug:
#         logging.getLogger().setLevel(logging.DEBUG)

#     io = VoiceIO(
#         stt_backend   = args.stt_backend,
#         tts_backend   = args.tts_backend,
#         language      = args.language,
#         whisper_model = args.whisper_model,
#         coqui_model   = args.coqui_model,
#         piper_model   = args.piper_model,
#     )
#     app = VRScenarioApp(io)
#     try:
#         app.run()
#     except KeyboardInterrupt:
#         print("\nSession interrompue par l'utilisateur.")
#     finally:
#         io.close()


# if __name__ == "__main__":
#     main()






# """
# Application vocale de supervision de scénarios de formation en réalité virtuelle.
# Version entreprise — standards industriels.

# RÔLE DE L'APPLICATION
# ----------------------
# L'utilisateur décrit librement un scénario de réalité virtuelle à voix haute.
# L'application écoute en continu, transcrit par fragments avec détection de voix,
# et soumet chaque fragment à un superviseur linguistique qui peut :
#   - CONTINUER  : rester silencieux (écoute neutre)
#   - CONSEIL    : intervenir poliment pour formuler un conseil
#   - STOP       : interrompre fermement pour signaler une erreur critique

# Architecture
# ------------
# VoiceIO          : reconnaissance vocale (Faster Whisper + VAD SpeechRecognition) + synthèse vocale française native.
# SupervisorLLM    : analyse chaque fragment, décide CONTINUER / CONSEIL / STOP.
# NarratorSession  : accumule la transcription, maintient le contexte du scénario.
# VRScenarioApp    : orchestration métier (initialisation + boucle de narration supervisée).
# PatienceManager  : retour sonore pendant les temps de traitement (signaux d'ambiance + phrases de transition).

# Moteurs de synthèse vocale française (ordre de priorité automatique)
# --------------------------------------------------------------------
# 1. coqui   -- Coqui VITS tts_models/fr/mai/tacotron2-DDC : voix neurale hors ligne, haute qualité
# 2. piper   -- Piper fr_FR-tom-medium                      : voix neurale hors ligne, très rapide
# 3. gtts    -- Google Synthèse vocale                      : voix en ligne, qualité maximale
# 4. pyttsx3 -- espeak-fr                                   : synthèse de base, sans dépendances

# Usage :
#     python app_vocal.py                            # détection automatique du meilleur moteur disponible
#     python app_vocal.py --tts-backend coqui        # Coqui VITS (hors ligne, haute qualité)
#     python app_vocal.py --tts-backend piper        # Piper (hors ligne, très rapide)
#     python app_vocal.py --tts-backend gtts         # Google Synthèse vocale (en ligne)
#     python app_vocal.py --stt-backend google       # Google Reconnaissance vocale (en ligne)
#     python app_vocal.py --whisper-model small      # meilleure précision de reconnaissance
#     python app_vocal.py --debug                    # journaux de débogage complets
# """

# from __future__ import annotations

# import argparse
# import json
# import logging
# import math
# import os
# import random
# import struct
# import sys
# import tempfile
# import threading
# import time
# import uuid
# from dataclasses import dataclass, field
# from datetime import datetime, timezone
# from enum import Enum
# from typing import Any, Dict, List, Optional

# # ---------------------------------------------------------------------------
# # Journalisation
# # ---------------------------------------------------------------------------
# logging.basicConfig(
#     level=logging.INFO,
#     format="%(asctime)s | %(name)-36s | %(levelname)-8s | %(message)s",
#     datefmt="%H:%M:%S",
# )
# logger = logging.getLogger(__name__)

# sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# # ============================================================================
# # Constantes
# # ============================================================================

# STT_LISTEN_TIMEOUT    = 8
# STT_PHRASE_TIME_LIMIT = 20          # durée maximale d'un fragment de narration
# STT_SILENCE_TIMEOUT   = 2.0         # silence détecté → fin du fragment
# STT_AMBIENT_DURATION  = 0.5
# TTS_TO_STT_SETTLE_S   = 0.3         # pause après la synthèse vocale, avant calibration du micro
#                                      # (laisse l'écho de la synthèse se dissiper — sinon les
#                                      # réponses courtes comme "oui" sont mal captées)
# TTS_SPEECH_RATE       = 145
# TTS_VOLUME            = 0.92
# WHISPER_DEFAULT_MODEL = "base"
# WHISPER_BEAM_SIZE     = 5

# # Biais lexical Whisper pour la capture du thème : un thème prononcé est un
# # fragment de 2 à 4 mots SANS contexte (contrairement aux questions en Q&R,
# # plus longues, où le modèle peut s'appuyer sur la phrase pour se corriger).
# # initial_prompt oriente la transcription vers le vocabulaire attendu —
# # technique standard pour fiabiliser la reconnaissance de termes techniques courts.
# WHISPER_TOPIC_PROMPT = (
#     "Thèmes de formation en réalité virtuelle industrielle : consignation gaz, "
#     "consignation électrique, sécurité incendie, premiers secours, travail en hauteur, "
#     "espace confiné, risque chimique, manutention, procédures de sécurité."
# )

# # Biais lexical Whisper pour les confirmations oui/non : cas encore plus
# # défavorable que le thème (un seul mot, souvent moins d'une seconde de signal).
# WHISPER_YESNO_PROMPT = (
#     "L'apprenant confirme le thème proposé. Il répond soit oui, c'est exact, "
#     "c'est le bon thème, soit non, ce n'est pas correct, ce n'est pas ça."
# )

# # Mots déclencheurs de fin de session
# # Rédigés pour être naturels à l'oral et fiables à la transcription
# EXIT_WORDS = {"quitter", "terminer", "au revoir", "fin", "arrêter", "c'est tout"}

# # Capture du thème — confirmation orale obligatoire (limite les scénarios générés
# # sur un thème mal compris par la reconnaissance vocale)
# TOPIC_MAX_ATTEMPTS         = 3
# TOPIC_CONFIRM_MAX_ATTEMPTS = 2   # un "oui"/"non" isolé est plus dur à transcrire qu'une phrase :
#                                   # on retente la question de confirmation seule avant d'abandonner
# TOPIC_CONFIRM_YES  = {"oui", "ouais", "yes", "exact", "correct", "c'est ça", "d'accord", "affirmatif"}
# TOPIC_CONFIRM_NO   = {"non", "no", "faux", "incorrect", "pas ça", "négatif"}


# # Moteurs de synthèse vocale française native
# TTS_DEFAULT_BACKEND   = "coqui"
# TTS_FALLBACK_CHAIN    = ["coqui", "piper", "gtts", "pyttsx3"]

# # Coqui : voix féminine Maï, accent français métropolitain soigné
# COQUI_MODEL_FR    = "tts_models/fr/mai/tacotron2-DDC"
# COQUI_SAMPLE_RATE = 22050

# # Piper : voix masculine Tom, accent français métropolitain naturel
# PIPER_MODEL_FR    = "fr_FR-tom-medium"
# PIPER_SAMPLE_RATE = 22050

# # Superviseur — instructions système
# SUPERVISOR_MAX_TOKENS = 256
# SUPERVISOR_SYSTEM = (
#     "Tu es un superviseur expert en sécurité de la réalité virtuelle et en procédures industrielles. "
#     "L'utilisateur décrit à voix haute un scénario de formation en réalité virtuelle. "
#     "Tu reçois des fragments de sa narration en temps réel.\n\n"
#     "Analyse le dernier fragment dans son contexte et réponds UNIQUEMENT avec un objet JSON :\n"
#     '{"decision": "CONTINUER" | "CONSEIL" | "STOP", "message": "<texte à dire, vide si CONTINUER>"}\n\n'
#     "Règles strictes :\n"
#     "- CONTINUER  : narration correcte, cohérente, sans danger. Message vide obligatoire.\n"
#     "- CONSEIL    : amélioration possible. Message court, positif, concret. Deux phrases maximum.\n"
#     "- STOP       : erreur critique de procédure, danger réel, incohérence grave. "
#     "Message direct et précis. Commence par 'Attention : '.\n"
#     "Ne jamais inventer de contexte non mentionné. Rester factuel."
# )

# # Génération de scénario — instructions système
# SCENARIO_GEN_MAX_TOKENS = 1024
# SCENARIO_GEN_SYSTEM = (
#     "Tu es un expert en conception de scénarios de formation en réalité virtuelle industrielle. "
#     "À partir d'un thème, génère un scénario structuré en JSON uniquement, sans aucun texte avant ou après.\n\n"
#     "Format JSON attendu (respecte exactement ces clés) :\n"
#     '{\n'
#     '  "titre": "Titre court du scénario",\n'
#     '  "objectifs": ["objectif 1", "objectif 2", "objectif 3"],\n'
#     '  "grandes_lignes": [\n'
#     '    {"etape": 1, "titre": "Titre de l\'étape", "description": "Description concise"},\n'
#     '    ...\n'
#     '  ],\n'
#     '  "procedures_cles": ["procédure 1", "procédure 2"],\n'
#     '  "points_vigilance": ["point 1", "point 2"],\n'
#     '  "resume_oral": "Texte fluide de trois à quatre phrases pour lecture vocale. Pas de listes, pas de symboles."\n'
#     '}\n\n'
#     "Le champ resume_oral doit être lisible à voix haute sans aucun accroc : pas de tirets, "
#     "pas de parenthèses, pas d'abréviations, pas de sigles. Quatre phrases au maximum."
# )

# # Questions-réponses — instructions système
# QA_MAX_TOKENS    = 180          # réduit : force la concision dès la génération
# QA_MAX_SENTENCES = 2            # filet de sécurité appliqué après coup (cf. _enforce_max_sentences)
# QA_SYSTEM = (
#     "Tu es un formateur expert qui aide un apprenant à comprendre un scénario de formation en réalité virtuelle. "
#     "Tu réponds aux questions en t'appuyant exclusivement sur le scénario fourni. "
#     "Réponse impérativement courte : une phrase si possible, deux phrases maximum. "
#     "Va droit à l'information utile. "
#     "Pas de listes, pas de tirets, pas de symboles, aucun mot ou formule de remplissage "
#     "(par exemple : en fait, donc, voilà, eh bien, du coup, en gros, extra). "
#     "Parle directement à l'apprenant, avec chaleur et précision."
# )

# # Appel au modèle de langage — robustesse réseau (standard industriel : retry + backoff)
# LLM_CALL_MAX_RETRIES     = 2     # tentatives supplémentaires après l'essai initial
# LLM_CALL_RETRY_BACKOFF_S = 1.5   # délai de base entre tentatives (croissance linéaire)

# # Locutions de remplissage à éliminer des réponses orales (filet de sécurité post-génération)
# FILLER_PATTERNS_FR = [
#     r"\ben fait\b,?\s*",
#     r"\bdonc\b,?\s*",
#     r"\bvoil[aà]\b,?\s*",
#     r"\beh bien\b,?\s*",
#     r"\bdu coup\b,?\s*",
#     r"\ben gros\b,?\s*",
#     r"\ben quelque sorte\b,?\s*",
#     r"\bpour ainsi dire\b,?\s*",
#     r"\b[aà] vrai dire\b,?\s*",
#     r"\bdisons que\b,?\s*",
#     r"\bil faut savoir que\b,?\s*",
#     r"\bextra\b\s*[!.,]?\s*",
#     r"^\s*alors,?\s*",
# ]


# # ============================================================================
# # Bibliothèque de phrases système
# # ----------------------------------------------------------------------------
# # Chaque entrée regroupe plusieurs formulations d'une même situation récurrente.
# # La fonction pick() tire une variante aléatoire à chaque appel, ce qui réduit
# # sensiblement la fatigue auditive lors de longues sessions.
# #
# # Principes de rédaction appliqués :
# #   - Phrases courtes, musicalité naturelle, rythme parlé
# #   - Pas de sigles ni d'anglicismes difficiles à prononcer
# #   - Pas de virgules superflues (pause TTS mal placée)
# #   - Finales ouvertes ou légèrement montantes (intonation invitante)
# #   - Chaleur professionnelle — ni trop formel ni trop familier
# # ============================================================================

# CACHED_PHRASES_FR: Dict[str, List[str]] = {

#     # Invitation à parler — brève, neutre, non répétitive
#     "listening": [
#         "Je vous écoute.",
#         "À vous.",
#         "Allez-y.",
#         "Je suis prêt.",
#         "La parole est à vous.",
#     ],

#     # Accusé de réception très court
#     "ack_short": [
#         "Bien reçu.",
#         "Compris.",
#         "Noté.",
#         "Entendu.",
#     ],

#     # Attente courte (1 à 3 secondes) — rien de verbal, juste un signal d'ambiance
#     # Ces phrases ne sont pas utilisées directement : le niveau 1 est traité
#     # uniquement par earcon, sans parole, pour ne pas alourdir les courtes attentes.
#     "thinking_short": [
#         "Un instant.",
#         "Je vérifie.",
#     ],

#     # Attente moyenne (3 à 10 secondes) — une phrase rassurante, pas d'explication
#     "thinking_medium": [
#         "Je prépare votre réponse.",
#         "Je consulte le scénario.",
#         "Je rassemble les éléments.",
#         "Je cherche la bonne information.",
#         "Je réfléchis à votre question.",
#     ],

#     # Attente longue (10 à 20 secondes) — on reconnaît que ça prend du temps
#     "thinking_long": [
#         "La question est détaillée, je finalise ma réponse.",
#         "Cela demande un peu plus de réflexion. Je suis sur le sujet.",
#         "Je creuse la question. Encore un court instant.",
#         "Je vérifie tous les éléments. Merci de votre patience.",
#     ],

#     # Attente très longue (au-delà de 20 secondes) — ton calme, pas d'alarme
#     "thinking_very_long": [
#         "Je suis toujours en train de traiter votre demande.",
#         "Le traitement prend un peu plus de temps que prévu. Je reste sur le sujet.",
#         "Toujours en cours. Je reviens vers vous très bientôt.",
#     ],

#     # Relance douce après un premier silence — sans interroger explicitement
#     "soft_nudge": [
#         "Je reste disponible si vous avez une question.",
#         "Prenez votre temps. Je vous écoute quand vous êtes prêt.",
#         "Pas de précipitation. Je suis là.",
#         "Vous pouvez continuer quand vous le souhaitez.",
#     ],

#     # Question explicite après un silence prolongé (oui / non)
#     "no_response_continue_check": [
#         "Je n'entends plus rien. Souhaitez-vous continuer la session ? "
#         "Dites oui pour continuer, ou non pour terminer.",
#         "Il y a un long silence. Voulez-vous poursuivre ? "
#         "Répondez oui ou non.",
#     ],
# }


# def pick(key: str) -> str:
#     """Tire aléatoirement une variante de phrase système pour réduire la répétition."""
#     options = CACHED_PHRASES_FR.get(key)
#     if not options:
#         return ""
#     return random.choice(options)


# # ============================================================================
# # Décision + NarratorSession
# # ============================================================================

# class Decision(Enum):
#     CONTINUER = "CONTINUER"
#     CONSEIL   = "CONSEIL"
#     STOP      = "STOP"


# @dataclass
# class SupervisorDecision:
#     decision: Decision = Decision.CONTINUER
#     message:  str      = ""

#     def must_speak(self) -> bool:
#         return self.decision in (Decision.CONSEIL, Decision.STOP)


# @dataclass
# class NarratorSession:
#     """Accumule la transcription et maintient le contexte pour le superviseur."""
#     topic:     str
#     chunks:    List[str] = field(default_factory=list)
#     full_text: str       = ""

#     def add_chunk(self, text: str) -> None:
#         self.chunks.append(text)
#         self.full_text = " ".join(self.chunks)

#     def context_window(self, n: int = 5) -> str:
#         return " ".join(self.chunks[-n:])

#     def summary(self) -> str:
#         return "%d séquence(s), environ %d mots" % (len(self.chunks), len(self.full_text.split()))


# # ============================================================================
# # PatienceManager — retour sonore pendant les temps de traitement
# # ----------------------------------------------------------------------------
# # Stratégie à paliers calibrée sur la durée d'attente réelle :
# #
# #   Moins de 1 s    : rien (imperceptible)
# #   De 1 à 3 s      : signal d'ambiance discret seul (pas de phrase —
# #                     évite la surcharge verbale sur les attentes courantes)
# #   De 3 à 10 s     : signal d'ambiance + courte phrase de transition
# #   Au-delà de 10 s : signal grave + phrase "longue attente", puis rappel
# #                     toutes les 12 s pour éviter le silence total anxiogène
# #
# # Le suivi tourne dans un fil d'exécution dédié pendant l'appel bloquant
# # au modèle de langage. Il s'arrête proprement (threading.Event) dès que
# # le résultat est disponible.
# # ============================================================================

# class PatienceManager:
#     """Pilote les signaux d'ambiance et les phrases de patience selon la durée réelle d'attente."""

#     LEVEL_SHORT_S     = 1.0    # moins de 1 s : rien
#     LEVEL_MEDIUM_S    = 3.0    # 1 à 3 s : signal seul
#     LEVEL_LONG_S      = 10.0   # 3 à 10 s : signal + phrase courte
#     LEVEL_VERY_LONG_S = 20.0   # au-delà de 10 s : signal grave + phrase longue

#     def __init__(self, io: "VoiceIO") -> None:
#         self.io = io
#         self._stop_event = threading.Event()
#         self._thread: Optional[threading.Thread] = None

#     def start(self) -> None:
#         self._stop_event.clear()
#         self._thread = threading.Thread(target=self._run, daemon=True)
#         self._thread.start()

#     def stop(self) -> None:
#         self._stop_event.set()
#         if self._thread is not None:
#             self._thread.join(timeout=2.0)
#             self._thread = None

#     def _run(self) -> None:
#         start = time.monotonic()
#         announced_medium    = False
#         announced_long      = False
#         announced_very_long = False

#         while not self._stop_event.is_set():
#             elapsed = time.monotonic() - start

#             if elapsed >= self.LEVEL_MEDIUM_S and not announced_medium:
#                 announced_medium = True
#                 self.io.play_earcon("patience_short")

#             if elapsed >= self.LEVEL_LONG_S and not announced_long:
#                 announced_long = True
#                 self.io.play_earcon("patience_medium")
#                 self.io.speak(pick("thinking_medium"), blocking=False)

#             if elapsed >= self.LEVEL_VERY_LONG_S and not announced_very_long:
#                 announced_very_long = True
#                 self.io.play_earcon("patience_long")
#                 self.io.speak(pick("thinking_long"), blocking=False)

#             # Rappel périodique au-delà du seuil très long
#             if announced_very_long and elapsed >= self.LEVEL_VERY_LONG_S + 12.0:
#                 self.io.speak(pick("thinking_very_long"), blocking=False)
#                 start -= 12.0  # reprogramme le prochain rappel dans 12 s

#             self._stop_event.wait(timeout=0.25)

#     def run_with_patience(self, fn, *args, **kwargs):
#         """Exécute fn(*args, **kwargs) en pilotant le retour sonore de patience."""
#         self.start()
#         try:
#             return fn(*args, **kwargs)
#         finally:
#             self.stop()


# # ============================================================================
# # SupervisorLLM
# # ============================================================================

# class SupervisorLLM:
#     """Analyse les fragments de narration et produit des décisions de supervision."""

#     def __init__(self, config) -> None:
#         self._config = config
#         self._lock   = threading.Lock()

#     def analyse(self, session: NarratorSession, new_chunk: str) -> SupervisorDecision:
#         if self._config is None:
#             return SupervisorDecision()

#         user_msg = (
#             "Thème du scénario : %s\n\n"
#             "Contexte (narration précédente) :\n%s\n\n"
#             "Nouveau fragment :\n%s"
#         ) % (session.topic, session.context_window(), new_chunk)

#         try:
#             with self._lock:
#                 raw = self._call_llm(user_msg)
#             return self._parse(raw)
#         except Exception as exc:
#             logger.warning("SupervisorLLM erreur : %s", exc)
#             return SupervisorDecision()

#     def _call_llm(self, user_msg: str) -> str:
#         # Tentative via la bibliothèque de scénarios
#         try:
#             from vr_scenario_lib.llm import call_llm
#             return call_llm(
#                 system=SUPERVISOR_SYSTEM,
#                 user=user_msg,
#                 llm_config=self._config,
#                 max_tokens=SUPERVISOR_MAX_TOKENS,
#             )
#         except ImportError:
#             pass

#         # Appel direct compatible avec l'interface de l'API de langage
#         import json
#         import urllib.request

#         payload = json.dumps({
#             "model":      getattr(self._config, "model", "gpt-3.5-turbo"),
#             "max_tokens": SUPERVISOR_MAX_TOKENS,
#             "messages":   [
#                 {"role": "system", "content": SUPERVISOR_SYSTEM},
#                 {"role": "user",   "content": user_msg},
#             ],
#         }).encode()
#         api_url = getattr(self._config, "api_url", "https://api.openai.com/v1/chat/completions")
#         token   = getattr(self._config, "token", "")
#         req = urllib.request.Request(
#             api_url,
#             data=payload,
#             headers={
#                 "Content-Type":  "application/json",
#                 "Authorization": "Bearer " + token,
#             },
#         )
#         with urllib.request.urlopen(req, timeout=15) as resp:
#             data = json.loads(resp.read())
#         return data["choices"][0]["message"]["content"]

#     def _parse(self, raw: str) -> SupervisorDecision:
#         import json
#         import re
#         m = re.search(r'\{.*\}', raw, re.DOTALL)
#         if not m:
#             logger.warning("SupervisorLLM : structure JSON introuvable dans '%s'", raw[:120])
#             return SupervisorDecision()
#         obj = json.loads(m.group())
#         try:
#             dec = Decision(obj.get("decision", "CONTINUER").upper())
#         except ValueError:
#             dec = Decision.CONTINUER
#         return SupervisorDecision(decision=dec, message=obj.get("message", "").strip())


# # ============================================================================
# # VoiceIO
# # ============================================================================

# class VoiceIO:
#     """Couche basse — reconnaissance vocale et synthèse vocale.

#     Principes fondamentaux
#     ----------------------
#     1. speak() est TOUJOURS bloquant dans le fil principal.
#        Une synthèse non bloquante avant écoute = écho capturé par le moteur de
#        reconnaissance.
#     2. Le microphone n'est jamais ouvert pendant la synthèse vocale.
#     3. L'enregistrement utilise la détection automatique de voix, pas une durée fixe.
#     4. interrupt_and_speak() coupe l'audio en cours avant de parler (alertes STOP).
#     5. play_earcon() est toujours non bloquant et très court (moins de 400 ms) :
#        il ne doit jamais retarder le flux conversationnel.
#     """

#     def __init__(
#         self,
#         stt_backend:   str = "whisper",
#         tts_backend:   str = TTS_DEFAULT_BACKEND,
#         language:      str = "fr",
#         whisper_model: str = WHISPER_DEFAULT_MODEL,
#         coqui_model:   str = COQUI_MODEL_FR,
#         piper_model:   str = PIPER_MODEL_FR,
#     ) -> None:
#         self.stt_backend      = stt_backend
#         self.tts_backend      = tts_backend
#         self.language         = language
#         self.whisper_model_id = whisper_model
#         self.coqui_model_id   = coqui_model
#         self.piper_model_id   = piper_model

#         self._recognizer    = None
#         self._whisper_model = None
#         self._tts_engine    = None
#         self._coqui_model   = None
#         self._lock_tts      = threading.Lock()

#         self._init()

#     # ------------------------------------------------------------------
#     # Initialisation
#     # ------------------------------------------------------------------

#     def _init(self) -> None:
#         self._init_stt()
#         self._init_tts()
#         logger.info(
#             "VoiceIO prêt — Reconnaissance : %s | Synthèse : %s | Langue : %s",
#             self.stt_backend, self.tts_backend, self.language,
#         )

#     def _init_stt(self) -> None:
#         try:
#             import speech_recognition as sr
#             self._recognizer = sr.Recognizer()
#             self._recognizer.energy_threshold         = 4000
#             self._recognizer.pause_threshold          = STT_SILENCE_TIMEOUT
#             self._recognizer.dynamic_energy_threshold = True
#         except ImportError:
#             raise RuntimeError(
#                 "Module SpeechRecognition manquant. "
#                 "Installez-le avec : pip install SpeechRecognition PyAudio"
#             )
#         if self.stt_backend == "whisper":
#             self._whisper_model = self._load_whisper()

#     def _load_whisper(self) -> object:
#         try:
#             from faster_whisper import WhisperModel
#             logger.info("Chargement du modèle Faster Whisper '%s'...", self.whisper_model_id)
#             model = WhisperModel(
#                 self.whisper_model_id,
#                 device="cpu",
#                 compute_type="int8",
#             )
#             logger.info("Faster Whisper prêt")
#             return model
#         except ImportError:
#             raise RuntimeError(
#                 "Module faster-whisper manquant. Installez-le avec : pip install faster-whisper"
#             )

#     def _init_tts(self) -> None:
#         chain = (
#             [self.tts_backend]
#             + [b for b in TTS_FALLBACK_CHAIN if b != self.tts_backend]
#         )
#         for backend in chain:
#             try:
#                 if backend == "coqui":
#                     self._init_coqui()
#                 elif backend == "piper":
#                     self._init_piper()
#                 elif backend == "gtts":
#                     self._init_gtts()
#                 elif backend == "pyttsx3":
#                     self._init_pyttsx3()
#                 else:
#                     continue
#                 self.tts_backend = backend
#                 logger.info("Moteur de synthèse actif : %s", backend)
#                 return
#             except Exception as exc:
#                 logger.warning(
#                     "Moteur '%s' indisponible : %s — essai du suivant", backend, exc
#                 )

#         raise RuntimeError(
#             "Aucun moteur de synthèse vocale disponible. "
#             "Installez au minimum : pip install coqui-tts sounddevice soundfile"
#         )

#     # ------------------------------------------------------------------
#     # Initialisation Coqui VITS — voix neurale française hors ligne
#     # ------------------------------------------------------------------

#     def _init_coqui(self) -> None:
#         try:
#             from TTS.api import TTS as CoquiTTS
#             import sounddevice  # noqa: F401
#             import soundfile    # noqa: F401
#         except ImportError:
#             raise RuntimeError(
#                 "Module Coqui manquant. Installez-le avec : pip install coqui-tts sounddevice soundfile"
#             )
#         logger.info("Chargement de Coqui '%s'...", self.coqui_model_id)
#         self._coqui_model = CoquiTTS(
#             model_name=self.coqui_model_id,
#             progress_bar=False,
#             gpu=False,
#         )
#         logger.info("Coqui prêt")

#     # ------------------------------------------------------------------
#     # Initialisation Piper — voix neurale française hors ligne, très rapide
#     # ------------------------------------------------------------------

#     def _init_piper(self) -> None:
#         try:
#             import piper  # noqa: F401
#         except ImportError:
#             raise RuntimeError("Module piper-tts manquant. Installez-le avec : pip install piper-tts")
#         logger.info("Piper disponible — modèle '%s'", self.piper_model_id)

#     # ------------------------------------------------------------------
#     # Initialisation Google Synthèse vocale — en ligne
#     # ------------------------------------------------------------------

#     def _init_gtts(self) -> None:
#         try:
#             import gtts    # noqa: F401
#             import pygame  # noqa: F401
#         except ImportError:
#             raise RuntimeError(
#                 "Modules gTTS ou pygame manquants. Installez-les avec : pip install gTTS pygame"
#             )
#         logger.info("Google Synthèse vocale initialisée")

#     # ------------------------------------------------------------------
#     # Initialisation pyttsx3 — solution de secours ultime
#     # ------------------------------------------------------------------

#     def _init_pyttsx3(self) -> None:
#         try:
#             import pyttsx3
#         except ImportError:
#             raise RuntimeError(
#                 "Module pyttsx3 manquant. Installez-le avec : pip install pyttsx3"
#             )

#         engine = pyttsx3.init()
#         engine.setProperty("rate",   TTS_SPEECH_RATE)
#         engine.setProperty("volume", TTS_VOLUME)

#         fr_voice_found = False
#         # Priorité 1 : voix fr_FR espeak-ng (accent français métropolitain)
#         # Priorité 2 : toute voix contenant "french" ou "fr" dans le nom ou l'identifiant
#         for priority in ("fr_FR", "fr-FR", "french", "fr"):
#             for v in engine.getProperty("voices"):
#                 name_lower = v.name.lower()
#                 id_lower   = v.id.lower()
#                 if priority.lower() in id_lower or priority.lower() in name_lower:
#                     engine.setProperty("voice", v.id)
#                     logger.info(
#                         "pyttsx3 : voix française sélectionnée : %s (%s)", v.name, v.id
#                     )
#                     fr_voice_found = True
#                     break
#             if fr_voice_found:
#                 break

#         if not fr_voice_found:
#             logger.warning(
#                 "Aucune voix française trouvée dans pyttsx3. "
#                 "Sur Linux : sudo apt install espeak-ng-data"
#             )

#         self._tts_engine = engine
#         logger.info("pyttsx3 initialisé (voix système)")

#     # ------------------------------------------------------------------
#     # Synthèse vocale — TOUJOURS bloquante dans le fil principal
#     # ------------------------------------------------------------------

#     def interrupt_and_speak(self, text: str) -> None:
#         """Coupe l'audio en cours PUIS parle. Réservé aux alertes STOP urgentes."""
#         self._stop_audio()
#         self.speak(text)

#     def _stop_audio(self) -> None:
#         """Arrête immédiatement la lecture audio (tous moteurs)."""
#         try:
#             if self.tts_backend in ("coqui", "piper"):
#                 import sounddevice as sd
#                 sd.stop()
#             elif self.tts_backend == "gtts":
#                 try:
#                     import pygame
#                     if pygame.mixer.get_init():
#                         pygame.mixer.music.stop()
#                 except Exception:
#                     pass
#         except Exception as exc:
#             logger.debug("_stop_audio : %s", exc)

#     @staticmethod
#     def _sanitize_tts(text: str) -> str:
#         """Nettoie le texte avant synthèse vocale.

#         Transformations appliquées dans l'ordre :
#         1. Blocs de code Markdown (``` … ```) → supprimés
#         2. Emphase Markdown (* ** _ __ ~ ~~)  → supprimée (le texte reste)
#         3. Titres Markdown (# ## ###…)         → supprimés (le texte reste)
#         4. Adresses web (http / https / ftp)   → remplacées par « lien »
#         5. Ponctuation non orale               → remplacée ou supprimée
#         6. Espaces multiples et lignes vides   → normalisés
#         """
#         import re

#         # 1. Blocs de code (``` … ```) et code en ligne (` … `)
#         text = re.sub(r'```.*?```', '', text, flags=re.DOTALL)
#         text = re.sub(r'`[^`]*`', '', text)

#         # 2. Emphase Markdown
#         text = re.sub(r'\*{1,3}|_{1,3}|~{1,2}', '', text)

#         # 3. Titres Markdown en début de ligne
#         text = re.sub(r'^\s*#{1,6}\s*', '', text, flags=re.MULTILINE)

#         # 4. Adresses web
#         text = re.sub(r'https?://\S+|ftp://\S+', 'lien', text)

#         # 5. Ponctuation non orale
#         text = re.sub(r'^\s*[-•–—]\s+', '', text, flags=re.MULTILINE)
#         text = re.sub(r'^\s*[\-|: ]{3,}\s*$', '', text, flags=re.MULTILINE)
#         text = re.sub(r'\|', ' ', text)
#         text = re.sub(r'[\\/@#$%^&{}\[\]<>=]', ' ', text)
#         text = re.sub(r'[(){}\[\]]', ' ', text)
#         text = re.sub(r'\.{2,}', ',', text)
#         text = re.sub(r'\s*[–—]\s*', ', ', text)
#         text = re.sub(r'\*+', '', text)
#         text = re.sub(r'_+', ' ', text)

#         # 6. Normalisation des espaces et des sauts de ligne
#         text = re.sub(r'\n+', ' ', text)
#         text = re.sub(r' {2,}', ' ', text)

#         return text.strip()

#     def speak(self, text: str, *, blocking: bool = True) -> None:
#         """Synthèse vocale en français natif.

#         blocking=True (par défaut) : retourne APRÈS la fin de la lecture.
#         blocking=False             : usage exceptionnel uniquement —
#                                      par exemple, phrases de patience émises
#                                      par PatienceManager pendant qu'un autre fil
#                                      attend le modèle de langage. Dans ce cas,
#                                      le microphone n'est pas sollicité en parallèle,
#                                      donc pas de risque d'écho capturé.
#         RÈGLE : ne JAMAIS appeler avec blocking=False juste avant écoute().
#         """
#         if not text or not text.strip():
#             return
#         text = self._sanitize_tts(text)
#         if not text:
#             return
#         logger.info("Synthèse [%s] : '%s'", self.tts_backend, text[:80])

#         dispatch = {
#             "coqui":   self._speak_coqui,
#             "piper":   self._speak_piper,
#             "gtts":    self._speak_gtts,
#             "pyttsx3": self._speak_pyttsx3,
#         }
#         fn = dispatch.get(self.tts_backend)
#         if fn is None:
#             logger.error("Moteur de synthèse inconnu : %s", self.tts_backend)
#             print("[Synthèse] " + text)
#             return
#         fn(text, blocking)

#     # ------------------------------------------------------------------
#     # Signaux d'ambiance — retour sonore court pendant les attentes
#     # ------------------------------------------------------------------
#     # Générés à la volée (sinusoïdes), aucune dépendance audio externe
#     # supplémentaire au-delà de sounddevice (déjà requis par coqui/piper).
#     # En cas d'indisponibilité : dégradation silencieuse, sans exception
#     # propagée ni affichage parasite — un signal manqué ne doit jamais
#     # bloquer le flux conversationnel.
#     # ------------------------------------------------------------------

#     _EARCON_PROFILES = {
#         # (fréquence Hz, durée s, amplitude) — profils courts et discrets
#         "patience_short":  (880.0, 0.10, 0.15),   # signal discret, attente courte
#         "patience_medium": (660.0, 0.15, 0.18),   # signal intermédiaire
#         "patience_long":   (440.0, 0.22, 0.20),   # signal grave, longue attente
#     }

#     def play_earcon(self, profile: str) -> None:
#         """Joue un signal d'ambiance court et non bloquant. Échec silencieux."""
#         params = self._EARCON_PROFILES.get(profile)
#         if params is None:
#             return
#         try:
#             threading.Thread(
#                 target=self._play_earcon_sync, args=(params,), daemon=True
#             ).start()
#         except Exception as exc:
#             logger.debug("play_earcon : %s", exc)

#     def _play_earcon_sync(self, params) -> None:
#         freq, duration, amplitude = params
#         try:
#             import sounddevice as sd
#             sample_rate = 22050
#             n_samples = int(sample_rate * duration)
#             tone = [
#                 amplitude * math.sin(2 * math.pi * freq * (i / sample_rate))
#                 for i in range(n_samples)
#             ]
#             sd.play(tone, sample_rate)
#             sd.wait()
#         except Exception as exc:
#             logger.debug("Signal d'ambiance indisponible (%s), ignoré", exc)

#     # ------------------------------------------------------------------
#     # Moteur Coqui — référence qualité
#     # ------------------------------------------------------------------

#     def _speak_coqui(self, text: str, blocking: bool) -> None:
#         tmp_path: Optional[str] = None
#         try:
#             import soundfile as sf
#             import sounddevice as sd

#             with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
#                 tmp_path = f.name

#             with self._lock_tts:
#                 self._coqui_model.tts_to_file(text=text, file_path=tmp_path)

#             data, sr = sf.read(tmp_path, dtype="float32")
#             if blocking:
#                 sd.play(data, sr)
#                 sd.wait()
#             else:
#                 sd.play(data, sr)

#         except Exception as exc:
#             logger.error("Coqui erreur : %s", exc)
#             print("[Synthèse] " + text)
#         finally:
#             if tmp_path and os.path.exists(tmp_path):
#                 try:
#                     os.unlink(tmp_path)
#                 except OSError:
#                     pass

#     # ------------------------------------------------------------------
#     # Moteur Piper — latence minimale
#     # ------------------------------------------------------------------

#     def _speak_piper(self, text: str, blocking: bool) -> None:
#         tmp_path: Optional[str] = None
#         try:
#             import subprocess
#             import soundfile as sf
#             import sounddevice as sd

#             with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
#                 tmp_path = f.name

#             result = subprocess.run(
#                 ["piper", "--model", self.piper_model_id, "--output_file", tmp_path],
#                 input=text.encode("utf-8"),
#                 capture_output=True,
#                 timeout=30,
#             )
#             if result.returncode != 0:
#                 raise RuntimeError(
#                     "piper code de retour=%d : %s" % (
#                         result.returncode, result.stderr.decode()
#                     )
#                 )

#             data, sr = sf.read(tmp_path, dtype="float32")
#             if blocking:
#                 sd.play(data, sr)
#                 sd.wait()
#             else:
#                 sd.play(data, sr)

#         except FileNotFoundError:
#             logger.error("Exécutable 'piper' introuvable. pip install piper-tts")
#             print("[Synthèse] " + text)
#         except Exception as exc:
#             logger.error("Piper erreur : %s", exc)
#             print("[Synthèse] " + text)
#         finally:
#             if tmp_path and os.path.exists(tmp_path):
#                 try:
#                     os.unlink(tmp_path)
#                 except OSError:
#                     pass

#     # ------------------------------------------------------------------
#     # Moteur Google Synthèse vocale — en ligne
#     # ------------------------------------------------------------------

#     def _speak_gtts(self, text: str, blocking: bool) -> None:
#         tmp_path: Optional[str] = None
#         try:
#             from gtts import gTTS
#             import pygame

#             tts = gTTS(text=text, lang=self.language, slow=False)
#             with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
#                 tmp_path = f.name
#             tts.save(tmp_path)

#             # Réinitialisation propre du mixeur à chaque appel
#             if pygame.mixer.get_init():
#                 pygame.mixer.quit()
#             pygame.mixer.init(frequency=22050, size=-16, channels=1, buffer=512)
#             pygame.mixer.music.load(tmp_path)
#             pygame.mixer.music.play()

#             if blocking:
#                 while pygame.mixer.music.get_busy():
#                     time.sleep(0.05)
#                 pygame.mixer.quit()

#         except Exception as exc:
#             logger.error("Google Synthèse vocale erreur : %s", exc)
#             print("[Synthèse] " + text)
#         finally:
#             if tmp_path and os.path.exists(tmp_path):
#                 try:
#                     time.sleep(0.1)
#                     os.unlink(tmp_path)
#                 except OSError:
#                     pass

#     # ------------------------------------------------------------------
#     # Moteur pyttsx3 — solution de secours ultime
#     # ------------------------------------------------------------------

#     def _speak_pyttsx3(self, text: str, blocking: bool) -> None:
#         with self._lock_tts:
#             try:
#                 self._tts_engine.say(text)
#                 if blocking:
#                     self._tts_engine.runAndWait()
#                 else:
#                     t = threading.Thread(
#                         target=self._tts_engine.runAndWait, daemon=True
#                     )
#                     t.start()
#             except Exception as exc:
#                 logger.error("pyttsx3 erreur : %s", exc)
#                 print("[Synthèse] " + text)

#     # ------------------------------------------------------------------
#     # Reconnaissance vocale — fragment avec détection automatique de voix
#     # ------------------------------------------------------------------

#     def listen_chunk(
#         self,
#         *,
#         pause_threshold:   float = STT_SILENCE_TIMEOUT,
#         phrase_time_limit: int   = STT_PHRASE_TIME_LIMIT,
#         listen_timeout:    float = STT_LISTEN_TIMEOUT,
#         initial_prompt:    Optional[str] = None,
#     ) -> str:
#         """Capture un fragment de parole et le transcrit.

#         initial_prompt (Whisper uniquement) : biais lexical optionnel pour
#         orienter la transcription vers un vocabulaire attendu (ex. thèmes
#         techniques courts, sans contexte de phrase). Ignoré sur le moteur Google.

#         Retourne :
#             Le texte transcrit (non vide).

#         Lève :
#             RuntimeError si la capture ou la transcription échoue,
#             ou si aucune voix n'est détectée dans le délai imparti.
#         """
#         import speech_recognition as sr

#         original = self._recognizer.pause_threshold
#         self._recognizer.pause_threshold = pause_threshold
#         tmp_path: Optional[str] = None

#         try:
#             with sr.Microphone() as src:
#                 logger.info(
#                     "Écoute (silence=%.1fs, max=%ds)...",
#                     pause_threshold, phrase_time_limit,
#                 )
#                 self._recognizer.adjust_for_ambient_noise(src, duration=STT_AMBIENT_DURATION)
#                 audio = self._recognizer.listen(
#                     src,
#                     timeout=listen_timeout,
#                     phrase_time_limit=phrase_time_limit,
#                 )

#             with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
#                 tmp_path = f.name
#                 f.write(audio.get_wav_data())

#             if self.stt_backend == "whisper":
#                 return self._transcribe_whisper(tmp_path, initial_prompt=initial_prompt)
#             else:
#                 return self._transcribe_google(audio)

#         except sr.WaitTimeoutError as exc:
#             raise RuntimeError("Aucune voix détectée dans le délai imparti") from exc

#         finally:
#             self._recognizer.pause_threshold = original
#             if tmp_path and os.path.exists(tmp_path):
#                 try:
#                     os.unlink(tmp_path)
#                 except OSError:
#                     pass

#     def listen_short(self, question: str, timeout: float = 8.0, initial_prompt: Optional[str] = None) -> str:
#         """Pose une question brève et attend une réponse courte.
#         Retourne une chaîne vide en cas d'absence de réponse (aucune exception propagée).

#         Utilise les mêmes seuils d'écoute que la boucle de questions-réponses
#         (déjà fiables en usage réel) plutôt que des seuils plus courts : un silence
#         de coupure trop bref clipe une prononciation hésitante (thème technique,
#         mot inhabituel) ou un simple "oui" arrivant juste après la synthèse vocale.

#         initial_prompt : transmis à Whisper pour biaiser la reconnaissance vers
#         un vocabulaire attendu (cf. listen_chunk).
#         """
#         self.speak(question)
#         self.speak(pick("listening"))
#         time.sleep(TTS_TO_STT_SETTLE_S)  # laisse l'écho de la synthèse se dissiper avant calibration du micro
#         try:
#             return self.listen_chunk(
#                 pause_threshold=STT_SILENCE_TIMEOUT,
#                 phrase_time_limit=STT_PHRASE_TIME_LIMIT,
#                 listen_timeout=timeout,
#                 initial_prompt=initial_prompt,
#             )
#         except RuntimeError as exc:
#             logger.info("listen_short : aucune réponse (%s)", exc)
#             return ""

#     def _transcribe_whisper(self, wav_path: str, initial_prompt: Optional[str] = None) -> str:
#         try:
#             segments_gen, info = self._whisper_model.transcribe(
#                 wav_path,
#                 language=self.language,
#                 beam_size=WHISPER_BEAM_SIZE,
#                 initial_prompt=initial_prompt,
#             )
#         except TypeError:
#             # Repli : version de faster-whisper ne supportant pas initial_prompt
#             logger.debug(
#                 "Whisper : 'initial_prompt' non supporté par cette version, "
#                 "repli sans biais lexical"
#             )
#             segments_gen, info = self._whisper_model.transcribe(
#                 wav_path,
#                 language=self.language,
#                 beam_size=WHISPER_BEAM_SIZE,
#             )
#         logger.debug(
#             "Whisper : langue=%s (%.0f%%)",
#             info.language, info.language_probability * 100,
#         )
#         text = " ".join(seg.text.strip() for seg in segments_gen).strip()
#         if not text:
#             raise RuntimeError("La reconnaissance vocale n'a produit aucun texte")
#         logger.info("Fragment reconnu : '%s'", text[:100])
#         return text

#     def _transcribe_google(self, audio) -> str:
#         import speech_recognition as sr
#         lang = "fr-FR" if self.language == "fr" else (self.language + "-" + self.language.upper())
#         try:
#             text = self._recognizer.recognize_google(audio, language=lang)
#             logger.info("Reconnaissance Google : '%s'", text[:100])
#             return text
#         except sr.UnknownValueError:
#             raise RuntimeError("Reconnaissance Google : audio incompréhensible")
#         except sr.RequestError as exc:
#             raise RuntimeError("Reconnaissance Google : erreur de service : %s" % exc)

#     # ------------------------------------------------------------------
#     # Nettoyage
#     # ------------------------------------------------------------------

#     def close(self) -> None:
#         self._stop_audio()
#         if self._tts_engine is not None:
#             try:
#                 with self._lock_tts:
#                     self._tts_engine.stop()
#             except Exception:
#                 pass
#         logger.info("VoiceIO fermé")


# # ============================================================================
# # VRScenarioApp — orchestration principale
# # ============================================================================

# class VRScenarioApp:
#     """
#     Flux en deux phases :

#     PHASE 1 — Génération et présentation du scénario
#       - Saisie vocale du thème
#       - Le modèle de langage génère un scénario structuré
#       - Construction de la session de scénario
#       - Lecture du résumé oral par synthèse vocale

#     PHASE 2 — Questions et réponses supervisées
#       - L'utilisateur pose librement ses questions à voix haute
#       - Le modèle répond en s'appuyant sur le scénario généré
#       - Le superviseur évalue chaque échange : CONTINUER / CONSEIL / STOP
#       - Un mot de sortie clôt proprement la session

#     Gestion de la patience
#     ----------------------
#     Toute attente potentiellement longue (génération de scénario, appel
#     au modèle en questions-réponses) est encadrée par PatienceManager,
#     qui pilote automatiquement les signaux d'ambiance et les phrases de
#     transition selon la durée réelle d'attente.
#     """

#     def __init__(self, io: VoiceIO) -> None:
#         self.io = io
#         self.patience = PatienceManager(io)

#     def run(self) -> None:
#         self._welcome()
#         topic      = self._ask_topic()
#         config     = self._setup_llm()
#         supervisor = SupervisorLLM(config)

#         # -- Phase 1 : génération et présentation -------------------------
#         scenario_session = self._generate_and_announce(topic, config)

#         # -- Phase 2 : questions-réponses supervisées ---------------------
#         self._qa_loop(scenario_session, supervisor, config)

#         self._goodbye()

#     # ------------------------------------------------------------------
#     # Phase 1 : génération du scénario
#     # ------------------------------------------------------------------

#     def _welcome(self) -> None:
#         print("\n" + "=" * 60)
#         print("  APPLICATION VOCALE — SCÉNARIOS DE FORMATION EN RÉALITÉ VIRTUELLE")
#         print("=" * 60)
#         self.io.speak(
#             "Bienvenue dans votre assistant vocal de scénarios de formation. "
#             "Je vais générer un scénario à partir du thème que vous me donnerez, "
#             "vous en présenter les grandes lignes, "
#             "puis répondre à vos questions. "
#             "Dites terminer à tout moment pour clore la session."
#         )

#     def _ask_topic(self) -> str:
#         """Capture le thème par la voix avec confirmation orale explicite.

#         La reconnaissance vocale peut mal comprendre le thème prononcé
#         (homophones, bruit ambiant, accent). Générer un scénario complet sur
#         un thème erroné coûte cher en temps et en confiance utilisateur :
#         on confirme donc systématiquement avant de poursuivre.

#         Stratégie :
#           1. Capture du thème (écoute courte, déjà tolérante au silence).
#           2. Confirmation orale explicite ("Le thème retenu est X, correct ?").
#           3. Nouvelle tentative si infirmé, absent ou ambigu — jusqu'à
#              TOPIC_MAX_ATTEMPTS.
#           4. Repli sur un thème par défaut si aucune confirmation n'est obtenue
#              (dégradation silencieuse : la session continue malgré tout).

#         Toute erreur inattendue de la couche vocale (microphone, moteur STT)
#         est absorbée localement : un échec de capture du thème ne doit jamais
#         interrompre la session.
#         """
#         prompt = (
#             "Sur quel thème souhaitez-vous travailler ? "
#             "Vous pouvez me dire, par exemple : la consignation gaz, "
#             "la sécurité incendie, ou les premiers secours."
#         )
#         for attempt in range(1, TOPIC_MAX_ATTEMPTS + 1):
#             try:
#                 text = self.io.listen_short(prompt, initial_prompt=WHISPER_TOPIC_PROMPT)
#             except Exception as exc:
#                 logger.warning(
#                     "Capture du thème échouée (tentative %d/%d) : %s",
#                     attempt, TOPIC_MAX_ATTEMPTS, exc,
#                 )
#                 text = ""

#             if text and self._confirm_topic(text):
#                 self.io.speak("Très bien. Le thème retenu est : " + text + ".")
#                 logger.info("Thème confirmé : '%s'", text)
#                 print("\nThème : " + text)
#                 return text

#             logger.info(
#                 "Thème non confirmé (tentative %d/%d) : '%s'",
#                 attempt, TOPIC_MAX_ATTEMPTS, text,
#             )
#             if attempt < TOPIC_MAX_ATTEMPTS:
#                 prompt = "Je vous écoute à nouveau. Quel est le thème souhaité ?"
#                 self.io.speak("D'accord, reprenons.")

#         text = "sécurité industrielle"
#         self.io.speak(
#             "Je n'arrive pas à confirmer le thème. "
#             "Je vais utiliser la sécurité industrielle par défaut."
#         )
#         logger.info("Thème : repli par défaut '%s'", text)
#         print("\nThème : " + text)
#         return text

#     def _confirm_topic(self, topic: str) -> bool:
#         """Demande une confirmation orale explicite du thème compris.

#         Un "oui"/"non" isolé est plus difficile à transcrire correctement qu'une
#         phrase complète (peu de contexte pour le modèle de reconnaissance). On
#         retente donc la question de confirmation elle-même, jusqu'à
#         TOPIC_CONFIRM_MAX_ATTEMPTS fois, avant de conclure à une non-confirmation —
#         plutôt que de forcer l'utilisateur à reprononcer tout le thème pour un
#         simple aléa de reconnaissance sur "oui".
#         """
#         question = "Le thème retenu est : " + topic + ". Est-ce correct ? Dites oui ou non."
#         for attempt in range(1, TOPIC_CONFIRM_MAX_ATTEMPTS + 1):
#             try:
#                 answer = self.io.listen_short(question, initial_prompt=WHISPER_YESNO_PROMPT).lower()
#             except Exception as exc:
#                 logger.debug(
#                     "_confirm_topic (tentative %d/%d) : %s",
#                     attempt, TOPIC_CONFIRM_MAX_ATTEMPTS, exc,
#                 )
#                 answer = ""

#             if any(w in answer for w in TOPIC_CONFIRM_NO):
#                 return False
#             if any(w in answer for w in TOPIC_CONFIRM_YES):
#                 return True

#             if attempt < TOPIC_CONFIRM_MAX_ATTEMPTS:
#                 question = "Je n'ai pas compris. Dites simplement oui, ou non."

#         return False

#     def _generate_and_announce(self, topic: str, config) -> "ScenarioSession | None":
#         """
#         Appelle le modèle pour générer le scénario, construit la session,
#         et lit le résumé oral.
#         Retourne None si la génération échoue (les questions-réponses restent possibles).

#         La génération peut prendre plusieurs secondes. Elle est encadrée par
#         PatienceManager qui gère automatiquement les signaux d'ambiance et
#         les phrases de transition selon la durée réelle d'attente.
#         """
#         print("\nGénération du scénario en cours…")

#         scenario_json: Dict[str, Any] = {}
#         scenario_text: str = ""

#         def _do_generate():
#             nonlocal scenario_text, scenario_json
#             try:
#                 from vr_scenario_lib.scenario import generate_scenario as lib_generate
#                 result = lib_generate(topic=topic, llm_config=config)
#                 if isinstance(result, tuple):
#                     scenario_text, scenario_json = result[0], result[1]
#                 else:
#                     scenario_text = getattr(result, "text", str(result))
#                     scenario_json = getattr(result, "json", {})
#                 logger.info(
#                     "Scénario généré via la bibliothèque (%d caractères)", len(scenario_text)
#                 )
#             except Exception as exc:
#                 logger.warning(
#                     "Bibliothèque indisponible : %s — génération directe", exc
#                 )
#                 scenario_json, scenario_text = self._generate_via_llm(topic, config)

#         self.patience.run_with_patience(_do_generate)

#         if not scenario_json and not scenario_text:
#             self.io.speak(
#                 "La génération du scénario n'a pas abouti. "
#                 "Vous pouvez néanmoins me poser vos questions directement."
#             )
#             return None

#         # -- Construction de la session -----------------------------------
#         now = datetime.now(timezone.utc).isoformat()
#         try:
#             from vr_scenario_lib.scenario_store import ScenarioSession
#             session = ScenarioSession(
#                 scenario_id   = str(uuid.uuid4()),
#                 topic         = topic,
#                 scenario_text = scenario_text,
#                 scenario_json = scenario_json,
#                 created_at    = now,
#                 updated_at    = now,
#             )
#             logger.info("Session créée (identifiant=%s)", session.scenario_id)
#         except Exception as exc:
#             logger.warning("Création de session impossible : %s", exc)
#             session = None

#         # -- Présentation vocale du scénario ------------------------------
#         self._announce_scenario(scenario_json, scenario_text)
#         return session

#     def _generate_via_llm(
#         self, topic: str, config
#     ) -> "tuple[Dict[str, Any], str]":
#         """
#         Appel direct au modèle pour générer le scénario.
#         Retourne ({}, "") en cas d'échec.
#         """
#         if config is None:
#             return self._fallback_static_scenario(topic)

#         user_msg = "Génère un scénario de formation en réalité virtuelle sur le thème : " + topic

#         try:
#             raw = self._call_llm_raw(
#                 system     = SCENARIO_GEN_SYSTEM,
#                 user       = user_msg,
#                 config     = config,
#                 max_tokens = SCENARIO_GEN_MAX_TOKENS,
#             )
#         except Exception as exc:
#             logger.error("Génération par le modèle échouée : %s", exc)
#             return self._fallback_static_scenario(topic)

#         try:
#             import re
#             m = re.search(r'\{.*\}', raw, re.DOTALL)
#             if not m:
#                 raise ValueError("Structure JSON introuvable")
#             obj = json.loads(m.group())
#         except Exception as exc:
#             logger.error("Analyse du scénario échouée : %s | brut=%s", exc, raw[:200])
#             return self._fallback_static_scenario(topic)

#         text = self._json_to_text(obj, topic)
#         return obj, text

#     @staticmethod
#     def _json_to_text(obj: Dict[str, Any], topic: str) -> str:
#         """Convertit le scénario structuré en texte lisible."""
#         lines = ["# SCÉNARIO DE FORMATION — " + topic.upper(), ""]
#         titre = obj.get("titre", topic)
#         lines += ["## " + titre, ""]

#         objectifs = obj.get("objectifs", [])
#         if objectifs:
#             lines.append("### Objectifs")
#             for o in objectifs:
#                 lines.append("- " + str(o))
#             lines.append("")

#         for etape in obj.get("grandes_lignes", []):
#             num    = etape.get("etape", "")
#             titre_e = etape.get("titre", "")
#             desc   = etape.get("description", "")
#             lines.append("### Étape %s : %s" % (num, titre_e))
#             lines.append(desc)
#             lines.append("")

#         procs = obj.get("procedures_cles", [])
#         if procs:
#             lines.append("### Procédures clés")
#             for p in procs:
#                 lines.append("- " + str(p))
#             lines.append("")

#         vigilance = obj.get("points_vigilance", [])
#         if vigilance:
#             lines.append("### Points de vigilance")
#             for v in vigilance:
#                 lines.append("- " + str(v))
#             lines.append("")

#         return "\n".join(lines)

#     @staticmethod
#     def _fallback_static_scenario(topic: str) -> "tuple[Dict[str, Any], str]":
#         """Scénario minimal si le modèle de langage est inaccessible."""
#         obj = {
#             "titre": "Scénario " + topic,
#             "objectifs": [
#                 "Comprendre les principes fondamentaux de " + topic,
#                 "Maîtriser les procédures de sécurité essentielles",
#                 "Réagir de façon appropriée aux situations d'urgence",
#             ],
#             "grandes_lignes": [
#                 {
#                     "etape": 1,
#                     "titre": "Préparation",
#                     "description": "Vérifier les équipements et les protections individuelles avant toute intervention.",
#                 },
#                 {
#                     "etape": 2,
#                     "titre": "Intervention",
#                     "description": "Appliquer les procédures standard en respectant les consignes de sécurité.",
#                 },
#                 {
#                     "etape": 3,
#                     "titre": "Clôture",
#                     "description": "Consigner les actions effectuées et signaler tout incident survenu.",
#                 },
#             ],
#             "procedures_cles": [
#                 "Vérifier les équipements avant toute intervention",
#                 "Respecter les périmètres de sécurité",
#                 "Alerter la hiérarchie en cas d'incident",
#             ],
#             "points_vigilance": [
#                 "Ne jamais intervenir seul",
#                 "Toujours porter les protections adaptées à la situation",
#             ],
#             "resume_oral": (
#                 "Ce scénario porte sur le thème " + topic + ". "
#                 "Il se déroule en trois étapes : la préparation du matériel, "
#                 "l'intervention selon les procédures standard, "
#                 "et la clôture avec consignation des actions effectuées."
#             ),
#         }
#         text = VRScenarioApp._json_to_text(obj, topic)
#         return obj, text

#     def _announce_scenario(self, scenario_json: Dict[str, Any], scenario_text: str) -> None:
#         # """Présente les grandes lignes du scénario à voix haute."""
#         # print("\n" + "=" * 60)
#         # print("  SCÉNARIO GÉNÉRÉ")
#         # print("=" * 60)
#         # print(scenario_text[:1200] + ("…" if len(scenario_text) > 1200 else ""))
#         print("\n" + "=" * 60)
#         print("  SCÉNARIO TEXTUEL")
#         print("=" * 60)
#         print(scenario_text)
#         print("=" * 60)
#         # --- AJOUT : Affichage du JSON de configuration généré ---
#         print("\n" + "=" * 60)
#         print("  SCÉNARIO GÉNÉRÉ (JSON)")
#         print("=" * 60)
#         print(json.dumps(scenario_json, indent=2, ensure_ascii=False))
#         print("=" * 60 + "\n")
#         # ---------------------------------------------------------
#         # Lecture du résumé oral (conçu pour la synthèse vocale, sans listes)
#         resume = scenario_json.get("resume_oral", "")
#         if not resume:
#             titre = scenario_json.get("titre", "le scénario")
#             etapes = scenario_json.get("grandes_lignes", [])
#             if etapes:
#                 noms = ", ".join(str(e.get("titre", "")) for e in etapes[:4])
#                 resume = (
#                     "Le scénario intitulé " + titre
#                     + " se déroule en " + str(len(etapes))
#                     + " étapes : " + noms + "."
#                 )
#             else:
#                 resume = "Le scénario " + titre + " vient d'être généré."

#         self.io.speak("Voici les grandes lignes de votre scénario.")
#         self.io.speak(resume)

#         # Points de vigilance, si présents
#         vigilance = scenario_json.get("points_vigilance", [])
#         if vigilance:
#             points = " et ".join(vigilance[:3])
#             self.io.speak("Les points de vigilance à retenir sont : " + points + ".")

#         self.io.speak(
#             "Le scénario est prêt. "
#             "Posez-moi vos questions quand vous voulez. "
#             "Dites terminer pour clore la session."
#         )

#     # ------------------------------------------------------------------
#     # Phase 2 : questions-réponses supervisées
#     # ------------------------------------------------------------------

#     def _qa_loop(
#         self,
#         scenario_session,   # ScenarioSession | None
#         supervisor: SupervisorLLM,
#         config,
#     ) -> None:
#         """Boucle de questions et réponses supervisées.

#         Gestion du silence en trois niveaux :
#           Niveau 1 — silence léger    : on relance l'écoute sans rien dire
#           Niveau 2 — relance douce    : après le premier délai, une phrase
#                                         courte rassure sans interroger
#           Niveau 3 — silence prolongé : après plusieurs délais, question
#                                         explicite pour continuer ou terminer
#         """
#         print("\n" + "-" * 60)
#         print("[ SESSION DE QUESTIONS — posez vos questions ]")
#         print("-" * 60)

#         narrator = NarratorSession(
#             topic=scenario_session.topic if scenario_session else "général"
#         )
#         consecutive_timeouts = 0
#         MAX_TIMEOUTS  = 3
#         SOFT_NUDGE_AT = 1

#         while True:

#             # ---- 1. Capture de la question ---------------------------------
#             self.io.speak(pick("listening"))
#             try:
#                 question = self.io.listen_chunk(
#                     pause_threshold   = STT_SILENCE_TIMEOUT,
#                     phrase_time_limit = STT_PHRASE_TIME_LIMIT,
#                     listen_timeout    = STT_LISTEN_TIMEOUT,
#                 )
#                 consecutive_timeouts = 0
#             except RuntimeError as exc:
#                 consecutive_timeouts += 1
#                 logger.info(
#                     "Délai Q&R %d/%d : %s", consecutive_timeouts, MAX_TIMEOUTS, exc
#                 )

#                 if consecutive_timeouts >= MAX_TIMEOUTS:
#                     if self._ask_continue_qa():
#                         consecutive_timeouts = 0
#                     else:
#                         break
#                 elif consecutive_timeouts == SOFT_NUDGE_AT:
#                     self.io.speak(pick("soft_nudge"))
#                 continue

#             # ---- 2. Détection d'un mot de sortie ---------------------------
#             if any(w in question.lower() for w in EXIT_WORDS):
#                 print("\nSortie Q&R : '%s'" % question)
#                 break

#             print("\n[Question] " + question)
#             narrator.add_chunk(question)

#             # ---- 3. Réponse du modèle (avec patience) ----------------------
#             answer = self.patience.run_with_patience(
#                 self._get_answer, question, scenario_session, config
#             )
#             print("[Réponse] " + answer)
#             self.io.speak(answer)

#             # ---- 4. Supervision de l'échange -------------------------------
#             exchange = "Question : " + question + "\nRéponse : " + answer
#             decision = supervisor.analyse(narrator, exchange)
#             logger.info(
#                 "Superviseur Q&R : %s | '%s'",
#                 decision.decision.value,
#                 decision.message[:60] if decision.message else "",
#             )

#             if decision.decision == Decision.CONSEIL:
#                 print("\n[CONSEIL] " + decision.message)
#                 self.io.speak(decision.message)

#             elif decision.decision == Decision.STOP:
#                 print("\n[STOP] " + decision.message)
#                 self.io.interrupt_and_speak(decision.message)
#                 if not self._handle_stop_qa():
#                     break

#     @staticmethod
#     def _strip_filler_words(text: str) -> str:
#         """Supprime les locutions de remplissage les plus courantes (cf. FILLER_PATTERNS_FR).

#         Dégradation silencieuse : en cas d'erreur de traitement, le texte original
#         est retourné inchangé plutôt que de propager une exception pour un simple
#         nettoyage cosmétique (standard de robustesse : ne jamais casser la session
#         vocale pour une amélioration non critique).
#         """
#         if not text:
#             return text
#         try:
#             import re
#             cleaned = text
#             for pattern in FILLER_PATTERNS_FR:
#                 cleaned = re.sub(pattern, "", cleaned, flags=re.IGNORECASE | re.MULTILINE)
#             cleaned = re.sub(r"\s{2,}", " ", cleaned).strip()
#             cleaned = re.sub(r"^[,.]\s*", "", cleaned)
#             if cleaned and cleaned[0].islower():
#                 cleaned = cleaned[0].upper() + cleaned[1:]
#             return cleaned if cleaned else text
#         except Exception as exc:
#             logger.debug("_strip_filler_words : %s", exc)
#             return text

#     @staticmethod
#     def _enforce_max_sentences(text: str, max_sentences: int = QA_MAX_SENTENCES) -> str:
#         """Filet de sécurité : tronque la réponse si le modèle ignore la consigne de concision."""
#         if not text:
#             return text
#         try:
#             import re
#             sentences = [s for s in re.split(r'(?<=[.!?])\s+', text.strip()) if s]
#             if len(sentences) <= max_sentences:
#                 return text
#             return " ".join(sentences[:max_sentences])
#         except Exception as exc:
#             logger.debug("_enforce_max_sentences : %s", exc)
#             return text

#     def _get_answer(self, question: str, scenario_session, config) -> str:
#         """
#         Obtient une réponse du modèle à la question posée.
#         Priorité : discuss_scenario() de la bibliothèque, puis appel direct, puis message de repli.
#         Toute réponse exploitable passe par les filets de sécurité de concision
#         (suppression des mots de remplissage, plafond de phrases) avant d'être renvoyée.
#         """
#         # Via la bibliothèque de scénarios
#         if scenario_session is not None and config is not None:
#             try:
#                 from vr_scenario_lib.scenario import discuss_scenario
#                 reply = discuss_scenario(
#                     session      = scenario_session,
#                     user_message = question,
#                     llm_config   = config,
#                 )
#                 if reply and reply.strip():
#                     reply = self._strip_filler_words(reply.strip())
#                     return self._enforce_max_sentences(reply)
#             except Exception as exc:
#                 logger.warning("discuss_scenario erreur : %s — appel direct", exc)

#         # Appel direct avec contexte du scénario
#         if config is not None:
#             context = (
#                 scenario_session.scenario_text[:800]
#                 if scenario_session and scenario_session.scenario_text
#                 else ""
#             )
#             user_msg = (
#                 ("Contexte du scénario :\n" + context + "\n\n" if context else "")
#                 + "Question de l'apprenant : " + question
#             )
#             try:
#                 reply = self._call_llm_raw(
#                     system     = QA_SYSTEM,
#                     user       = user_msg,
#                     config     = config,
#                     max_tokens = QA_MAX_TOKENS,
#                 ).strip()
#                 reply = self._strip_filler_words(reply)
#                 return self._enforce_max_sentences(reply)
#             except Exception as exc:
#                 logger.error("Appel direct Q&R erreur : %s", exc)

#         return (
#             "Je n'ai pas pu obtenir de réponse pour le moment. "
#             "Vous pouvez reformuler votre question ou consulter la documentation du scénario."
#         )

#     # ------------------------------------------------------------------
#     # Fonctions auxiliaires
#     # ------------------------------------------------------------------

#     @staticmethod
#     def _call_llm_raw(*, system: str, user: str, config, max_tokens: int) -> str:
#         """Appel unifié au modèle de langage : bibliothèque, puis appel direct avec retry.

#         L'appel HTTP direct est retenté jusqu'à LLM_CALL_MAX_RETRIES fois en cas
#         d'erreur réseau, de timeout ou de réponse malformée, avec un délai croissant
#         entre tentatives (backoff linéaire). Lève RuntimeError si toutes les
#         tentatives échouent, pour que l'appelant applique son propre repli.
#         """
#         try:
#             from vr_scenario_lib.llm import call_llm
#             return call_llm(
#                 system=system, user=user,
#                 llm_config=config, max_tokens=max_tokens,
#             )
#         except ImportError:
#             pass

#         import urllib.request
#         import urllib.error

#         payload = json.dumps({
#             "model":      getattr(config, "model", "gpt-3.5-turbo"),
#             "max_tokens": max_tokens,
#             "messages":   [
#                 {"role": "system", "content": system},
#                 {"role": "user",   "content": user},
#             ],
#         }).encode()
#         api_url = getattr(config, "api_url", "https://api.openai.com/v1/chat/completions")
#         token   = getattr(config, "token", "")
#         req = urllib.request.Request(
#             api_url, data=payload,
#             headers={
#                 "Content-Type":  "application/json",
#                 "Authorization": "Bearer " + token,
#             },
#         )

#         last_exc: Optional[Exception] = None
#         total_attempts = LLM_CALL_MAX_RETRIES + 1
#         for attempt in range(1, total_attempts + 1):
#             try:
#                 with urllib.request.urlopen(req, timeout=20) as resp:
#                     data = json.loads(resp.read())
#                 return data["choices"][0]["message"]["content"]
#             except (urllib.error.URLError, TimeoutError, ValueError, KeyError) as exc:
#                 last_exc = exc
#                 logger.warning(
#                     "Appel LLM échoué (tentative %d/%d) : %s", attempt, total_attempts, exc
#                 )
#                 if attempt < total_attempts:
#                     time.sleep(LLM_CALL_RETRY_BACKOFF_S * attempt)

#         raise RuntimeError(
#             "Appel au modèle de langage impossible après %d tentative(s)" % total_attempts
#         ) from last_exc

#     def _ask_continue_qa(self) -> bool:
#         text = self.io.listen_short(pick("no_response_continue_check"))
#         if not text:
#             return False
#         return any(
#             w in text.lower()
#             for w in {"oui", "yes", "continuer", "continue", "si", "d'accord", "bien sûr"}
#         )

#     def _handle_stop_qa(self) -> bool:
#         """Pause après une alerte STOP en phase questions-réponses. Retourne True pour reprendre."""
#         self.io.speak(
#             "La session est interrompue suite à cette alerte. "
#             "Dites reprendre pour continuer vos questions, "
#             "ou terminer pour clore la session."
#         )
#         text = ""
#         try:
#             text = self.io.listen_chunk(
#                 pause_threshold   = 2.0,
#                 phrase_time_limit = 10,
#                 listen_timeout    = 12,
#             )
#         except RuntimeError:
#             pass
#         if any(w in text.lower() for w in {"reprendre", "continuer", "oui", "yes", "d'accord"}):
#             self.io.speak("Très bien. Je reste à l'écoute de vos questions.")
#             return True
#         return False

#     def _goodbye(self) -> None:
#         self.io.speak(
#             "Merci pour cette session de formation. "
#             "J'espère que ce scénario vous a été utile. "
#             "À très bientôt."
#         )
#         print("\nAu revoir !\n")

#     # ------------------------------------------------------------------
#     # Configuration du modèle de langage
#     # ------------------------------------------------------------------

#     def _setup_llm(self):
#         try:
#             from vr_scenario_lib.config import build_llm_config
#             return build_llm_config()
#         except Exception as exc:
#             logger.warning(
#                 "Configuration du modèle indisponible : %s — mode dégradé (scénarios statiques)",
#                 exc,
#             )
#             return None


# # ============================================================================
# # Interface en ligne de commande
# # ============================================================================

# def _parse_args() -> argparse.Namespace:
#     p = argparse.ArgumentParser(
#         description=(
#             "Application vocale de supervision de scénarios de formation en réalité virtuelle"
#         ),
#         formatter_class=argparse.ArgumentDefaultsHelpFormatter,
#     )
#     p.add_argument(
#         "--stt-backend", default="whisper", choices=["whisper", "google"],
#         help="Moteur de reconnaissance vocale.",
#     )
#     p.add_argument(
#         "--tts-backend", default=TTS_DEFAULT_BACKEND,
#         choices=["coqui", "piper", "gtts", "pyttsx3"],
#         help=(
#             "Moteur de synthèse vocale. "
#             "Les options 'coqui' et 'piper' fonctionnent entièrement hors ligne."
#         ),
#     )
#     p.add_argument(
#         "--language", default="fr",
#         help="Code de langue au format ISO 639-1 (fr par défaut).",
#     )
#     p.add_argument(
#         "--whisper-model", default=WHISPER_DEFAULT_MODEL,
#         choices=["tiny", "base", "small", "medium", "large"],
#         help="Taille du modèle Whisper. L'option 'small' est recommandée pour le français.",
#     )
#     p.add_argument(
#         "--coqui-model", default=COQUI_MODEL_FR,
#         help="Identifiant du modèle Coqui.",
#     )
#     p.add_argument(
#         "--piper-model", default=PIPER_MODEL_FR,
#         help="Nom du modèle Piper (exemple : fr_FR-tom-medium).",
#     )
#     p.add_argument(
#         "--debug", action="store_true",
#         help="Active les journaux de débogage complets.",
#     )
#     return p.parse_args()


# def main() -> None:
#     args = _parse_args()
#     if args.debug:
#         logging.getLogger().setLevel(logging.DEBUG)

#     io = VoiceIO(
#         stt_backend   = args.stt_backend,
#         tts_backend   = args.tts_backend,
#         language      = args.language,
#         whisper_model = args.whisper_model,
#         coqui_model   = args.coqui_model,
#         piper_model   = args.piper_model,
#     )
#     app = VRScenarioApp(io)
#     try:
#         app.run()
#     except KeyboardInterrupt:
#         print("\nSession interrompue par l'utilisateur.")
#     finally:
#         io.close()


# if __name__ == "__main__":
#     main()











# """
# Application vocale de supervision de scénarios de formation en réalité virtuelle.
# Version entreprise — standards industriels.

# RÔLE DE L'APPLICATION
# ----------------------
# L'utilisateur décrit librement un scénario de réalité virtuelle à voix haute.
# L'application écoute en continu, transcrit par fragments avec détection de voix,
# et soumet chaque fragment à un superviseur linguistique qui peut :
#   - CONTINUER  : rester silencieux (écoute neutre)
#   - CONSEIL    : intervenir poliment pour formuler un conseil
#   - STOP       : interrompre fermement pour signaler une erreur critique

# Architecture
# ------------
# VoiceIO          : reconnaissance vocale (Faster Whisper + VAD SpeechRecognition) + synthèse vocale française native.
# SupervisorLLM    : analyse chaque fragment, décide CONTINUER / CONSEIL / STOP.
# NarratorSession  : accumule la transcription, maintient le contexte du scénario.
# VRScenarioApp    : orchestration métier (initialisation + boucle de narration supervisée).
# PatienceManager  : retour sonore pendant les temps de traitement (signaux d'ambiance + phrases de transition).

# Moteurs de synthèse vocale française (ordre de priorité automatique)
# --------------------------------------------------------------------
# 1. coqui   -- Coqui VITS tts_models/fr/mai/tacotron2-DDC : voix neurale hors ligne, haute qualité
# 2. piper   -- Piper fr_FR-tom-medium                      : voix neurale hors ligne, très rapide
# 3. gtts    -- Google Synthèse vocale                      : voix en ligne, qualité maximale
# 4. pyttsx3 -- espeak-fr                                   : synthèse de base, sans dépendances

# Usage :
#     python app_vocal.py                            # détection automatique du meilleur moteur disponible
#     python app_vocal.py --tts-backend coqui        # Coqui VITS (hors ligne, haute qualité)
#     python app_vocal.py --tts-backend piper        # Piper (hors ligne, très rapide)
#     python app_vocal.py --tts-backend gtts         # Google Synthèse vocale (en ligne)
#     python app_vocal.py --stt-backend google       # Google Reconnaissance vocale (en ligne)
#     python app_vocal.py --whisper-model small      # meilleure précision de reconnaissance
#     python app_vocal.py --debug                    # journaux de débogage complets
# """

# from __future__ import annotations

# import argparse
# import json
# import logging
# import math
# import os
# import random
# import struct
# import sys
# import tempfile
# import threading
# import time
# import uuid
# from dataclasses import dataclass, field
# from datetime import datetime, timezone
# from enum import Enum
# from typing import Any, Dict, List, Optional

# # ---------------------------------------------------------------------------
# # Journalisation
# # ---------------------------------------------------------------------------
# logging.basicConfig(
#     level=logging.INFO,
#     format="%(asctime)s | %(name)-36s | %(levelname)-8s | %(message)s",
#     datefmt="%H:%M:%S",
# )
# logger = logging.getLogger(__name__)

# sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# # ============================================================================
# # Constantes
# # ============================================================================

# STT_LISTEN_TIMEOUT    = 8
# STT_PHRASE_TIME_LIMIT = 20          # durée maximale d'un fragment de narration
# STT_SILENCE_TIMEOUT   = 2.0         # silence détecté → fin du fragment
# STT_AMBIENT_DURATION  = 0.5
# TTS_TO_STT_SETTLE_S   = 0.3         # pause après la synthèse vocale, avant calibration du micro
#                                      # (laisse l'écho de la synthèse se dissiper — sinon les
#                                      # réponses courtes comme "oui" sont mal captées)
# TTS_SPEECH_RATE       = 145
# TTS_VOLUME            = 0.92
# WHISPER_DEFAULT_MODEL = "base"
# WHISPER_BEAM_SIZE     = 5

# # Biais lexical Whisper pour la capture du thème : un thème prononcé est un
# # fragment de 2 à 4 mots SANS contexte (contrairement aux questions en Q&R,
# # plus longues, où le modèle peut s'appuyer sur la phrase pour se corriger).
# # initial_prompt oriente la transcription vers le vocabulaire attendu —
# # technique standard pour fiabiliser la reconnaissance de termes techniques courts.
# WHISPER_TOPIC_PROMPT = (
#     "Thèmes de formation en réalité virtuelle industrielle : consignation gaz, "
#     "consignation électrique, sécurité incendie, premiers secours, travail en hauteur, "
#     "espace confiné, risque chimique, manutention, procédures de sécurité."
# )

# # Biais lexical Whisper pour les confirmations oui/non : cas encore plus
# # défavorable que le thème (un seul mot, souvent moins d'une seconde de signal).
# WHISPER_YESNO_PROMPT = (
#     "L'apprenant confirme le thème proposé. Il répond soit oui, c'est exact, "
#     "c'est le bon thème, soit non, ce n'est pas correct, ce n'est pas ça."
# )

# # Mots déclencheurs de fin de session
# # Rédigés pour être naturels à l'oral et fiables à la transcription
# EXIT_WORDS = {"quitter", "terminer", "au revoir", "fin", "arrêter", "c'est tout"}

# # Capture du thème — confirmation orale obligatoire (limite les scénarios générés
# # sur un thème mal compris par la reconnaissance vocale)
# TOPIC_MAX_ATTEMPTS         = 3
# TOPIC_CONFIRM_MAX_ATTEMPTS = 2   # un "oui"/"non" isolé est plus dur à transcrire qu'une phrase :
#                                   # on retente la question de confirmation seule avant d'abandonner
# TOPIC_CONFIRM_YES  = {"oui", "ouais", "yes", "exact", "correct", "c'est ça", "d'accord", "affirmatif"}
# TOPIC_CONFIRM_NO   = {"non", "no", "faux", "incorrect", "pas ça", "négatif"}


# # Moteurs de synthèse vocale française native
# TTS_DEFAULT_BACKEND   = "coqui"
# TTS_FALLBACK_CHAIN    = ["coqui", "piper", "gtts", "pyttsx3"]

# # Coqui : voix féminine Maï, accent français métropolitain soigné
# COQUI_MODEL_FR    = "tts_models/fr/mai/tacotron2-DDC"
# COQUI_SAMPLE_RATE = 22050

# # Piper : voix masculine Tom, accent français métropolitain naturel
# PIPER_MODEL_FR    = "fr_FR-tom-medium"
# PIPER_SAMPLE_RATE = 22050

# # Superviseur — instructions système
# SUPERVISOR_MAX_TOKENS = 256
# SUPERVISOR_SYSTEM = (
#     "Tu es un superviseur expert en sécurité de la réalité virtuelle et en procédures industrielles. "
#     "L'utilisateur décrit à voix haute un scénario de formation en réalité virtuelle. "
#     "Tu reçois des fragments de sa narration en temps réel.\n\n"
#     "Analyse le dernier fragment dans son contexte et réponds UNIQUEMENT avec un objet JSON :\n"
#     '{"decision": "CONTINUER" | "CONSEIL" | "STOP", "message": "<texte à dire, vide si CONTINUER>"}\n\n'
#     "Règles strictes :\n"
#     "- CONTINUER  : narration correcte, cohérente, sans danger. Message vide obligatoire.\n"
#     "- CONSEIL    : amélioration possible. Message court, positif, concret. Deux phrases maximum.\n"
#     "- STOP       : erreur critique de procédure, danger réel, incohérence grave. "
#     "Message direct et précis. Commence par 'Attention : '.\n"
#     "Ne jamais inventer de contexte non mentionné. Rester factuel."
# )

# # Génération de scénario — instructions système
# SCENARIO_GEN_MAX_TOKENS = 1024
# SCENARIO_GEN_SYSTEM = (
#     "Tu es un expert en conception de scénarios de formation en réalité virtuelle industrielle. "
#     "À partir d'un thème, génère un scénario structuré en JSON uniquement, sans aucun texte avant ou après.\n\n"
#     "Format JSON attendu (respecte exactement ces clés) :\n"
#     '{\n'
#     '  "titre": "Titre court du scénario",\n'
#     '  "objectifs": ["objectif 1", "objectif 2", "objectif 3"],\n'
#     '  "grandes_lignes": [\n'
#     '    {"etape": 1, "titre": "Titre de l\'étape", "description": "Description concise"},\n'
#     '    ...\n'
#     '  ],\n'
#     '  "procedures_cles": ["procédure 1", "procédure 2"],\n'
#     '  "points_vigilance": ["point 1", "point 2"],\n'
#     '  "resume_oral": "Texte fluide de trois à quatre phrases pour lecture vocale. Pas de listes, pas de symboles."\n'
#     '}\n\n'
#     "Le champ resume_oral doit être lisible à voix haute sans aucun accroc : pas de tirets, "
#     "pas de parenthèses, pas d'abréviations, pas de sigles. Quatre phrases au maximum."
# )

# # Questions-réponses — instructions système
# QA_MAX_TOKENS    = 180          # réduit : force la concision dès la génération
# QA_MAX_SENTENCES = 2            # filet de sécurité appliqué après coup (cf. _enforce_max_sentences)
# QA_SYSTEM = (
#     "Tu es un formateur expert qui aide un apprenant à comprendre un scénario de formation en réalité virtuelle. "
#     "Tu réponds aux questions en t'appuyant exclusivement sur le scénario fourni. "
#     "Réponse impérativement courte : une phrase si possible, deux phrases maximum. "
#     "Va droit à l'information utile. "
#     "Pas de listes, pas de tirets, pas de symboles, aucun mot ou formule de remplissage "
#     "(par exemple : en fait, donc, voilà, eh bien, du coup, en gros, extra). "
#     "Parle directement à l'apprenant, avec chaleur et précision."
# )

# # Appel au modèle de langage — robustesse réseau (standard industriel : retry + backoff)
# LLM_CALL_MAX_RETRIES     = 2     # tentatives supplémentaires après l'essai initial
# LLM_CALL_RETRY_BACKOFF_S = 1.5   # délai de base entre tentatives (croissance linéaire)

# # Locutions de remplissage à éliminer des réponses orales (filet de sécurité post-génération)
# FILLER_PATTERNS_FR = [
#     r"\ben fait\b,?\s*",
#     r"\bdonc\b,?\s*",
#     r"\bvoil[aà]\b,?\s*",
#     r"\beh bien\b,?\s*",
#     r"\bdu coup\b,?\s*",
#     r"\ben gros\b,?\s*",
#     r"\ben quelque sorte\b,?\s*",
#     r"\bpour ainsi dire\b,?\s*",
#     r"\b[aà] vrai dire\b,?\s*",
#     r"\bdisons que\b,?\s*",
#     r"\bil faut savoir que\b,?\s*",
#     r"\bextra\b\s*[!.,]?\s*",
#     r"^\s*alors,?\s*",
# ]


# # ============================================================================
# # Bibliothèque de phrases système
# # ----------------------------------------------------------------------------
# # Chaque entrée regroupe plusieurs formulations d'une même situation récurrente.
# # La fonction pick() tire une variante aléatoire à chaque appel, ce qui réduit
# # sensiblement la fatigue auditive lors de longues sessions.
# #
# # Principes de rédaction appliqués :
# #   - Phrases courtes, musicalité naturelle, rythme parlé
# #   - Pas de sigles ni d'anglicismes difficiles à prononcer
# #   - Pas de virgules superflues (pause TTS mal placée)
# #   - Finales ouvertes ou légèrement montantes (intonation invitante)
# #   - Chaleur professionnelle — ni trop formel ni trop familier
# # ============================================================================

# CACHED_PHRASES_FR: Dict[str, List[str]] = {

#     # Invitation à parler — brève, neutre, non répétitive
#     "listening": [
#         "Je vous écoute.",
#         "À vous.",
#         "Allez-y.",
#         "Je suis prêt.",
#         "La parole est à vous.",
#     ],

#     # Accusé de réception très court
#     "ack_short": [
#         "Bien reçu.",
#         "Compris.",
#         "Noté.",
#         "Entendu.",
#     ],

#     # Attente courte (1 à 3 secondes) — rien de verbal, juste un signal d'ambiance
#     # Ces phrases ne sont pas utilisées directement : le niveau 1 est traité
#     # uniquement par earcon, sans parole, pour ne pas alourdir les courtes attentes.
#     "thinking_short": [
#         "Un instant.",
#         "Je vérifie.",
#     ],

#     # Attente moyenne (3 à 10 secondes) — une phrase rassurante, pas d'explication
#     "thinking_medium": [
#         "Je prépare votre réponse.",
#         "Je consulte le scénario.",
#         "Je rassemble les éléments.",
#         "Je cherche la bonne information.",
#         "Je réfléchis à votre question.",
#     ],

#     # Attente longue (10 à 20 secondes) — on reconnaît que ça prend du temps
#     "thinking_long": [
#         "La question est détaillée, je finalise ma réponse.",
#         "Cela demande un peu plus de réflexion. Je suis sur le sujet.",
#         "Je creuse la question. Encore un court instant.",
#         "Je vérifie tous les éléments. Merci de votre patience.",
#     ],

#     # Attente très longue (au-delà de 20 secondes) — ton calme, pas d'alarme
#     "thinking_very_long": [
#         "Je suis toujours en train de traiter votre demande.",
#         "Le traitement prend un peu plus de temps que prévu. Je reste sur le sujet.",
#         "Toujours en cours. Je reviens vers vous très bientôt.",
#     ],

#     # Relance douce après un premier silence — sans interroger explicitement
#     "soft_nudge": [
#         "Je reste disponible si vous avez une question.",
#         "Prenez votre temps. Je vous écoute quand vous êtes prêt.",
#         "Pas de précipitation. Je suis là.",
#         "Vous pouvez continuer quand vous le souhaitez.",
#     ],

#     # Question explicite après un silence prolongé (oui / non)
#     "no_response_continue_check": [
#         "Je n'entends plus rien. Souhaitez-vous continuer la session ? "
#         "Dites oui pour continuer, ou non pour terminer.",
#         "Il y a un long silence. Voulez-vous poursuivre ? "
#         "Répondez oui ou non.",
#     ],
# }


# def pick(key: str) -> str:
#     """Tire aléatoirement une variante de phrase système pour réduire la répétition."""
#     options = CACHED_PHRASES_FR.get(key)
#     if not options:
#         return ""
#     return random.choice(options)


# # ============================================================================
# # Décision + NarratorSession
# # ============================================================================

# class Decision(Enum):
#     CONTINUER = "CONTINUER"
#     CONSEIL   = "CONSEIL"
#     STOP      = "STOP"


# @dataclass
# class SupervisorDecision:
#     decision: Decision = Decision.CONTINUER
#     message:  str      = ""

#     def must_speak(self) -> bool:
#         return self.decision in (Decision.CONSEIL, Decision.STOP)


# @dataclass
# class NarratorSession:
#     """Accumule la transcription et maintient le contexte pour le superviseur."""
#     topic:     str
#     chunks:    List[str] = field(default_factory=list)
#     full_text: str       = ""

#     def add_chunk(self, text: str) -> None:
#         self.chunks.append(text)
#         self.full_text = " ".join(self.chunks)

#     def context_window(self, n: int = 5) -> str:
#         return " ".join(self.chunks[-n:])

#     def summary(self) -> str:
#         return "%d séquence(s), environ %d mots" % (len(self.chunks), len(self.full_text.split()))


# # ============================================================================
# # PatienceManager — retour sonore pendant les temps de traitement
# # ----------------------------------------------------------------------------
# # Stratégie à paliers calibrée sur la durée d'attente réelle :
# #
# #   Moins de 1 s    : rien (imperceptible)
# #   De 1 à 3 s      : signal d'ambiance discret seul (pas de phrase —
# #                     évite la surcharge verbale sur les attentes courantes)
# #   De 3 à 10 s     : signal d'ambiance + courte phrase de transition
# #   Au-delà de 10 s : signal grave + phrase "longue attente", puis rappel
# #                     toutes les 12 s pour éviter le silence total anxiogène
# #
# # Le suivi tourne dans un fil d'exécution dédié pendant l'appel bloquant
# # au modèle de langage. Il s'arrête proprement (threading.Event) dès que
# # le résultat est disponible.
# # ============================================================================

# class PatienceManager:
#     """Pilote les signaux d'ambiance et les phrases de patience selon la durée réelle d'attente."""

#     LEVEL_SHORT_S     = 1.0    # moins de 1 s : rien
#     LEVEL_MEDIUM_S    = 3.0    # 1 à 3 s : signal seul
#     LEVEL_LONG_S      = 10.0   # 3 à 10 s : signal + phrase courte
#     LEVEL_VERY_LONG_S = 20.0   # au-delà de 10 s : signal grave + phrase longue

#     def __init__(self, io: "VoiceIO") -> None:
#         self.io = io
#         self._stop_event = threading.Event()
#         self._thread: Optional[threading.Thread] = None

#     def start(self) -> None:
#         self._stop_event.clear()
#         self._thread = threading.Thread(target=self._run, daemon=True)
#         self._thread.start()

#     def stop(self) -> None:
#         self._stop_event.set()
#         if self._thread is not None:
#             self._thread.join(timeout=2.0)
#             self._thread = None

#     def _run(self) -> None:
#         start = time.monotonic()
#         announced_medium    = False
#         announced_long      = False
#         announced_very_long = False

#         while not self._stop_event.is_set():
#             elapsed = time.monotonic() - start

#             if elapsed >= self.LEVEL_MEDIUM_S and not announced_medium:
#                 announced_medium = True
#                 self.io.play_earcon("patience_short")

#             if elapsed >= self.LEVEL_LONG_S and not announced_long:
#                 announced_long = True
#                 self.io.play_earcon("patience_medium")
#                 self.io.speak(pick("thinking_medium"), blocking=False)

#             if elapsed >= self.LEVEL_VERY_LONG_S and not announced_very_long:
#                 announced_very_long = True
#                 self.io.play_earcon("patience_long")
#                 self.io.speak(pick("thinking_long"), blocking=False)

#             # Rappel périodique au-delà du seuil très long
#             if announced_very_long and elapsed >= self.LEVEL_VERY_LONG_S + 12.0:
#                 self.io.speak(pick("thinking_very_long"), blocking=False)
#                 start += 12.0  # reprogramme le prochain rappel dans 12 s
#                 # (avancer start recule elapsed d'autant ; le signe inverse
#                 # ferait remonter elapsed et redéclencherait la phrase en boucle)

#             self._stop_event.wait(timeout=0.25)

#     def run_with_patience(self, fn, *args, **kwargs):
#         """Exécute fn(*args, **kwargs) en pilotant le retour sonore de patience."""
#         self.start()
#         try:
#             return fn(*args, **kwargs)
#         finally:
#             self.stop()


# # ============================================================================
# # SupervisorLLM
# # ============================================================================

# class SupervisorLLM:
#     """Analyse les fragments de narration et produit des décisions de supervision."""

#     def __init__(self, config) -> None:
#         self._config = config
#         self._lock   = threading.Lock()

#     def analyse(self, session: NarratorSession, new_chunk: str) -> SupervisorDecision:
#         if self._config is None:
#             return SupervisorDecision()

#         user_msg = (
#             "Thème du scénario : %s\n\n"
#             "Contexte (narration précédente) :\n%s\n\n"
#             "Nouveau fragment :\n%s"
#         ) % (session.topic, session.context_window(), new_chunk)

#         try:
#             with self._lock:
#                 raw = self._call_llm(user_msg)
#             return self._parse(raw)
#         except Exception as exc:
#             logger.warning("SupervisorLLM erreur : %s", exc)
#             return SupervisorDecision()

#     def _call_llm(self, user_msg: str) -> str:
#         # Tentative via la bibliothèque de scénarios
#         try:
#             from vr_scenario_lib.llm import call_llm
#             return call_llm(
#                 system=SUPERVISOR_SYSTEM,
#                 user=user_msg,
#                 llm_config=self._config,
#                 max_tokens=SUPERVISOR_MAX_TOKENS,
#             )
#         except ImportError:
#             pass
#         except TypeError as exc:
#             # La bibliothèque est présente mais son interface ne correspond pas
#             # à l'appel attendu (signature différente) : on bascule sur l'appel
#             # HTTP direct plutôt que de laisser l'erreur désactiver le superviseur.
#             logger.debug("call_llm (bibliothèque) signature incompatible : %s — appel direct", exc)

#         # Appel direct compatible avec l'interface de l'API de langage
#         import json
#         import urllib.request

#         payload = json.dumps({
#             "model":      getattr(self._config, "model", "gpt-3.5-turbo"),
#             "max_tokens": SUPERVISOR_MAX_TOKENS,
#             "messages":   [
#                 {"role": "system", "content": SUPERVISOR_SYSTEM},
#                 {"role": "user",   "content": user_msg},
#             ],
#         }).encode()
#         api_url = getattr(self._config, "api_url", "https://api.openai.com/v1/chat/completions")
#         token   = getattr(self._config, "token", "")
#         req = urllib.request.Request(
#             api_url,
#             data=payload,
#             headers={
#                 "Content-Type":  "application/json",
#                 "Authorization": "Bearer " + token,
#             },
#         )
#         with urllib.request.urlopen(req, timeout=15) as resp:
#             data = json.loads(resp.read())
#         return data["choices"][0]["message"]["content"]

#     def _parse(self, raw: str) -> SupervisorDecision:
#         import json
#         import re
#         m = re.search(r'\{.*\}', raw, re.DOTALL)
#         if not m:
#             logger.warning("SupervisorLLM : structure JSON introuvable dans '%s'", raw[:120])
#             return SupervisorDecision()
#         obj = json.loads(m.group())
#         try:
#             dec = Decision(obj.get("decision", "CONTINUER").upper())
#         except ValueError:
#             dec = Decision.CONTINUER
#         return SupervisorDecision(decision=dec, message=obj.get("message", "").strip())


# # ============================================================================
# # VoiceIO
# # ============================================================================

# class VoiceIO:
#     """Couche basse — reconnaissance vocale et synthèse vocale.

#     Principes fondamentaux
#     ----------------------
#     1. speak() est TOUJOURS bloquant dans le fil principal.
#        Une synthèse non bloquante avant écoute = écho capturé par le moteur de
#        reconnaissance.
#     2. Le microphone n'est jamais ouvert pendant la synthèse vocale.
#     3. L'enregistrement utilise la détection automatique de voix, pas une durée fixe.
#     4. interrupt_and_speak() coupe l'audio en cours avant de parler (alertes STOP).
#     5. play_earcon() est toujours non bloquant et très court (moins de 400 ms) :
#        il ne doit jamais retarder le flux conversationnel.
#     """

#     def __init__(
#         self,
#         stt_backend:   str = "whisper",
#         tts_backend:   str = TTS_DEFAULT_BACKEND,
#         language:      str = "fr",
#         whisper_model: str = WHISPER_DEFAULT_MODEL,
#         coqui_model:   str = COQUI_MODEL_FR,
#         piper_model:   str = PIPER_MODEL_FR,
#     ) -> None:
#         self.stt_backend      = stt_backend
#         self.tts_backend      = tts_backend
#         self.language         = language
#         self.whisper_model_id = whisper_model
#         self.coqui_model_id   = coqui_model
#         self.piper_model_id   = piper_model

#         self._recognizer    = None
#         self._whisper_model = None
#         self._tts_engine    = None
#         self._coqui_model   = None
#         self._lock_tts      = threading.Lock()

#         self._init()

#     # ------------------------------------------------------------------
#     # Initialisation
#     # ------------------------------------------------------------------

#     def _init(self) -> None:
#         self._init_stt()
#         self._init_tts()
#         logger.info(
#             "VoiceIO prêt — Reconnaissance : %s | Synthèse : %s | Langue : %s",
#             self.stt_backend, self.tts_backend, self.language,
#         )

#     def _init_stt(self) -> None:
#         try:
#             import speech_recognition as sr
#             self._recognizer = sr.Recognizer()
#             self._recognizer.energy_threshold         = 4000
#             self._recognizer.pause_threshold          = STT_SILENCE_TIMEOUT
#             self._recognizer.dynamic_energy_threshold = True
#         except ImportError:
#             raise RuntimeError(
#                 "Module SpeechRecognition manquant. "
#                 "Installez-le avec : pip install SpeechRecognition PyAudio"
#             )
#         if self.stt_backend == "whisper":
#             self._whisper_model = self._load_whisper()

#     def _load_whisper(self) -> object:
#         try:
#             from faster_whisper import WhisperModel
#             logger.info("Chargement du modèle Faster Whisper '%s'...", self.whisper_model_id)
#             model = WhisperModel(
#                 self.whisper_model_id,
#                 device="cpu",
#                 compute_type="int8",
#             )
#             logger.info("Faster Whisper prêt")
#             return model
#         except ImportError:
#             raise RuntimeError(
#                 "Module faster-whisper manquant. Installez-le avec : pip install faster-whisper"
#             )

#     def _init_tts(self) -> None:
#         chain = (
#             [self.tts_backend]
#             + [b for b in TTS_FALLBACK_CHAIN if b != self.tts_backend]
#         )
#         for backend in chain:
#             try:
#                 if backend == "coqui":
#                     self._init_coqui()
#                 elif backend == "piper":
#                     self._init_piper()
#                 elif backend == "gtts":
#                     self._init_gtts()
#                 elif backend == "pyttsx3":
#                     self._init_pyttsx3()
#                 else:
#                     continue
#                 self.tts_backend = backend
#                 logger.info("Moteur de synthèse actif : %s", backend)
#                 return
#             except Exception as exc:
#                 logger.warning(
#                     "Moteur '%s' indisponible : %s — essai du suivant", backend, exc
#                 )

#         raise RuntimeError(
#             "Aucun moteur de synthèse vocale disponible. "
#             "Installez au minimum : pip install coqui-tts sounddevice soundfile"
#         )

#     # ------------------------------------------------------------------
#     # Initialisation Coqui VITS — voix neurale française hors ligne
#     # ------------------------------------------------------------------

#     def _init_coqui(self) -> None:
#         try:
#             from TTS.api import TTS as CoquiTTS
#             import sounddevice  # noqa: F401
#             import soundfile    # noqa: F401
#         except ImportError:
#             raise RuntimeError(
#                 "Module Coqui manquant. Installez-le avec : pip install coqui-tts sounddevice soundfile"
#             )
#         logger.info("Chargement de Coqui '%s'...", self.coqui_model_id)
#         self._coqui_model = CoquiTTS(
#             model_name=self.coqui_model_id,
#             progress_bar=False,
#             gpu=False,
#         )
#         logger.info("Coqui prêt")

#     # ------------------------------------------------------------------
#     # Initialisation Piper — voix neurale française hors ligne, très rapide
#     # ------------------------------------------------------------------

#     def _init_piper(self) -> None:
#         try:
#             import piper  # noqa: F401
#         except ImportError:
#             raise RuntimeError("Module piper-tts manquant. Installez-le avec : pip install piper-tts")
#         logger.info("Piper disponible — modèle '%s'", self.piper_model_id)

#     # ------------------------------------------------------------------
#     # Initialisation Google Synthèse vocale — en ligne
#     # ------------------------------------------------------------------

#     def _init_gtts(self) -> None:
#         try:
#             import gtts    # noqa: F401
#             import pygame  # noqa: F401
#         except ImportError:
#             raise RuntimeError(
#                 "Modules gTTS ou pygame manquants. Installez-les avec : pip install gTTS pygame"
#             )
#         logger.info("Google Synthèse vocale initialisée")

#     # ------------------------------------------------------------------
#     # Initialisation pyttsx3 — solution de secours ultime
#     # ------------------------------------------------------------------

#     def _init_pyttsx3(self) -> None:
#         try:
#             import pyttsx3
#         except ImportError:
#             raise RuntimeError(
#                 "Module pyttsx3 manquant. Installez-le avec : pip install pyttsx3"
#             )

#         engine = pyttsx3.init()
#         engine.setProperty("rate",   TTS_SPEECH_RATE)
#         engine.setProperty("volume", TTS_VOLUME)

#         fr_voice_found = False
#         # Priorité 1 : voix fr_FR espeak-ng (accent français métropolitain)
#         # Priorité 2 : toute voix contenant "french" ou "fr" dans le nom ou l'identifiant
#         for priority in ("fr_FR", "fr-FR", "french", "fr"):
#             for v in engine.getProperty("voices"):
#                 name_lower = v.name.lower()
#                 id_lower   = v.id.lower()
#                 if priority.lower() in id_lower or priority.lower() in name_lower:
#                     engine.setProperty("voice", v.id)
#                     logger.info(
#                         "pyttsx3 : voix française sélectionnée : %s (%s)", v.name, v.id
#                     )
#                     fr_voice_found = True
#                     break
#             if fr_voice_found:
#                 break

#         if not fr_voice_found:
#             logger.warning(
#                 "Aucune voix française trouvée dans pyttsx3. "
#                 "Sur Linux : sudo apt install espeak-ng-data"
#             )

#         self._tts_engine = engine
#         logger.info("pyttsx3 initialisé (voix système)")

#     # ------------------------------------------------------------------
#     # Synthèse vocale — TOUJOURS bloquante dans le fil principal
#     # ------------------------------------------------------------------

#     def interrupt_and_speak(self, text: str) -> None:
#         """Coupe l'audio en cours PUIS parle. Réservé aux alertes STOP urgentes."""
#         self._stop_audio()
#         self.speak(text)

#     def _stop_audio(self) -> None:
#         """Arrête immédiatement la lecture audio (tous moteurs)."""
#         try:
#             if self.tts_backend in ("coqui", "piper"):
#                 import sounddevice as sd
#                 sd.stop()
#             elif self.tts_backend == "gtts":
#                 try:
#                     import pygame
#                     if pygame.mixer.get_init():
#                         pygame.mixer.music.stop()
#                 except Exception:
#                     pass
#         except Exception as exc:
#             logger.debug("_stop_audio : %s", exc)

#     @staticmethod
#     def _sanitize_tts(text: str) -> str:
#         """Nettoie le texte avant synthèse vocale.

#         Transformations appliquées dans l'ordre :
#         1. Blocs de code Markdown (``` … ```) → supprimés
#         2. Emphase Markdown (* ** _ __ ~ ~~)  → supprimée (le texte reste)
#         3. Titres Markdown (# ## ###…)         → supprimés (le texte reste)
#         4. Adresses web (http / https / ftp)   → remplacées par « lien »
#         5. Ponctuation non orale               → remplacée ou supprimée
#         6. Espaces multiples et lignes vides   → normalisés
#         7. Mots de remplissage (donc, voilà, extra…) → supprimés, avec
#            vérification de rendu : si le nettoyage efface tout le texte
#            (sur-correction), on prononce l'original plutôt que de rester muet.
#         """
#         import re

#         # 1. Blocs de code (``` … ```) et code en ligne (` … `)
#         text = re.sub(r'```.*?```', '', text, flags=re.DOTALL)
#         text = re.sub(r'`[^`]*`', '', text)

#         # 2. Emphase Markdown
#         text = re.sub(r'\*{1,3}|_{1,3}|~{1,2}', '', text)

#         # 3. Titres Markdown en début de ligne
#         text = re.sub(r'^\s*#{1,6}\s*', '', text, flags=re.MULTILINE)

#         # 4. Adresses web
#         text = re.sub(r'https?://\S+|ftp://\S+', 'lien', text)

#         # 5. Ponctuation non orale
#         text = re.sub(r'^\s*[-•–—]\s+', '', text, flags=re.MULTILINE)
#         text = re.sub(r'^\s*[\-|: ]{3,}\s*$', '', text, flags=re.MULTILINE)
#         text = re.sub(r'\|', ' ', text)
#         text = re.sub(r'[\\/@#$%^&{}\[\]<>=]', ' ', text)
#         text = re.sub(r'[(){}\[\]]', ' ', text)
#         text = re.sub(r'\.{2,}', ',', text)
#         text = re.sub(r'\s*[–—]\s*', ', ', text)
#         text = re.sub(r'\*+', '', text)
#         text = re.sub(r'_+', ' ', text)

#         # 6. Normalisation des espaces et des sauts de ligne
#         text = re.sub(r'\n+', ' ', text)
#         text = re.sub(r' {2,}', ' ', text)
#         text = text.strip()

#         # 7. Mots de remplissage (cf. FILLER_PATTERNS_FR) — appliqué ici pour
#         # couvrir TOUTE synthèse vocale (accueil, scénario, alertes du
#         # superviseur), pas seulement les réponses Q&R déjà nettoyées en amont.
#         cleaned = text
#         for pattern in FILLER_PATTERNS_FR:
#             cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE | re.MULTILINE)
#         cleaned = re.sub(r' {2,}', ' ', cleaned).strip()
#         cleaned = re.sub(r'^[,.]\s*', '', cleaned)
#         if cleaned and cleaned[0].islower():
#             cleaned = cleaned[0].upper() + cleaned[1:]
#         if cleaned:
#             text = cleaned
#         # sinon : le filtre a tout effacé (sur-correction) — on garde
#         # l'original plutôt que de prononcer une phrase vide.

#         return text.strip()

#     def speak(self, text: str, *, blocking: bool = True) -> None:
#         """Synthèse vocale en français natif.

#         blocking=True (par défaut) : retourne APRÈS la fin de la lecture.
#         blocking=False             : usage exceptionnel uniquement —
#                                      par exemple, phrases de patience émises
#                                      par PatienceManager pendant qu'un autre fil
#                                      attend le modèle de langage. Dans ce cas,
#                                      le microphone n'est pas sollicité en parallèle,
#                                      donc pas de risque d'écho capturé.
#         RÈGLE : ne JAMAIS appeler avec blocking=False juste avant écoute().
#         """
#         if not text or not text.strip():
#             return
#         text = self._sanitize_tts(text)
#         if not text:
#             return
#         logger.info("Synthèse [%s] : '%s'", self.tts_backend, text[:80])

#         dispatch = {
#             "coqui":   self._speak_coqui,
#             "piper":   self._speak_piper,
#             "gtts":    self._speak_gtts,
#             "pyttsx3": self._speak_pyttsx3,
#         }
#         fn = dispatch.get(self.tts_backend)
#         if fn is None:
#             logger.error("Moteur de synthèse inconnu : %s", self.tts_backend)
#             print("[Synthèse] " + text)
#             return
#         fn(text, blocking)

#     # ------------------------------------------------------------------
#     # Signaux d'ambiance — retour sonore court pendant les attentes
#     # ------------------------------------------------------------------
#     # Générés à la volée (sinusoïdes), aucune dépendance audio externe
#     # supplémentaire au-delà de sounddevice (déjà requis par coqui/piper).
#     # En cas d'indisponibilité : dégradation silencieuse, sans exception
#     # propagée ni affichage parasite — un signal manqué ne doit jamais
#     # bloquer le flux conversationnel.
#     # ------------------------------------------------------------------

#     _EARCON_PROFILES = {
#         # (fréquence Hz, durée s, amplitude) — profils courts et discrets
#         "patience_short":  (880.0, 0.10, 0.15),   # signal discret, attente courte
#         "patience_medium": (660.0, 0.15, 0.18),   # signal intermédiaire
#         "patience_long":   (440.0, 0.22, 0.20),   # signal grave, longue attente
#     }

#     def play_earcon(self, profile: str) -> None:
#         """Joue un signal d'ambiance court et non bloquant. Échec silencieux."""
#         params = self._EARCON_PROFILES.get(profile)
#         if params is None:
#             return
#         try:
#             threading.Thread(
#                 target=self._play_earcon_sync, args=(params,), daemon=True
#             ).start()
#         except Exception as exc:
#             logger.debug("play_earcon : %s", exc)

#     def _play_earcon_sync(self, params) -> None:
#         freq, duration, amplitude = params
#         try:
#             import sounddevice as sd
#             sample_rate = 22050
#             n_samples = int(sample_rate * duration)
#             tone = [
#                 amplitude * math.sin(2 * math.pi * freq * (i / sample_rate))
#                 for i in range(n_samples)
#             ]
#             sd.play(tone, sample_rate)
#             sd.wait()
#         except Exception as exc:
#             logger.debug("Signal d'ambiance indisponible (%s), ignoré", exc)

#     # ------------------------------------------------------------------
#     # Moteur Coqui — référence qualité
#     # ------------------------------------------------------------------

#     def _speak_coqui(self, text: str, blocking: bool) -> None:
#         """Synthèse Coqui (réseau de neurones) + lecture sounddevice.

#         La lecture est sérialisée via self._lock_tts pendant toute sa durée
#         réelle (y compris en non bloquant, via un fil dédié) : sans cela, un
#         appel concurrent peut démarrer une nouvelle lecture sur le flux audio
#         par défaut avant la fin de la précédente, qui est alors coupée net.
#         """
#         tmp_path: Optional[str] = None
#         try:
#             import soundfile as sf
#             import sounddevice as sd

#             with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
#                 tmp_path = f.name

#             with self._lock_tts:
#                 self._coqui_model.tts_to_file(text=text, file_path=tmp_path)

#             data, sr = sf.read(tmp_path, dtype="float32")

#             def _play() -> None:
#                 with self._lock_tts:
#                     sd.play(data, sr)
#                     sd.wait()

#             if blocking:
#                 _play()
#             else:
#                 threading.Thread(target=_play, daemon=True).start()

#         except Exception as exc:
#             logger.error("Coqui erreur : %s", exc)
#             print("[Synthèse] " + text)
#         finally:
#             if tmp_path and os.path.exists(tmp_path):
#                 try:
#                     os.unlink(tmp_path)
#                 except OSError:
#                     pass

#     # ------------------------------------------------------------------
#     # Moteur Piper — latence minimale
#     # ------------------------------------------------------------------

#     def _speak_piper(self, text: str, blocking: bool) -> None:
#         """Synthèse Piper (CLI externe) + lecture sounddevice.

#         Lecture sérialisée via self._lock_tts pour toute sa durée réelle
#         (cf. _speak_coqui) afin qu'un appel concurrent ne coupe pas une
#         phrase en cours de diffusion.
#         """
#         tmp_path: Optional[str] = None
#         try:
#             import subprocess
#             import soundfile as sf
#             import sounddevice as sd

#             with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
#                 tmp_path = f.name

#             result = subprocess.run(
#                 ["piper", "--model", self.piper_model_id, "--output_file", tmp_path],
#                 input=text.encode("utf-8"),
#                 capture_output=True,
#                 timeout=30,
#             )
#             if result.returncode != 0:
#                 raise RuntimeError(
#                     "piper code de retour=%d : %s" % (
#                         result.returncode, result.stderr.decode()
#                     )
#                 )

#             data, sr = sf.read(tmp_path, dtype="float32")

#             def _play() -> None:
#                 with self._lock_tts:
#                     sd.play(data, sr)
#                     sd.wait()

#             if blocking:
#                 _play()
#             else:
#                 threading.Thread(target=_play, daemon=True).start()

#         except FileNotFoundError:
#             logger.error("Exécutable 'piper' introuvable. pip install piper-tts")
#             print("[Synthèse] " + text)
#         except Exception as exc:
#             logger.error("Piper erreur : %s", exc)
#             print("[Synthèse] " + text)
#         finally:
#             if tmp_path and os.path.exists(tmp_path):
#                 try:
#                     os.unlink(tmp_path)
#                 except OSError:
#                     pass

#     # ------------------------------------------------------------------
#     # Moteur Google Synthèse vocale — en ligne
#     # ------------------------------------------------------------------

#     def _speak_gtts(self, text: str, blocking: bool) -> None:
#         """Synthèse Google (gTTS) + lecture pygame.

#         Robustesse :
#         - Toute lecture (bloquante ou non) est sérialisée via self._lock_tts.
#           Sans ce verrou, un appel concurrent (fil principal pendant que
#           PatienceManager parle encore, ou deux rappels de patience rapprochés)
#           réinitialise le mixeur en pleine lecture — la phrase précédente est
#           coupée net.
#         - Le fichier temporaire n'est supprimé qu'après la fin RÉELLE de la
#           lecture (boucle get_busy()), jamais après un simple délai fixe :
#           un délai fixe trop court coupait l'audio en cours de diffusion.
#         """
#         def _play_and_cleanup() -> None:
#             tmp_path: Optional[str] = None
#             try:
#                 from gtts import gTTS
#                 import pygame

#                 tts = gTTS(text=text, lang=self.language, slow=False)
#                 with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
#                     tmp_path = f.name
#                 tts.save(tmp_path)

#                 with self._lock_tts:
#                     if pygame.mixer.get_init():
#                         pygame.mixer.quit()
#                     pygame.mixer.init(frequency=22050, size=-16, channels=1, buffer=512)
#                     pygame.mixer.music.load(tmp_path)
#                     pygame.mixer.music.play()
#                     while pygame.mixer.music.get_busy():
#                         time.sleep(0.05)
#                     pygame.mixer.quit()

#             except Exception as exc:
#                 logger.error("Google Synthèse vocale erreur : %s", exc)
#                 print("[Synthèse] " + text)
#             finally:
#                 if tmp_path and os.path.exists(tmp_path):
#                     try:
#                         os.unlink(tmp_path)
#                     except OSError:
#                         pass

#         if blocking:
#             _play_and_cleanup()
#         else:
#             threading.Thread(target=_play_and_cleanup, daemon=True).start()

#     # ------------------------------------------------------------------
#     # Moteur pyttsx3 — solution de secours ultime
#     # ------------------------------------------------------------------

#     def _speak_pyttsx3(self, text: str, blocking: bool) -> None:
#         """Synthèse pyttsx3 (solution de secours ultime).

#         Le verrou est tenu pendant toute la durée réelle de runAndWait(),
#         y compris en non bloquant (via un fil dédié) : le moteur pyttsx3
#         n'est pas conçu pour des appels concurrents, et libérer le verrou
#         avant la fin de la lecture exposait à des phrases tronquées ou
#         entremêlées lors d'un appel suivant rapproché.
#         """
#         def _say_and_wait() -> None:
#             with self._lock_tts:
#                 try:
#                     self._tts_engine.say(text)
#                     self._tts_engine.runAndWait()
#                 except Exception as exc:
#                     logger.error("pyttsx3 erreur : %s", exc)
#                     print("[Synthèse] " + text)

#         if blocking:
#             _say_and_wait()
#         else:
#             threading.Thread(target=_say_and_wait, daemon=True).start()

#     # ------------------------------------------------------------------
#     # Reconnaissance vocale — fragment avec détection automatique de voix
#     # ------------------------------------------------------------------

#     def listen_chunk(
#         self,
#         *,
#         pause_threshold:   float = STT_SILENCE_TIMEOUT,
#         phrase_time_limit: int   = STT_PHRASE_TIME_LIMIT,
#         listen_timeout:    float = STT_LISTEN_TIMEOUT,
#         initial_prompt:    Optional[str] = None,
#     ) -> str:
#         """Capture un fragment de parole et le transcrit.

#         initial_prompt (Whisper uniquement) : biais lexical optionnel pour
#         orienter la transcription vers un vocabulaire attendu (ex. thèmes
#         techniques courts, sans contexte de phrase). Ignoré sur le moteur Google.

#         Retourne :
#             Le texte transcrit (non vide).

#         Lève :
#             RuntimeError si la capture ou la transcription échoue,
#             ou si aucune voix n'est détectée dans le délai imparti.
#         """
#         import speech_recognition as sr

#         original = self._recognizer.pause_threshold
#         self._recognizer.pause_threshold = pause_threshold
#         tmp_path: Optional[str] = None

#         try:
#             with sr.Microphone() as src:
#                 logger.info(
#                     "Écoute (silence=%.1fs, max=%ds)...",
#                     pause_threshold, phrase_time_limit,
#                 )
#                 self._recognizer.adjust_for_ambient_noise(src, duration=STT_AMBIENT_DURATION)
#                 audio = self._recognizer.listen(
#                     src,
#                     timeout=listen_timeout,
#                     phrase_time_limit=phrase_time_limit,
#                 )

#             with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
#                 tmp_path = f.name
#                 f.write(audio.get_wav_data())

#             if self.stt_backend == "whisper":
#                 return self._transcribe_whisper(tmp_path, initial_prompt=initial_prompt)
#             else:
#                 return self._transcribe_google(audio)

#         except sr.WaitTimeoutError as exc:
#             raise RuntimeError("Aucune voix détectée dans le délai imparti") from exc

#         finally:
#             self._recognizer.pause_threshold = original
#             if tmp_path and os.path.exists(tmp_path):
#                 try:
#                     os.unlink(tmp_path)
#                 except OSError:
#                     pass

#     def listen_short(self, question: str, timeout: float = 8.0, initial_prompt: Optional[str] = None) -> str:
#         """Pose une question brève et attend une réponse courte.
#         Retourne une chaîne vide en cas d'absence de réponse (aucune exception propagée).

#         Utilise les mêmes seuils d'écoute que la boucle de questions-réponses
#         (déjà fiables en usage réel) plutôt que des seuils plus courts : un silence
#         de coupure trop bref clipe une prononciation hésitante (thème technique,
#         mot inhabituel) ou un simple "oui" arrivant juste après la synthèse vocale.

#         initial_prompt : transmis à Whisper pour biaiser la reconnaissance vers
#         un vocabulaire attendu (cf. listen_chunk).
#         """
#         self.speak(question)
#         self.speak(pick("listening"))
#         time.sleep(TTS_TO_STT_SETTLE_S)  # laisse l'écho de la synthèse se dissiper avant calibration du micro
#         try:
#             return self.listen_chunk(
#                 pause_threshold=STT_SILENCE_TIMEOUT,
#                 phrase_time_limit=STT_PHRASE_TIME_LIMIT,
#                 listen_timeout=timeout,
#                 initial_prompt=initial_prompt,
#             )
#         except RuntimeError as exc:
#             logger.info("listen_short : aucune réponse (%s)", exc)
#             return ""

#     def _transcribe_whisper(self, wav_path: str, initial_prompt: Optional[str] = None) -> str:
#         try:
#             segments_gen, info = self._whisper_model.transcribe(
#                 wav_path,
#                 language=self.language,
#                 beam_size=WHISPER_BEAM_SIZE,
#                 initial_prompt=initial_prompt,
#             )
#         except TypeError:
#             # Repli : version de faster-whisper ne supportant pas initial_prompt
#             logger.debug(
#                 "Whisper : 'initial_prompt' non supporté par cette version, "
#                 "repli sans biais lexical"
#             )
#             segments_gen, info = self._whisper_model.transcribe(
#                 wav_path,
#                 language=self.language,
#                 beam_size=WHISPER_BEAM_SIZE,
#             )
#         logger.debug(
#             "Whisper : langue=%s (%.0f%%)",
#             info.language, info.language_probability * 100,
#         )
#         text = " ".join(seg.text.strip() for seg in segments_gen).strip()
#         if not text:
#             raise RuntimeError("La reconnaissance vocale n'a produit aucun texte")
#         logger.info("Fragment reconnu : '%s'", text[:100])
#         return text

#     def _transcribe_google(self, audio) -> str:
#         import speech_recognition as sr
#         lang = "fr-FR" if self.language == "fr" else (self.language + "-" + self.language.upper())
#         try:
#             text = self._recognizer.recognize_google(audio, language=lang)
#             logger.info("Reconnaissance Google : '%s'", text[:100])
#             return text
#         except sr.UnknownValueError:
#             raise RuntimeError("Reconnaissance Google : audio incompréhensible")
#         except sr.RequestError as exc:
#             raise RuntimeError("Reconnaissance Google : erreur de service : %s" % exc)

#     # ------------------------------------------------------------------
#     # Nettoyage
#     # ------------------------------------------------------------------

#     def close(self) -> None:
#         self._stop_audio()
#         if self._tts_engine is not None:
#             try:
#                 with self._lock_tts:
#                     self._tts_engine.stop()
#             except Exception:
#                 pass
#         logger.info("VoiceIO fermé")


# # ============================================================================
# # VRScenarioApp — orchestration principale
# # ============================================================================

# class VRScenarioApp:
#     """
#     Flux en deux phases :

#     PHASE 1 — Génération et présentation du scénario
#       - Saisie vocale du thème
#       - Le modèle de langage génère un scénario structuré
#       - Construction de la session de scénario
#       - Lecture du résumé oral par synthèse vocale

#     PHASE 2 — Questions et réponses supervisées
#       - L'utilisateur pose librement ses questions à voix haute
#       - Le modèle répond en s'appuyant sur le scénario généré
#       - Le superviseur évalue chaque échange : CONTINUER / CONSEIL / STOP
#       - Un mot de sortie clôt proprement la session

#     Gestion de la patience
#     ----------------------
#     Toute attente potentiellement longue (génération de scénario, appel
#     au modèle en questions-réponses) est encadrée par PatienceManager,
#     qui pilote automatiquement les signaux d'ambiance et les phrases de
#     transition selon la durée réelle d'attente.
#     """

#     def __init__(self, io: VoiceIO) -> None:
#         self.io = io
#         self.patience = PatienceManager(io)

#     def run(self) -> None:
#         self._welcome()
#         topic      = self._ask_topic()
#         config     = self._setup_llm()
#         supervisor = SupervisorLLM(config)

#         # -- Phase 1 : génération et présentation -------------------------
#         scenario_session = self._generate_and_announce(topic, config)

#         # -- Phase 2 : questions-réponses supervisées ---------------------
#         self._qa_loop(scenario_session, supervisor, config)

#         self._goodbye()

#     # ------------------------------------------------------------------
#     # Phase 1 : génération du scénario
#     # ------------------------------------------------------------------

#     def _welcome(self) -> None:
#         print("\n" + "=" * 60)
#         print("  APPLICATION VOCALE — SCÉNARIOS DE FORMATION EN RÉALITÉ VIRTUELLE")
#         print("=" * 60)
#         self.io.speak(
#             "Bienvenue dans votre assistant vocal de scénarios de formation. "
#             "Je vais générer un scénario à partir du thème que vous me donnerez, "
#             "vous en présenter les grandes lignes, "
#             "puis répondre à vos questions. "
#             "Dites terminer à tout moment pour clore la session."
#         )

#     def _ask_topic(self) -> str:
#         """Capture le thème par la voix avec confirmation orale explicite.

#         La reconnaissance vocale peut mal comprendre le thème prononcé
#         (homophones, bruit ambiant, accent). Générer un scénario complet sur
#         un thème erroné coûte cher en temps et en confiance utilisateur :
#         on confirme donc systématiquement avant de poursuivre.

#         Stratégie :
#           1. Capture du thème (écoute courte, déjà tolérante au silence).
#           2. Confirmation orale explicite ("Le thème retenu est X, correct ?").
#           3. Nouvelle tentative si infirmé, absent ou ambigu — jusqu'à
#              TOPIC_MAX_ATTEMPTS.
#           4. Repli sur un thème par défaut si aucune confirmation n'est obtenue
#              (dégradation silencieuse : la session continue malgré tout).

#         Toute erreur inattendue de la couche vocale (microphone, moteur STT)
#         est absorbée localement : un échec de capture du thème ne doit jamais
#         interrompre la session.
#         """
#         prompt = (
#             "Sur quel thème souhaitez-vous travailler ? "
#             "Vous pouvez me dire, par exemple : la consignation gaz, "
#             "la sécurité incendie, ou les premiers secours."
#         )
#         for attempt in range(1, TOPIC_MAX_ATTEMPTS + 1):
#             try:
#                 text = self.io.listen_short(prompt, initial_prompt=WHISPER_TOPIC_PROMPT)
#             except Exception as exc:
#                 logger.warning(
#                     "Capture du thème échouée (tentative %d/%d) : %s",
#                     attempt, TOPIC_MAX_ATTEMPTS, exc,
#                 )
#                 text = ""

#             if text and self._confirm_topic(text):
#                 self.io.speak("Très bien. Le thème retenu est : " + text + ".")
#                 logger.info("Thème confirmé : '%s'", text)
#                 print("\nThème : " + text)
#                 return text

#             logger.info(
#                 "Thème non confirmé (tentative %d/%d) : '%s'",
#                 attempt, TOPIC_MAX_ATTEMPTS, text,
#             )
#             if attempt < TOPIC_MAX_ATTEMPTS:
#                 prompt = "Je vous écoute à nouveau. Quel est le thème souhaité ?"
#                 self.io.speak("D'accord, reprenons.")

#         text = "sécurité industrielle"
#         self.io.speak(
#             "Je n'arrive pas à confirmer le thème. "
#             "Je vais utiliser la sécurité industrielle par défaut."
#         )
#         logger.info("Thème : repli par défaut '%s'", text)
#         print("\nThème : " + text)
#         return text

#     def _confirm_topic(self, topic: str) -> bool:
#         """Demande une confirmation orale explicite du thème compris.

#         Un "oui"/"non" isolé est plus difficile à transcrire correctement qu'une
#         phrase complète (peu de contexte pour le modèle de reconnaissance). On
#         retente donc la question de confirmation elle-même, jusqu'à
#         TOPIC_CONFIRM_MAX_ATTEMPTS fois, avant de conclure à une non-confirmation —
#         plutôt que de forcer l'utilisateur à reprononcer tout le thème pour un
#         simple aléa de reconnaissance sur "oui".
#         """
#         question = "Le thème retenu est : " + topic + ". Est-ce correct ? Dites oui ou non."
#         for attempt in range(1, TOPIC_CONFIRM_MAX_ATTEMPTS + 1):
#             try:
#                 answer = self.io.listen_short(question, initial_prompt=WHISPER_YESNO_PROMPT).lower()
#             except Exception as exc:
#                 logger.debug(
#                     "_confirm_topic (tentative %d/%d) : %s",
#                     attempt, TOPIC_CONFIRM_MAX_ATTEMPTS, exc,
#                 )
#                 answer = ""

#             if any(w in answer for w in TOPIC_CONFIRM_NO):
#                 return False
#             if any(w in answer for w in TOPIC_CONFIRM_YES):
#                 return True

#             if attempt < TOPIC_CONFIRM_MAX_ATTEMPTS:
#                 question = "Je n'ai pas compris. Dites simplement oui, ou non."

#         return False

#     def _generate_and_announce(self, topic: str, config) -> "ScenarioSession | None":
#         """
#         Appelle le modèle pour générer le scénario, construit la session,
#         et lit le résumé oral.
#         Retourne None si la génération échoue (les questions-réponses restent possibles).

#         La génération peut prendre plusieurs secondes. Elle est encadrée par
#         PatienceManager qui gère automatiquement les signaux d'ambiance et
#         les phrases de transition selon la durée réelle d'attente.
#         """
#         print("\nGénération du scénario en cours…")

#         scenario_json: Dict[str, Any] = {}
#         scenario_text: str = ""

#         def _do_generate():
#             nonlocal scenario_text, scenario_json
#             try:
#                 from vr_scenario_lib.scenario import generate_scenario as lib_generate
#                 result = lib_generate(topic=topic, llm_config=config)
#                 if isinstance(result, tuple):
#                     scenario_text, scenario_json = result[0], result[1]
#                 else:
#                     scenario_text = getattr(result, "text", str(result))
#                     scenario_json = getattr(result, "json", {})
#                 logger.info(
#                     "Scénario généré via la bibliothèque (%d caractères)", len(scenario_text)
#                 )
#             except Exception as exc:
#                 logger.warning(
#                     "Bibliothèque indisponible : %s — génération directe", exc
#                 )
#                 scenario_json, scenario_text = self._generate_via_llm(topic, config)

#         self.patience.run_with_patience(_do_generate)

#         if not scenario_json and not scenario_text:
#             self.io.speak(
#                 "La génération du scénario n'a pas abouti. "
#                 "Vous pouvez néanmoins me poser vos questions directement."
#             )
#             return None

#         # -- Construction de la session -----------------------------------
#         now = datetime.now(timezone.utc).isoformat()
#         try:
#             from vr_scenario_lib.scenario_store import ScenarioSession
#             session = ScenarioSession(
#                 scenario_id   = str(uuid.uuid4()),
#                 topic         = topic,
#                 scenario_text = scenario_text,
#                 scenario_json = scenario_json,
#                 created_at    = now,
#                 updated_at    = now,
#             )
#             logger.info("Session créée (identifiant=%s)", session.scenario_id)
#         except Exception as exc:
#             logger.warning("Création de session impossible : %s", exc)
#             session = None

#         # -- Présentation vocale du scénario ------------------------------
#         self._announce_scenario(scenario_json, scenario_text)
#         return session

#     def _generate_via_llm(
#         self, topic: str, config
#     ) -> "tuple[Dict[str, Any], str]":
#         """
#         Appel direct au modèle pour générer le scénario.
#         Retourne ({}, "") en cas d'échec.
#         """
#         if config is None:
#             return self._fallback_static_scenario(topic)

#         user_msg = "Génère un scénario de formation en réalité virtuelle sur le thème : " + topic

#         try:
#             raw = self._call_llm_raw(
#                 system     = SCENARIO_GEN_SYSTEM,
#                 user       = user_msg,
#                 config     = config,
#                 max_tokens = SCENARIO_GEN_MAX_TOKENS,
#             )
#         except Exception as exc:
#             logger.error("Génération par le modèle échouée : %s", exc)
#             return self._fallback_static_scenario(topic)

#         try:
#             import re
#             m = re.search(r'\{.*\}', raw, re.DOTALL)
#             if not m:
#                 raise ValueError("Structure JSON introuvable")
#             obj = json.loads(m.group())
#         except Exception as exc:
#             logger.error("Analyse du scénario échouée : %s | brut=%s", exc, raw[:200])
#             return self._fallback_static_scenario(topic)

#         text = self._json_to_text(obj, topic)
#         return obj, text

#     @staticmethod
#     def _json_to_text(obj: Dict[str, Any], topic: str) -> str:
#         """Convertit le scénario structuré en texte lisible."""
#         lines = ["# SCÉNARIO DE FORMATION — " + topic.upper(), ""]
#         titre = obj.get("titre", topic)
#         lines += ["## " + titre, ""]

#         objectifs = obj.get("objectifs", [])
#         if objectifs:
#             lines.append("### Objectifs")
#             for o in objectifs:
#                 lines.append("- " + str(o))
#             lines.append("")

#         for etape in obj.get("grandes_lignes", []):
#             num    = etape.get("etape", "")
#             titre_e = etape.get("titre", "")
#             desc   = etape.get("description", "")
#             lines.append("### Étape %s : %s" % (num, titre_e))
#             lines.append(desc)
#             lines.append("")

#         procs = obj.get("procedures_cles", [])
#         if procs:
#             lines.append("### Procédures clés")
#             for p in procs:
#                 lines.append("- " + str(p))
#             lines.append("")

#         vigilance = obj.get("points_vigilance", [])
#         if vigilance:
#             lines.append("### Points de vigilance")
#             for v in vigilance:
#                 lines.append("- " + str(v))
#             lines.append("")

#         return "\n".join(lines)

#     @staticmethod
#     def _fallback_static_scenario(topic: str) -> "tuple[Dict[str, Any], str]":
#         """Scénario minimal si le modèle de langage est inaccessible."""
#         obj = {
#             "titre": "Scénario " + topic,
#             "objectifs": [
#                 "Comprendre les principes fondamentaux de " + topic,
#                 "Maîtriser les procédures de sécurité essentielles",
#                 "Réagir de façon appropriée aux situations d'urgence",
#             ],
#             "grandes_lignes": [
#                 {
#                     "etape": 1,
#                     "titre": "Préparation",
#                     "description": "Vérifier les équipements et les protections individuelles avant toute intervention.",
#                 },
#                 {
#                     "etape": 2,
#                     "titre": "Intervention",
#                     "description": "Appliquer les procédures standard en respectant les consignes de sécurité.",
#                 },
#                 {
#                     "etape": 3,
#                     "titre": "Clôture",
#                     "description": "Consigner les actions effectuées et signaler tout incident survenu.",
#                 },
#             ],
#             "procedures_cles": [
#                 "Vérifier les équipements avant toute intervention",
#                 "Respecter les périmètres de sécurité",
#                 "Alerter la hiérarchie en cas d'incident",
#             ],
#             "points_vigilance": [
#                 "Ne jamais intervenir seul",
#                 "Toujours porter les protections adaptées à la situation",
#             ],
#             "resume_oral": (
#                 "Ce scénario porte sur le thème " + topic + ". "
#                 "Il se déroule en trois étapes : la préparation du matériel, "
#                 "l'intervention selon les procédures standard, "
#                 "et la clôture avec consignation des actions effectuées."
#             ),
#         }
#         text = VRScenarioApp._json_to_text(obj, topic)
#         return obj, text

#     def _announce_scenario(self, scenario_json: Dict[str, Any], scenario_text: str) -> None:
#         # """Présente les grandes lignes du scénario à voix haute."""
#         # print("\n" + "=" * 60)
#         # print("  SCÉNARIO GÉNÉRÉ")
#         # print("=" * 60)
#         # print(scenario_text[:1200] + ("…" if len(scenario_text) > 1200 else ""))
#         print("\n" + "=" * 60)
#         print("  SCÉNARIO TEXTUEL")
#         print("=" * 60)
#         print(scenario_text)
#         print("=" * 60)
#         # --- AJOUT : Affichage du JSON de configuration généré ---
#         print("\n" + "=" * 60)
#         print("  SCÉNARIO GÉNÉRÉ (JSON)")
#         print("=" * 60)
#         print(json.dumps(scenario_json, indent=2, ensure_ascii=False))
#         print("=" * 60 + "\n")
#         # ---------------------------------------------------------
#         # Lecture du résumé oral (conçu pour la synthèse vocale, sans listes)
#         resume = scenario_json.get("resume_oral", "")
#         if not resume:
#             titre = scenario_json.get("titre", "le scénario")
#             etapes = scenario_json.get("grandes_lignes", [])
#             if etapes:
#                 noms = ", ".join(str(e.get("titre", "")) for e in etapes[:4])
#                 resume = (
#                     "Le scénario intitulé " + titre
#                     + " se déroule en " + str(len(etapes))
#                     + " étapes : " + noms + "."
#                 )
#             else:
#                 resume = "Le scénario " + titre + " vient d'être généré."

#         self.io.speak("Voici les grandes lignes de votre scénario.")
#         self.io.speak(resume)

#         # Points de vigilance, si présents
#         vigilance = scenario_json.get("points_vigilance", [])
#         if vigilance:
#             points = " et ".join(vigilance[:3])
#             self.io.speak("Les points de vigilance à retenir sont : " + points + ".")

#         self.io.speak(
#             "Le scénario est prêt. "
#             "Posez-moi vos questions quand vous voulez. "
#             "Dites terminer pour clore la session."
#         )

#     # ------------------------------------------------------------------
#     # Phase 2 : questions-réponses supervisées
#     # ------------------------------------------------------------------

#     def _qa_loop(
#         self,
#         scenario_session,   # ScenarioSession | None
#         supervisor: SupervisorLLM,
#         config,
#     ) -> None:
#         """Boucle de questions et réponses supervisées.

#         Gestion du silence en trois niveaux :
#           Niveau 1 — silence léger    : on relance l'écoute sans rien dire
#           Niveau 2 — relance douce    : après le premier délai, une phrase
#                                         courte rassure sans interroger
#           Niveau 3 — silence prolongé : après plusieurs délais, question
#                                         explicite pour continuer ou terminer
#         """
#         print("\n" + "-" * 60)
#         print("[ SESSION DE QUESTIONS — posez vos questions ]")
#         print("-" * 60)

#         narrator = NarratorSession(
#             topic=scenario_session.topic if scenario_session else "général"
#         )
#         consecutive_timeouts = 0
#         MAX_TIMEOUTS  = 3
#         SOFT_NUDGE_AT = 1

#         while True:

#             # ---- 1. Capture de la question ---------------------------------
#             self.io.speak(pick("listening"))
#             try:
#                 question = self.io.listen_chunk(
#                     pause_threshold   = STT_SILENCE_TIMEOUT,
#                     phrase_time_limit = STT_PHRASE_TIME_LIMIT,
#                     listen_timeout    = STT_LISTEN_TIMEOUT,
#                 )
#                 consecutive_timeouts = 0
#             except RuntimeError as exc:
#                 consecutive_timeouts += 1
#                 logger.info(
#                     "Délai Q&R %d/%d : %s", consecutive_timeouts, MAX_TIMEOUTS, exc
#                 )

#                 if consecutive_timeouts >= MAX_TIMEOUTS:
#                     if self._ask_continue_qa():
#                         consecutive_timeouts = 0
#                     else:
#                         break
#                 elif consecutive_timeouts == SOFT_NUDGE_AT:
#                     self.io.speak(pick("soft_nudge"))
#                 continue

#             # ---- 2. Détection d'un mot de sortie ---------------------------
#             if any(w in question.lower() for w in EXIT_WORDS):
#                 print("\nSortie Q&R : '%s'" % question)
#                 break

#             print("\n[Question] " + question)
#             narrator.add_chunk(question)

#             # ---- 3. Réponse du modèle (avec patience) ----------------------
#             answer = self.patience.run_with_patience(
#                 self._get_answer, question, scenario_session, config
#             )
#             print("[Réponse] " + answer)
#             self.io.speak(answer)

#             # ---- 4. Supervision de l'échange -------------------------------
#             exchange = "Question : " + question + "\nRéponse : " + answer
#             decision = supervisor.analyse(narrator, exchange)
#             logger.info(
#                 "Superviseur Q&R : %s | '%s'",
#                 decision.decision.value,
#                 decision.message[:60] if decision.message else "",
#             )

#             if decision.decision == Decision.CONSEIL:
#                 print("\n[CONSEIL] " + decision.message)
#                 self.io.speak(decision.message)

#             elif decision.decision == Decision.STOP:
#                 print("\n[STOP] " + decision.message)
#                 self.io.interrupt_and_speak(decision.message)
#                 if not self._handle_stop_qa():
#                     break

#     @staticmethod
#     def _strip_filler_words(text: str) -> str:
#         """Supprime les locutions de remplissage les plus courantes (cf. FILLER_PATTERNS_FR).

#         Dégradation silencieuse : en cas d'erreur de traitement, le texte original
#         est retourné inchangé plutôt que de propager une exception pour un simple
#         nettoyage cosmétique (standard de robustesse : ne jamais casser la session
#         vocale pour une amélioration non critique).
#         """
#         if not text:
#             return text
#         try:
#             import re
#             cleaned = text
#             for pattern in FILLER_PATTERNS_FR:
#                 cleaned = re.sub(pattern, "", cleaned, flags=re.IGNORECASE | re.MULTILINE)
#             cleaned = re.sub(r"\s{2,}", " ", cleaned).strip()
#             cleaned = re.sub(r"^[,.]\s*", "", cleaned)
#             if cleaned and cleaned[0].islower():
#                 cleaned = cleaned[0].upper() + cleaned[1:]
#             return cleaned if cleaned else text
#         except Exception as exc:
#             logger.debug("_strip_filler_words : %s", exc)
#             return text

#     @staticmethod
#     def _enforce_max_sentences(text: str, max_sentences: int = QA_MAX_SENTENCES) -> str:
#         """Filet de sécurité : tronque la réponse si le modèle ignore la consigne de concision."""
#         if not text:
#             return text
#         try:
#             import re
#             sentences = [s for s in re.split(r'(?<=[.!?])\s+', text.strip()) if s]
#             if len(sentences) <= max_sentences:
#                 return text
#             return " ".join(sentences[:max_sentences])
#         except Exception as exc:
#             logger.debug("_enforce_max_sentences : %s", exc)
#             return text

#     def _get_answer(self, question: str, scenario_session, config) -> str:
#         """
#         Obtient une réponse du modèle à la question posée.
#         Priorité : discuss_scenario() de la bibliothèque, puis appel direct, puis message de repli.
#         Toute réponse exploitable passe par les filets de sécurité de concision
#         (suppression des mots de remplissage, plafond de phrases) avant d'être renvoyée.
#         """
#         # Via la bibliothèque de scénarios
#         if scenario_session is not None and config is not None:
#             try:
#                 from vr_scenario_lib.scenario import discuss_scenario
#                 reply = discuss_scenario(
#                     session      = scenario_session,
#                     user_message = question,
#                     llm_config   = config,
#                 )
#                 if reply and reply.strip():
#                     reply = self._strip_filler_words(reply.strip())
#                     return self._enforce_max_sentences(reply)
#             except Exception as exc:
#                 logger.warning("discuss_scenario erreur : %s — appel direct", exc)

#         # Appel direct avec contexte du scénario
#         if config is not None:
#             context = (
#                 scenario_session.scenario_text[:800]
#                 if scenario_session and scenario_session.scenario_text
#                 else ""
#             )
#             user_msg = (
#                 ("Contexte du scénario :\n" + context + "\n\n" if context else "")
#                 + "Question de l'apprenant : " + question
#             )
#             try:
#                 reply = self._call_llm_raw(
#                     system     = QA_SYSTEM,
#                     user       = user_msg,
#                     config     = config,
#                     max_tokens = QA_MAX_TOKENS,
#                 ).strip()
#                 reply = self._strip_filler_words(reply)
#                 return self._enforce_max_sentences(reply)
#             except Exception as exc:
#                 logger.error("Appel direct Q&R erreur : %s", exc)

#         return (
#             "Je n'ai pas pu obtenir de réponse pour le moment. "
#             "Vous pouvez reformuler votre question ou consulter la documentation du scénario."
#         )

#     # ------------------------------------------------------------------
#     # Fonctions auxiliaires
#     # ------------------------------------------------------------------

#     @staticmethod
#     def _call_llm_raw(*, system: str, user: str, config, max_tokens: int) -> str:
#         """Appel unifié au modèle de langage : bibliothèque, puis appel direct avec retry.

#         L'appel HTTP direct est retenté jusqu'à LLM_CALL_MAX_RETRIES fois en cas
#         d'erreur réseau, de timeout ou de réponse malformée, avec un délai croissant
#         entre tentatives (backoff linéaire). Lève RuntimeError si toutes les
#         tentatives échouent, pour que l'appelant applique son propre repli.
#         """
#         try:
#             from vr_scenario_lib.llm import call_llm
#             return call_llm(
#                 system=system, user=user,
#                 llm_config=config, max_tokens=max_tokens,
#             )
#         except ImportError:
#             pass
#         except TypeError as exc:
#             # Bibliothèque présente mais signature incompatible : on bascule sur
#             # l'appel HTTP direct (cf. SupervisorLLM._call_llm pour le même cas).
#             logger.debug("call_llm (bibliothèque) signature incompatible : %s — appel direct", exc)

#         import urllib.request
#         import urllib.error

#         payload = json.dumps({
#             "model":      getattr(config, "model", "gpt-3.5-turbo"),
#             "max_tokens": max_tokens,
#             "messages":   [
#                 {"role": "system", "content": system},
#                 {"role": "user",   "content": user},
#             ],
#         }).encode()
#         api_url = getattr(config, "api_url", "https://api.openai.com/v1/chat/completions")
#         token   = getattr(config, "token", "")
#         req = urllib.request.Request(
#             api_url, data=payload,
#             headers={
#                 "Content-Type":  "application/json",
#                 "Authorization": "Bearer " + token,
#             },
#         )

#         last_exc: Optional[Exception] = None
#         total_attempts = LLM_CALL_MAX_RETRIES + 1
#         for attempt in range(1, total_attempts + 1):
#             try:
#                 with urllib.request.urlopen(req, timeout=20) as resp:
#                     data = json.loads(resp.read())
#                 return data["choices"][0]["message"]["content"]
#             except (urllib.error.URLError, TimeoutError, ValueError, KeyError) as exc:
#                 last_exc = exc
#                 logger.warning(
#                     "Appel LLM échoué (tentative %d/%d) : %s", attempt, total_attempts, exc
#                 )
#                 if attempt < total_attempts:
#                     time.sleep(LLM_CALL_RETRY_BACKOFF_S * attempt)

#         raise RuntimeError(
#             "Appel au modèle de langage impossible après %d tentative(s)" % total_attempts
#         ) from last_exc

#     def _ask_continue_qa(self) -> bool:
#         text = self.io.listen_short(pick("no_response_continue_check"))
#         if not text:
#             return False
#         return any(
#             w in text.lower()
#             for w in {"oui", "yes", "continuer", "continue", "si", "d'accord", "bien sûr"}
#         )

#     def _handle_stop_qa(self) -> bool:
#         """Pause après une alerte STOP en phase questions-réponses. Retourne True pour reprendre."""
#         self.io.speak(
#             "La session est interrompue suite à cette alerte. "
#             "Dites reprendre pour continuer vos questions, "
#             "ou terminer pour clore la session."
#         )
#         text = ""
#         try:
#             text = self.io.listen_chunk(
#                 pause_threshold   = 2.0,
#                 phrase_time_limit = 10,
#                 listen_timeout    = 12,
#             )
#         except RuntimeError:
#             pass
#         if any(w in text.lower() for w in {"reprendre", "continuer", "oui", "yes", "d'accord"}):
#             self.io.speak("Très bien. Je reste à l'écoute de vos questions.")
#             return True
#         return False

#     def _goodbye(self) -> None:
#         self.io.speak(
#             "Merci pour cette session de formation. "
#             "J'espère que ce scénario vous a été utile. "
#             "À très bientôt."
#         )
#         print("\nAu revoir !\n")

#     # ------------------------------------------------------------------
#     # Configuration du modèle de langage
#     # ------------------------------------------------------------------

#     def _setup_llm(self):
#         try:
#             from vr_scenario_lib.config import build_llm_config
#             return build_llm_config()
#         except Exception as exc:
#             logger.warning(
#                 "Configuration du modèle indisponible : %s — mode dégradé (scénarios statiques)",
#                 exc,
#             )
#             return None


# # ============================================================================
# # Interface en ligne de commande
# # ============================================================================

# def _parse_args() -> argparse.Namespace:
#     p = argparse.ArgumentParser(
#         description=(
#             "Application vocale de supervision de scénarios de formation en réalité virtuelle"
#         ),
#         formatter_class=argparse.ArgumentDefaultsHelpFormatter,
#     )
#     p.add_argument(
#         "--stt-backend", default="whisper", choices=["whisper", "google"],
#         help="Moteur de reconnaissance vocale.",
#     )
#     p.add_argument(
#         "--tts-backend", default=TTS_DEFAULT_BACKEND,
#         choices=["coqui", "piper", "gtts", "pyttsx3"],
#         help=(
#             "Moteur de synthèse vocale. "
#             "Les options 'coqui' et 'piper' fonctionnent entièrement hors ligne."
#         ),
#     )
#     p.add_argument(
#         "--language", default="fr",
#         help="Code de langue au format ISO 639-1 (fr par défaut).",
#     )
#     p.add_argument(
#         "--whisper-model", default=WHISPER_DEFAULT_MODEL,
#         choices=["tiny", "base", "small", "medium", "large"],
#         help="Taille du modèle Whisper. L'option 'small' est recommandée pour le français.",
#     )
#     p.add_argument(
#         "--coqui-model", default=COQUI_MODEL_FR,
#         help="Identifiant du modèle Coqui.",
#     )
#     p.add_argument(
#         "--piper-model", default=PIPER_MODEL_FR,
#         help="Nom du modèle Piper (exemple : fr_FR-tom-medium).",
#     )
#     p.add_argument(
#         "--debug", action="store_true",
#         help="Active les journaux de débogage complets.",
#     )
#     return p.parse_args()


# def main() -> None:
#     args = _parse_args()
#     if args.debug:
#         logging.getLogger().setLevel(logging.DEBUG)

#     io = VoiceIO(
#         stt_backend   = args.stt_backend,
#         tts_backend   = args.tts_backend,
#         language      = args.language,
#         whisper_model = args.whisper_model,
#         coqui_model   = args.coqui_model,
#         piper_model   = args.piper_model,
#     )
#     app = VRScenarioApp(io)
#     try:
#         app.run()
#     except KeyboardInterrupt:
#         print("\nSession interrompue par l'utilisateur.")
#     finally:
#         io.close()


# if __name__ == "__main__":
#     main()




"""
Application vocale de supervision de scénarios de formation en réalité virtuelle.
Version entreprise — standards industriels.

RÔLE DE L'APPLICATION
----------------------
L'utilisateur décrit librement un scénario de réalité virtuelle à voix haute.
L'application écoute en continu, transcrit par fragments avec détection de voix,
et soumet chaque fragment à un superviseur linguistique qui peut :
  - CONTINUER  : rester silencieux (écoute neutre)
  - CONSEIL    : intervenir poliment pour formuler un conseil
  - STOP       : interrompre fermement pour signaler une erreur critique

Architecture
------------
VoiceIO          : reconnaissance vocale (Faster Whisper + VAD SpeechRecognition) + synthèse vocale française native.
SupervisorLLM    : analyse chaque fragment, décide CONTINUER / CONSEIL / STOP.
NarratorSession  : accumule la transcription, maintient le contexte du scénario.
VRScenarioApp    : orchestration métier (initialisation + boucle de narration supervisée).
PatienceManager  : retour sonore pendant les temps de traitement (signaux d'ambiance + phrases de transition).

NOTE DE REFACTORING (paramétrage / atomicité)
----------------------------------------------
Cette version conserve EXACTEMENT la même logique métier que l'original. Le
refactoring porte uniquement sur l'organisation du code :

  1. Toute valeur auparavant codée en dur (timeouts, seuils, prompts système,
     listes de mots, chaînes de fallback TTS, etc.) est désormais portée par
     une dataclass de configuration dédiée (SttConfig, TtsConfig, TopicConfig,
     SupervisorConfig, ScenarioGenConfig, QaConfig, RetryConfig, PatienceConfig,
     ExitConfig), elle-même regroupée dans AppConfig. Les valeurs par défaut
     reprennent exactement les constantes d'origine.
  2. Les gros blocs de logique (sanitisation TTS, filtrage des mots de
     remplissage, retry réseau, lecture audio fichier->haut-parleur, obtention
     d'une réponse Q&R) sont décomposés en petites fonctions atomiques,
     testables isolément et réutilisées à plusieurs endroits (DRY).
  3. Le point d'extension demandé explicitement — "le scénario discuter
     soit paramétrable" — est exposé via QaConfig.discuss_scenario_fn : on
     peut injecter sa propre fonction de dialogue scénario sans toucher au
     reste du code (voir VRScenarioApp._answer_via_custom_fn).
  4. Aucune suppression de fallback, de retry, ni de gestion d'exception :
     chaque chemine de repli de l'original est conservé tel quel.

Moteurs de synthèse vocale française (ordre de priorité automatique)
--------------------------------------------------------------------
1. coqui   -- Coqui VITS tts_models/fr/mai/tacotron2-DDC : voix neurale hors ligne, haute qualité
2. piper   -- Piper fr_FR-tom-medium                      : voix neurale hors ligne, très rapide
3. gtts    -- Google Synthèse vocale                      : voix en ligne, qualité maximale
4. pyttsx3 -- espeak-fr                                   : synthèse de base, sans dépendances

Usage :
    python app_vocal.py                            # détection automatique du meilleur moteur disponible
    python app_vocal.py --tts-backend coqui        # Coqui VITS (hors ligne, haute qualité)
    python app_vocal.py --tts-backend piper        # Piper (hors ligne, très rapide)
    python app_vocal.py --tts-backend gtts         # Google Synthèse vocale (en ligne)
    python app_vocal.py --stt-backend google       # Google Reconnaissance vocale (en ligne)
    python app_vocal.py --whisper-model small      # meilleure précision de reconnaissance
    python app_vocal.py --debug                    # journaux de débogage complets
"""

from __future__ import annotations

import argparse
import json
import logging
import math
import os
import random
import sys
import tempfile
import threading
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple

# ---------------------------------------------------------------------------
# Journalisation
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(name)-36s | %(levelname)-8s | %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# ============================================================================
# Constantes par défaut
# ----------------------------------------------------------------------------
# Ces constantes ne sont plus consommées directement par la logique métier :
# elles servent uniquement de valeurs par défaut aux dataclasses de
# configuration ci-dessous. Toute la logique métier lit sa configuration via
# `self._cfg` (ou équivalent), jamais via ces constantes globales.
# ============================================================================

STT_LISTEN_TIMEOUT    = 8
STT_PHRASE_TIME_LIMIT = 20          # durée maximale d'un fragment de narration
STT_SILENCE_TIMEOUT   = 2.0         # silence détecté → fin du fragment
STT_AMBIENT_DURATION  = 0.5
TTS_TO_STT_SETTLE_S   = 0.3         # pause après la synthèse vocale, avant calibration du micro
                                     # (laisse l'écho de la synthèse se dissiper — sinon les
                                     # réponses courtes comme "oui" sont mal captées)
TTS_SPEECH_RATE       = 145
TTS_VOLUME            = 0.92
WHISPER_DEFAULT_MODEL = "base"
WHISPER_BEAM_SIZE     = 5

# Biais lexical Whisper pour la capture du thème : un thème prononcé est un
# fragment de 2 à 4 mots SANS contexte (contrairement aux questions en Q&R,
# plus longues, où le modèle peut s'appuyer sur la phrase pour se corriger).
# initial_prompt oriente la transcription vers le vocabulaire attendu —
# technique standard pour fiabiliser la reconnaissance de termes techniques courts.
WHISPER_TOPIC_PROMPT = (
    "Thèmes de formation en réalité virtuelle industrielle : consignation gaz, "
    "consignation électrique, sécurité incendie, premiers secours, travail en hauteur, "
    "espace confiné, risque chimique, manutention, procédures de sécurité."
)

# Biais lexical Whisper pour les confirmations oui/non : cas encore plus
# défavorable que le thème (un seul mot, souvent moins d'une seconde de signal).
WHISPER_YESNO_PROMPT = (
    "L'apprenant confirme le thème proposé. Il répond soit oui, c'est exact, "
    "c'est le bon thème, soit non, ce n'est pas correct, ce n'est pas ça."
)

# Mots déclencheurs de fin de session
EXIT_WORDS = {"quitter", "terminer", "au revoir", "fin", "arrêter", "c'est tout"}

# Capture du thème — confirmation orale obligatoire
TOPIC_MAX_ATTEMPTS         = 3
TOPIC_CONFIRM_MAX_ATTEMPTS = 2
TOPIC_CONFIRM_YES  = {"oui", "ouais", "yes", "exact", "correct", "c'est ça", "d'accord", "affirmatif"}
TOPIC_CONFIRM_NO   = {"non", "no", "faux", "incorrect", "pas ça", "négatif"}
TOPIC_DEFAULT_FALLBACK = "sécurité industrielle"

# Moteurs de synthèse vocale française native
TTS_DEFAULT_BACKEND   = "coqui"
TTS_FALLBACK_CHAIN    = ["coqui", "piper", "gtts", "pyttsx3"]

# Coqui : voix féminine Maï, accent français métropolitain soigné
COQUI_MODEL_FR    = "tts_models/fr/mai/tacotron2-DDC"
COQUI_SAMPLE_RATE = 22050

# Piper : voix masculine Tom, accent français métropolitain naturel
PIPER_MODEL_FR    = "fr_FR-tom-medium"
PIPER_SAMPLE_RATE = 22050

# Superviseur — instructions système
SUPERVISOR_MAX_TOKENS = 256
SUPERVISOR_SYSTEM = (
    "Tu es un superviseur expert en sécurité de la réalité virtuelle et en procédures industrielles. "
    "L'utilisateur décrit à voix haute un scénario de formation en réalité virtuelle. "
    "Tu reçois des fragments de sa narration en temps réel.\n\n"
    "Analyse le dernier fragment dans son contexte et réponds UNIQUEMENT avec un objet JSON :\n"
    '{"decision": "CONTINUER" | "CONSEIL" | "STOP", "message": "<texte à dire, vide si CONTINUER>"}\n\n'
    "Règles strictes :\n"
    "- CONTINUER  : narration correcte, cohérente, sans danger. Message vide obligatoire.\n"
    "- CONSEIL    : amélioration possible. Message court, positif, concret. Deux phrases maximum.\n"
    "- STOP       : erreur critique de procédure, danger réel, incohérence grave. "
    "Message direct et précis. Commence par 'Attention : '.\n"
    "Ne jamais inventer de contexte non mentionné. Rester factuel."
)

# Génération de scénario — instructions système
SCENARIO_GEN_MAX_TOKENS = 1024
SCENARIO_GEN_SYSTEM = (
    "Tu es un expert en conception de scénarios de formation en réalité virtuelle industrielle. "
    "À partir d'un thème, génère un scénario structuré en JSON uniquement, sans aucun texte avant ou après.\n\n"
    "Format JSON attendu (respecte exactement ces clés) :\n"
    '{\n'
    '  "titre": "Titre court du scénario",\n'
    '  "objectifs": ["objectif 1", "objectif 2", "objectif 3"],\n'
    '  "grandes_lignes": [\n'
    '    {"etape": 1, "titre": "Titre de l\'étape", "description": "Description concise"},\n'
    '    ...\n'
    '  ],\n'
    '  "procedures_cles": ["procédure 1", "procédure 2"],\n'
    '  "points_vigilance": ["point 1", "point 2"],\n'
    '  "resume_oral": "Texte fluide de trois à quatre phrases pour lecture vocale. Pas de listes, pas de symboles."\n'
    '}\n\n'
    "Le champ resume_oral doit être lisible à voix haute sans aucun accroc : pas de tirets, "
    "pas de parenthèses, pas d'abréviations, pas de sigles. Quatre phrases au maximum."
)

# Questions-réponses — instructions système
QA_MAX_TOKENS    = 180          # réduit : force la concision dès la génération
QA_MAX_SENTENCES = 2            # filet de sécurité appliqué après coup
QA_SYSTEM = (
    "Tu es un formateur expert qui aide un apprenant à comprendre un scénario de formation en réalité virtuelle. "
    "Tu réponds aux questions en t'appuyant exclusivement sur le scénario fourni. "
    "Réponse impérativement courte : une phrase si possible, deux phrases maximum. "
    "Va droit à l'information utile. "
    "Pas de listes, pas de tirets, pas de symboles, aucun mot ou formule de remplissage "
    "(par exemple : en fait, donc, voilà, eh bien, du coup, en gros, extra). "
    "Parle directement à l'apprenant, avec chaleur et précision."
)

# Appel au modèle de langage — robustesse réseau (standard industriel : retry + backoff)
LLM_CALL_MAX_RETRIES     = 2     # tentatives supplémentaires après l'essai initial
LLM_CALL_RETRY_BACKOFF_S = 1.5   # délai de base entre tentatives (croissance linéaire)
LLM_DEFAULT_MODEL        = "gpt-3.5-turbo"
LLM_DEFAULT_API_URL      = "https://api.openai.com/v1/chat/completions"
LLM_CALL_TIMEOUT_S       = 20
SUPERVISOR_CALL_TIMEOUT_S = 15

# Locutions de remplissage à éliminer des réponses orales (filet de sécurité post-génération)
FILLER_PATTERNS_FR = [
    r"\ben fait\b,?\s*",
    r"\bdonc\b,?\s*",
    r"\bvoil[aà]\b,?\s*",
    r"\beh bien\b,?\s*",
    r"\bdu coup\b,?\s*",
    r"\ben gros\b,?\s*",
    r"\ben quelque sorte\b,?\s*",
    r"\bpour ainsi dire\b,?\s*",
    r"\b[aà] vrai dire\b,?\s*",
    r"\bdisons que\b,?\s*",
    r"\bil faut savoir que\b,?\s*",
    r"\bextra\b\s*[!.,]?\s*",
    r"^\s*alors,?\s*",
]

# Profils des signaux d'ambiance (fréquence Hz, durée s, amplitude)
EARCON_PROFILES_DEFAULT: Dict[str, Tuple[float, float, float]] = {
    "patience_short":  (880.0, 0.10, 0.15),
    "patience_medium": (660.0, 0.15, 0.18),
    "patience_long":   (440.0, 0.22, 0.20),
}
EARCON_SAMPLE_RATE = 22050

# Paliers de patience (cf. PatienceConfig)
PATIENCE_LEVEL_SHORT_S     = 1.0
PATIENCE_LEVEL_MEDIUM_S    = 3.0
PATIENCE_LEVEL_LONG_S      = 10.0
PATIENCE_LEVEL_VERY_LONG_S = 20.0
PATIENCE_REMINDER_INTERVAL_S = 12.0

# Boucle Q&R — gestion du silence
QA_MAX_TIMEOUTS  = 3
QA_SOFT_NUDGE_AT = 1


# ============================================================================
# Bibliothèque de phrases système
# ----------------------------------------------------------------------------
# Chaque entrée regroupe plusieurs formulations d'une même situation récurrente.
# pick() tire une variante aléatoire à chaque appel, ce qui réduit sensiblement
# la fatigue auditive lors de longues sessions. L'ensemble du dictionnaire est
# paramétrable : on peut injecter sa propre bibliothèque de phrases.
# ============================================================================

CACHED_PHRASES_FR: Dict[str, List[str]] = {
    "listening": [
        "Je vous écoute.",
        "À vous.",
        "Allez-y.",
        "Je suis prêt.",
        "La parole est à vous.",
    ],
    "ack_short": [
        "Bien reçu.",
        "Compris.",
        "Noté.",
        "Entendu.",
    ],
    "thinking_short": [
        "Un instant.",
        "Je vérifie.",
    ],
    "thinking_medium": [
        "Je prépare votre réponse.",
        "Je consulte le scénario.",
        "Je rassemble les éléments.",
        "Je cherche la bonne information.",
        "Je réfléchis à votre question.",
    ],
    "thinking_long": [
        "La question est détaillée, je finalise ma réponse.",
        "Cela demande un peu plus de réflexion. Je suis sur le sujet.",
        "Je creuse la question. Encore un court instant.",
        "Je vérifie tous les éléments. Merci de votre patience.",
    ],
    "thinking_very_long": [
        "Je suis toujours en train de traiter votre demande.",
        "Le traitement prend un peu plus de temps que prévu. Je reste sur le sujet.",
        "Toujours en cours. Je reviens vers vous très bientôt.",
    ],
    "soft_nudge": [
        "Je reste disponible si vous avez une question.",
        "Prenez votre temps. Je vous écoute quand vous êtes prêt.",
        "Pas de précipitation. Je suis là.",
        "Vous pouvez continuer quand vous le souhaitez.",
    ],
    "no_response_continue_check": [
        "Je n'entends plus rien. Souhaitez-vous continuer la session ? "
        "Dites oui pour continuer, ou non pour terminer.",
        "Il y a un long silence. Voulez-vous poursuivre ? "
        "Répondez oui ou non.",
    ],
}


def pick(key: str, phrase_bank: Optional[Dict[str, List[str]]] = None) -> str:
    """Tire aléatoirement une variante de phrase système pour réduire la répétition.

    phrase_bank : bibliothèque de phrases à utiliser (paramétrable). Si non
    fournie, utilise la bibliothèque par défaut CACHED_PHRASES_FR.
    """
    bank = phrase_bank if phrase_bank is not None else CACHED_PHRASES_FR
    options = bank.get(key)
    if not options:
        return ""
    return random.choice(options)


# ============================================================================
# Configuration — dataclasses atomiques regroupées dans AppConfig
# ----------------------------------------------------------------------------
# Chaque sous-configuration porte la responsabilité d'un seul sous-système
# (séparation des responsabilités). AppConfig les agrège. Les valeurs par
# défaut reproduisent exactement le comportement d'origine.
# ============================================================================

@dataclass
class SttConfig:
    """Paramètres de reconnaissance vocale."""
    backend: str = "whisper"                      # "whisper" | "google"
    language: str = "fr"
    whisper_model: str = WHISPER_DEFAULT_MODEL
    whisper_beam_size: int = WHISPER_BEAM_SIZE
    listen_timeout: float = STT_LISTEN_TIMEOUT
    phrase_time_limit: int = STT_PHRASE_TIME_LIMIT
    silence_timeout: float = STT_SILENCE_TIMEOUT
    ambient_duration: float = STT_AMBIENT_DURATION
    energy_threshold: int = 4000
    dynamic_energy_threshold: bool = True
    topic_prompt_bias: str = WHISPER_TOPIC_PROMPT
    yesno_prompt_bias: str = WHISPER_YESNO_PROMPT


@dataclass
class TtsConfig:
    """Paramètres de synthèse vocale."""
    backend: str = TTS_DEFAULT_BACKEND
    fallback_chain: List[str] = field(default_factory=lambda: list(TTS_FALLBACK_CHAIN))
    language: str = "fr"
    coqui_model: str = COQUI_MODEL_FR
    coqui_sample_rate: int = COQUI_SAMPLE_RATE
    piper_model: str = PIPER_MODEL_FR
    piper_timeout_s: int = 30
    speech_rate: int = TTS_SPEECH_RATE
    volume: float = TTS_VOLUME
    settle_after_speak_s: float = TTS_TO_STT_SETTLE_S
    earcon_profiles: Dict[str, Tuple[float, float, float]] = field(
        default_factory=lambda: dict(EARCON_PROFILES_DEFAULT)
    )
    earcon_sample_rate: int = EARCON_SAMPLE_RATE
    filler_patterns: List[str] = field(default_factory=lambda: list(FILLER_PATTERNS_FR))
    phrase_bank: Dict[str, List[str]] = field(default_factory=lambda: dict(CACHED_PHRASES_FR))


@dataclass
class TopicConfig:
    """Paramètres de capture/confirmation du thème."""
    max_attempts: int = TOPIC_MAX_ATTEMPTS
    confirm_max_attempts: int = TOPIC_CONFIRM_MAX_ATTEMPTS
    confirm_yes_words: set = field(default_factory=lambda: set(TOPIC_CONFIRM_YES))
    confirm_no_words: set = field(default_factory=lambda: set(TOPIC_CONFIRM_NO))
    default_fallback_topic: str = TOPIC_DEFAULT_FALLBACK
    initial_prompt_text: str = (
        "Sur quel thème souhaitez-vous travailler ? "
        "Vous pouvez me dire, par exemple : la consignation gaz, "
        "la sécurité incendie, ou les premiers secours."
    )
    retry_prompt_text: str = "Je vous écoute à nouveau. Quel est le thème souhaité ?"


@dataclass
class RetryConfig:
    """Paramètres communs de retry réseau (standard industriel : retry + backoff)."""
    max_retries: int = LLM_CALL_MAX_RETRIES
    backoff_s: float = LLM_CALL_RETRY_BACKOFF_S
    call_timeout_s: int = LLM_CALL_TIMEOUT_S


@dataclass
class LlmEndpointConfig:
    """Paramètres réseau par défaut pour l'appel HTTP direct au modèle."""
    default_model: str = LLM_DEFAULT_MODEL
    default_api_url: str = LLM_DEFAULT_API_URL


@dataclass
class SupervisorConfig:
    """Paramètres du superviseur de narration."""
    system_prompt: str = SUPERVISOR_SYSTEM
    max_tokens: int = SUPERVISOR_MAX_TOKENS
    call_timeout_s: int = SUPERVISOR_CALL_TIMEOUT_S


@dataclass
class ScenarioGenConfig:
    """Paramètres de génération du scénario."""
    system_prompt: str = SCENARIO_GEN_SYSTEM
    max_tokens: int = SCENARIO_GEN_MAX_TOKENS


@dataclass
class QaConfig:
    """Paramètres de la boucle questions-réponses.

    discuss_scenario_fn est LE point d'extension demandé : on peut y injecter
    sa propre fonction de dialogue avec le scénario, avec la signature
    `fn(session, user_message, llm_config) -> str`. Si None (par défaut), le
    comportement d'origine s'applique (bibliothèque vr_scenario_lib, puis
    appel direct, puis message de repli).
    """
    system_prompt: str = QA_SYSTEM
    max_tokens: int = QA_MAX_TOKENS
    max_sentences: int = QA_MAX_SENTENCES
    filler_patterns: List[str] = field(default_factory=lambda: list(FILLER_PATTERNS_FR))
    scenario_context_chars: int = 800
    discuss_scenario_fn: Optional[Callable[[Any, str, Any], str]] = None
    fallback_message: str = (
        "Je n'ai pas pu obtenir de réponse pour le moment. "
        "Vous pouvez reformuler votre question ou consulter la documentation du scénario."
    )
    max_timeouts: int = QA_MAX_TIMEOUTS
    soft_nudge_at: int = QA_SOFT_NUDGE_AT


@dataclass
class PatienceConfig:
    """Seuils de la stratégie de retour sonore pendant les temps de traitement."""
    level_short_s: float = PATIENCE_LEVEL_SHORT_S
    level_medium_s: float = PATIENCE_LEVEL_MEDIUM_S
    level_long_s: float = PATIENCE_LEVEL_LONG_S
    level_very_long_s: float = PATIENCE_LEVEL_VERY_LONG_S
    reminder_interval_s: float = PATIENCE_REMINDER_INTERVAL_S
    poll_interval_s: float = 0.25
    phrase_bank: Dict[str, List[str]] = field(default_factory=lambda: dict(CACHED_PHRASES_FR))


@dataclass
class ExitConfig:
    """Mots déclencheurs de fin de session."""
    exit_words: set = field(default_factory=lambda: set(EXIT_WORDS))


@dataclass
class AppConfig:
    """Configuration agrégée de l'application — un seul objet à transmettre."""
    stt: SttConfig = field(default_factory=SttConfig)
    tts: TtsConfig = field(default_factory=TtsConfig)
    topic: TopicConfig = field(default_factory=TopicConfig)
    retry: RetryConfig = field(default_factory=RetryConfig)
    llm_endpoint: LlmEndpointConfig = field(default_factory=LlmEndpointConfig)
    supervisor: SupervisorConfig = field(default_factory=SupervisorConfig)
    scenario_gen: ScenarioGenConfig = field(default_factory=ScenarioGenConfig)
    qa: QaConfig = field(default_factory=QaConfig)
    patience: PatienceConfig = field(default_factory=PatienceConfig)
    exit: ExitConfig = field(default_factory=ExitConfig)
    debug: bool = False


# ----------------------------------------------------------------------------
# Constructeurs atomiques de configuration (un par sous-système), assemblés
# par build_app_config(). Chacun peut être appelé/testé indépendamment.
# ----------------------------------------------------------------------------

def build_stt_config(args: argparse.Namespace) -> SttConfig:
    return SttConfig(
        backend=args.stt_backend,
        language=args.language,
        whisper_model=args.whisper_model,
    )


def build_tts_config(args: argparse.Namespace) -> TtsConfig:
    return TtsConfig(
        backend=args.tts_backend,
        language=args.language,
        coqui_model=args.coqui_model,
        piper_model=args.piper_model,
    )


def build_topic_config(_args: argparse.Namespace) -> TopicConfig:
    return TopicConfig()


def build_retry_config(_args: argparse.Namespace) -> RetryConfig:
    return RetryConfig()


def build_supervisor_config(_args: argparse.Namespace) -> SupervisorConfig:
    return SupervisorConfig()


def build_scenario_gen_config(_args: argparse.Namespace) -> ScenarioGenConfig:
    return ScenarioGenConfig()


def build_qa_config(
    _args: argparse.Namespace,
    discuss_scenario_fn: Optional[Callable[[Any, str, Any], str]] = None,
) -> QaConfig:
    """Construit la configuration Q&R.

    discuss_scenario_fn permet d'injecter, depuis l'appelant (script, tests,
    intégration), une implémentation alternative de la discussion de scénario
    sans modifier VRScenarioApp.
    """
    return QaConfig(discuss_scenario_fn=discuss_scenario_fn)


def build_patience_config(_args: argparse.Namespace) -> PatienceConfig:
    return PatienceConfig()


def build_exit_config(_args: argparse.Namespace) -> ExitConfig:
    return ExitConfig()


def build_app_config(
    args: argparse.Namespace,
    *,
    discuss_scenario_fn: Optional[Callable[[Any, str, Any], str]] = None,
) -> AppConfig:
    """Assemble la configuration complète à partir des arguments CLI.

    Chaque sous-configuration est construite par sa propre fonction atomique,
    ce qui permet de les remplacer ou de les tester indépendamment.
    """
    return AppConfig(
        stt=build_stt_config(args),
        tts=build_tts_config(args),
        topic=build_topic_config(args),
        retry=build_retry_config(args),
        supervisor=build_supervisor_config(args),
        scenario_gen=build_scenario_gen_config(args),
        qa=build_qa_config(args, discuss_scenario_fn=discuss_scenario_fn),
        patience=build_patience_config(args),
        exit=build_exit_config(args),
        debug=args.debug,
    )


# ============================================================================
# Décision + NarratorSession
# ============================================================================

class Decision(Enum):
    CONTINUER = "CONTINUER"
    CONSEIL   = "CONSEIL"
    STOP      = "STOP"


@dataclass
class SupervisorDecision:
    decision: Decision = Decision.CONTINUER
    message:  str      = ""

    def must_speak(self) -> bool:
        return self.decision in (Decision.CONSEIL, Decision.STOP)


@dataclass
class NarratorSession:
    """Accumule la transcription et maintient le contexte pour le superviseur."""
    topic:     str
    chunks:    List[str] = field(default_factory=list)
    full_text: str       = ""

    def add_chunk(self, text: str) -> None:
        self.chunks.append(text)
        self.full_text = " ".join(self.chunks)

    def context_window(self, n: int = 5) -> str:
        return " ".join(self.chunks[-n:])

    def summary(self) -> str:
        return "%d séquence(s), environ %d mots" % (len(self.chunks), len(self.full_text.split()))


# ============================================================================
# Fonctions atomiques réutilisables — réseau, texte
# ----------------------------------------------------------------------------
# Extraites pour être partagées entre SupervisorLLM et VRScenarioApp (DRY),
# et pour rester testables indépendamment de toute classe.
# ============================================================================

def call_with_retry(
    fn: Callable[[], str],
    *,
    retry_cfg: RetryConfig,
    retryable_exceptions: Tuple[type, ...],
    on_attempt_failed: Optional[Callable[[int, int, Exception], None]] = None,
) -> str:
    """Exécute fn() avec retry + backoff linéaire (standard industriel).

    Tente jusqu'à (1 + retry_cfg.max_retries) fois. Entre deux tentatives,
    attend retry_cfg.backoff_s * numéro_de_tentative. Propage une RuntimeError
    chaînée si toutes les tentatives échouent — comportement identique à
    l'original.
    """
    last_exc: Optional[Exception] = None
    total_attempts = retry_cfg.max_retries + 1
    for attempt in range(1, total_attempts + 1):
        try:
            return fn()
        except retryable_exceptions as exc:
            last_exc = exc
            if on_attempt_failed is not None:
                on_attempt_failed(attempt, total_attempts, exc)
            if attempt < total_attempts:
                time.sleep(retry_cfg.backoff_s * attempt)
    raise RuntimeError(
        "Appel au modèle de langage impossible après %d tentative(s)" % total_attempts
    ) from last_exc


def build_chat_payload(*, system: str, user: str, model: str, max_tokens: int) -> bytes:
    """Construit le corps JSON d'un appel de complétion de chat."""
    return json.dumps({
        "model":      model,
        "max_tokens": max_tokens,
        "messages":   [
            {"role": "system", "content": system},
            {"role": "user",   "content": user},
        ],
    }).encode()


def perform_chat_http_call(
    *, system: str, user: str, config, max_tokens: int,
    endpoint_cfg: LlmEndpointConfig, timeout_s: int,
) -> str:
    """Appel HTTP direct unique (sans retry) à une API de complétion de chat.

    Fonction atomique réutilisée à la fois par SupervisorLLM et par le retry
    de VRScenarioApp._call_llm_raw.
    """
    import urllib.request

    model = getattr(config, "model", endpoint_cfg.default_model)
    api_url = getattr(config, "api_url", endpoint_cfg.default_api_url)
    token = getattr(config, "token", "")

    payload = build_chat_payload(system=system, user=user, model=model, max_tokens=max_tokens)
    req = urllib.request.Request(
        api_url,
        data=payload,
        headers={
            "Content-Type":  "application/json",
            "Authorization": "Bearer " + token,
        },
    )
    with urllib.request.urlopen(req, timeout=timeout_s) as resp:
        data = json.loads(resp.read())
    return data["choices"][0]["message"]["content"]


def try_call_llm_via_library(
    *, system: str, user: str, config, max_tokens: int,
) -> Optional[str]:
    """Tente l'appel via vr_scenario_lib.llm.call_llm. Retourne None si la
    bibliothèque est absente ou incompatible (pour basculer sur l'appel direct).
    """
    try:
        from vr_scenario_lib.llm import call_llm
        return call_llm(system=system, user=user, llm_config=config, max_tokens=max_tokens)
    except ImportError:
        return None
    except TypeError as exc:
        logger.debug("call_llm (bibliothèque) signature incompatible : %s — appel direct", exc)
        return None


def extract_first_json_object(raw: str) -> Optional[Dict[str, Any]]:
    """Extrait le premier objet JSON `{...}` trouvé dans une chaîne brute."""
    import re
    m = re.search(r'\{.*\}', raw, re.DOTALL)
    if not m:
        return None
    return json.loads(m.group())


def apply_regex_patterns(text: str, patterns: Sequence[str]) -> str:
    """Applique séquentiellement une liste de motifs regex de suppression.
    Fonction pure et atomique, réutilisée pour le nettoyage TTS et le
    filtrage des mots de remplissage en Q&R.
    """
    import re
    cleaned = text
    for pattern in patterns:
        cleaned = re.sub(pattern, "", cleaned, flags=re.IGNORECASE | re.MULTILINE)
    return cleaned


def normalize_whitespace(text: str) -> str:
    import re
    text = re.sub(r"\s{2,}", " ", text)
    return text.strip()


def capitalize_first_letter(text: str) -> str:
    if text and text[0].islower():
        return text[0].upper() + text[1:]
    return text


def strip_leading_punctuation(text: str) -> str:
    import re
    return re.sub(r"^[,.]\s*", "", text)


def strip_filler_words(text: str, patterns: Sequence[str] = FILLER_PATTERNS_FR) -> str:
    """Supprime les locutions de remplissage les plus courantes.

    Dégradation silencieuse : en cas d'erreur de traitement, le texte original
    est retourné inchangé plutôt que de propager une exception pour un simple
    nettoyage cosmétique (ne jamais casser la session vocale pour une
    amélioration non critique).
    """
    if not text:
        return text
    try:
        cleaned = apply_regex_patterns(text, patterns)
        cleaned = normalize_whitespace(cleaned)
        cleaned = strip_leading_punctuation(cleaned)
        cleaned = capitalize_first_letter(cleaned)
        return cleaned if cleaned else text
    except Exception as exc:
        logger.debug("strip_filler_words : %s", exc)
        return text


def enforce_max_sentences(text: str, max_sentences: int = QA_MAX_SENTENCES) -> str:
    """Filet de sécurité : tronque la réponse si le modèle ignore la consigne de concision."""
    if not text:
        return text
    try:
        import re
        sentences = [s for s in re.split(r'(?<=[.!?])\s+', text.strip()) if s]
        if len(sentences) <= max_sentences:
            return text
        return " ".join(sentences[:max_sentences])
    except Exception as exc:
        logger.debug("enforce_max_sentences : %s", exc)
        return text


def postprocess_qa_answer(text: str, qa_cfg: QaConfig) -> str:
    """Pipeline de post-traitement d'une réponse Q&R : filtrage des mots de
    remplissage puis plafonnement du nombre de phrases. Composé de deux
    fonctions atomiques indépendantes, dans l'ordre attendu par l'original.
    """
    cleaned = strip_filler_words(text, qa_cfg.filler_patterns)
    return enforce_max_sentences(cleaned, qa_cfg.max_sentences)


# --- Pipeline de sanitisation TTS : une fonction atomique par étape ---------

def strip_markdown_code_blocks(text: str) -> str:
    import re
    text = re.sub(r'```.*?```', '', text, flags=re.DOTALL)
    text = re.sub(r'`[^`]*`', '', text)
    return text


def strip_markdown_emphasis(text: str) -> str:
    import re
    return re.sub(r'\*{1,3}|_{1,3}|~{1,2}', '', text)


def strip_markdown_headings(text: str) -> str:
    import re
    return re.sub(r'^\s*#{1,6}\s*', '', text, flags=re.MULTILINE)


def replace_web_addresses(text: str) -> str:
    import re
    return re.sub(r'https?://\S+|ftp://\S+', 'lien', text)


def strip_non_oral_punctuation(text: str) -> str:
    import re
    text = re.sub(r'^\s*[-•–—]\s+', '', text, flags=re.MULTILINE)
    text = re.sub(r'^\s*[\-|: ]{3,}\s*$', '', text, flags=re.MULTILINE)
    text = re.sub(r'\|', ' ', text)
    text = re.sub(r'[\\/@#$%^&{}\[\]<>=]', ' ', text)
    text = re.sub(r'[(){}\[\]]', ' ', text)
    text = re.sub(r'\.{2,}', ',', text)
    text = re.sub(r'\s*[–—]\s*', ', ', text)
    text = re.sub(r'\*+', '', text)
    text = re.sub(r'_+', ' ', text)
    return text


def collapse_newlines_and_spaces(text: str) -> str:
    import re
    text = re.sub(r'\n+', ' ', text)
    text = re.sub(r' {2,}', ' ', text)
    return text.strip()


# Pipeline ordonné, paramétrable : remplacer/réordonner cette liste suffit à
# changer le comportement de sanitize_tts() sans toucher à son code.
TTS_SANITIZE_PIPELINE: List[Callable[[str], str]] = [
    strip_markdown_code_blocks,
    strip_markdown_emphasis,
    strip_markdown_headings,
    replace_web_addresses,
    strip_non_oral_punctuation,
    collapse_newlines_and_spaces,
]


def sanitize_tts(
    text: str,
    *,
    pipeline: Sequence[Callable[[str], str]] = TTS_SANITIZE_PIPELINE,
    filler_patterns: Sequence[str] = FILLER_PATTERNS_FR,
) -> str:
    """Nettoie le texte avant synthèse vocale.

    1..6. Étapes Markdown / ponctuation / espaces, appliquées via `pipeline`
          (paramétrable, ordre conservé à l'identique de l'original).
    7.    Mots de remplissage, avec vérification de rendu : si le nettoyage
          efface tout le texte (sur-correction), on prononce l'original
          plutôt que de rester muet.
    """
    for step in pipeline:
        text = step(text)

    cleaned = strip_filler_words(text, filler_patterns)
    if cleaned:
        text = cleaned
    # sinon : le filtre a tout effacé (sur-correction) — on garde l'original.

    return text.strip()


# ============================================================================
# PatienceManager — retour sonore pendant les temps de traitement
# ----------------------------------------------------------------------------
# Stratégie à paliers calibrée sur la durée d'attente réelle, entièrement
# pilotée par PatienceConfig :
#
#   < level_short_s     : rien (imperceptible)
#   level_short..medium : signal d'ambiance discret seul
#   level_medium..long  : signal d'ambiance + courte phrase de transition
#   > level_very_long_s : signal grave + phrase "longue attente", puis rappel
#                          toutes les reminder_interval_s secondes
#
# Le suivi tourne dans un fil d'exécution dédié pendant l'appel bloquant
# au modèle de langage. Il s'arrête proprement (threading.Event) dès que
# le résultat est disponible.
# ============================================================================

class PatienceManager:
    """Pilote les signaux d'ambiance et les phrases de patience selon la durée réelle d'attente."""

    def __init__(self, io: "VoiceIO", config: Optional[PatienceConfig] = None) -> None:
        self.io = io
        self._cfg = config or PatienceConfig()
        self._stop_event = threading.Event()
        self._thread: Optional[threading.Thread] = None

    def start(self) -> None:
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop_event.set()
        if self._thread is not None:
            self._thread.join(timeout=2.0)
            self._thread = None

    # -- Étapes atomiques de la machine à paliers ---------------------------

    def _maybe_announce_medium(self, elapsed: float, announced: bool) -> bool:
        if elapsed >= self._cfg.level_medium_s and not announced:
            self.io.play_earcon("patience_short")
            return True
        return announced

    def _maybe_announce_long(self, elapsed: float, announced: bool) -> bool:
        if elapsed >= self._cfg.level_long_s and not announced:
            self.io.play_earcon("patience_medium")
            self.io.speak(pick("thinking_medium", self._cfg.phrase_bank), blocking=False)
            return True
        return announced

    def _maybe_announce_very_long(self, elapsed: float, announced: bool) -> bool:
        if elapsed >= self._cfg.level_very_long_s and not announced:
            self.io.play_earcon("patience_long")
            self.io.speak(pick("thinking_long", self._cfg.phrase_bank), blocking=False)
            return True
        return announced

    def _maybe_send_periodic_reminder(self, elapsed: float, start: float, very_long: bool) -> float:
        """Envoie un rappel périodique au-delà du seuil très long.
        Retourne le nouveau temps de référence `start` (inchangé si pas de rappel).
        """
        if very_long and elapsed >= self._cfg.level_very_long_s + self._cfg.reminder_interval_s:
            self.io.speak(pick("thinking_very_long", self._cfg.phrase_bank), blocking=False)
            # avancer `start` recule `elapsed` d'autant ; le signe inverse
            # ferait remonter elapsed et redéclencherait la phrase en boucle.
            return start + self._cfg.reminder_interval_s
        return start

    def _run(self) -> None:
        start = time.monotonic()
        announced_medium    = False
        announced_long      = False
        announced_very_long = False

        while not self._stop_event.is_set():
            elapsed = time.monotonic() - start

            announced_medium    = self._maybe_announce_medium(elapsed, announced_medium)
            announced_long      = self._maybe_announce_long(elapsed, announced_long)
            announced_very_long = self._maybe_announce_very_long(elapsed, announced_very_long)
            start = self._maybe_send_periodic_reminder(elapsed, start, announced_very_long)

            self._stop_event.wait(timeout=self._cfg.poll_interval_s)

    def run_with_patience(self, fn, *args, **kwargs):
        """Exécute fn(*args, **kwargs) en pilotant le retour sonore de patience."""
        self.start()
        try:
            return fn(*args, **kwargs)
        finally:
            self.stop()


# ============================================================================
# SupervisorLLM
# ============================================================================

class SupervisorLLM:
    """Analyse les fragments de narration et produit des décisions de supervision."""

    def __init__(
        self,
        config,
        *,
        supervisor_cfg: Optional[SupervisorConfig] = None,
        retry_cfg: Optional[RetryConfig] = None,
        endpoint_cfg: Optional[LlmEndpointConfig] = None,
    ) -> None:
        self._config = config
        self._cfg = supervisor_cfg or SupervisorConfig()
        self._retry_cfg = retry_cfg or RetryConfig()
        self._endpoint_cfg = endpoint_cfg or LlmEndpointConfig()
        self._lock = threading.Lock()

    def analyse(self, session: NarratorSession, new_chunk: str) -> SupervisorDecision:
        if self._config is None:
            return SupervisorDecision()

        user_msg = self._build_user_message(session, new_chunk)

        try:
            with self._lock:
                raw = self._call_llm(user_msg)
            return self._parse(raw)
        except Exception as exc:
            logger.warning("SupervisorLLM erreur : %s", exc)
            return SupervisorDecision()

    @staticmethod
    def _build_user_message(session: NarratorSession, new_chunk: str) -> str:
        return (
            "Thème du scénario : %s\n\n"
            "Contexte (narration précédente) :\n%s\n\n"
            "Nouveau fragment :\n%s"
        ) % (session.topic, session.context_window(), new_chunk)

    def _call_llm(self, user_msg: str) -> str:
        via_library = try_call_llm_via_library(
            system=self._cfg.system_prompt, user=user_msg,
            config=self._config, max_tokens=self._cfg.max_tokens,
        )
        if via_library is not None:
            return via_library

        # Appel direct compatible avec l'interface de l'API de langage
        return perform_chat_http_call(
            system=self._cfg.system_prompt, user=user_msg,
            config=self._config, max_tokens=self._cfg.max_tokens,
            endpoint_cfg=self._endpoint_cfg, timeout_s=self._cfg.call_timeout_s,
        )

    def _parse(self, raw: str) -> SupervisorDecision:
        obj = extract_first_json_object(raw)
        if obj is None:
            logger.warning("SupervisorLLM : structure JSON introuvable dans '%s'", raw[:120])
            return SupervisorDecision()
        try:
            dec = Decision(obj.get("decision", "CONTINUER").upper())
        except ValueError:
            dec = Decision.CONTINUER
        return SupervisorDecision(decision=dec, message=obj.get("message", "").strip())


# ============================================================================
# VoiceIO
# ============================================================================

class VoiceIO:
    """Couche basse — reconnaissance vocale et synthèse vocale.

    Principes fondamentaux
    ----------------------
    1. speak() est TOUJOURS bloquant dans le fil principal.
       Une synthèse non bloquante avant écoute = écho capturé par le moteur de
       reconnaissance.
    2. Le microphone n'est jamais ouvert pendant la synthèse vocale.
    3. L'enregistrement utilise la détection automatique de voix, pas une durée fixe.
    4. interrupt_and_speak() coupe l'audio en cours avant de parler (alertes STOP).
    5. play_earcon() est toujours non bloquant et très court (moins de 400 ms) :
       il ne doit jamais retarder le flux conversationnel.
    """

    def __init__(
        self,
        stt: Optional[SttConfig] = None,
        tts: Optional[TtsConfig] = None,
    ) -> None:
        self.stt_cfg = stt or SttConfig()
        self.tts_cfg = tts or TtsConfig()

        # Alias conservés pour compatibilité de lecture du code existant
        self.stt_backend = self.stt_cfg.backend
        self.tts_backend = self.tts_cfg.backend
        self.language    = self.stt_cfg.language

        self._recognizer    = None
        self._whisper_model = None
        self._tts_engine    = None
        self._coqui_model   = None
        self._lock_tts      = threading.Lock()

        self._init()

    # ------------------------------------------------------------------
    # Initialisation
    # ------------------------------------------------------------------

    def _init(self) -> None:
        self._init_stt()
        self._init_tts()
        logger.info(
            "VoiceIO prêt — Reconnaissance : %s | Synthèse : %s | Langue : %s",
            self.stt_backend, self.tts_backend, self.language,
        )

    def _init_stt(self) -> None:
        self._recognizer = self._build_recognizer()
        if self.stt_backend == "whisper":
            self._whisper_model = self._load_whisper()

    def _build_recognizer(self):
        try:
            import speech_recognition as sr
        except ImportError:
            raise RuntimeError(
                "Module SpeechRecognition manquant. "
                "Installez-le avec : pip install SpeechRecognition PyAudio"
            )
        recognizer = sr.Recognizer()
        recognizer.energy_threshold         = self.stt_cfg.energy_threshold
        recognizer.pause_threshold          = self.stt_cfg.silence_timeout
        recognizer.dynamic_energy_threshold = self.stt_cfg.dynamic_energy_threshold
        return recognizer

    def _load_whisper(self) -> object:
        try:
            from faster_whisper import WhisperModel
            logger.info("Chargement du modèle Faster Whisper '%s'...", self.stt_cfg.whisper_model)
            model = WhisperModel(
                self.stt_cfg.whisper_model,
                device="cpu",
                compute_type="int8",
            )
            logger.info("Faster Whisper prêt")
            return model
        except ImportError:
            raise RuntimeError(
                "Module faster-whisper manquant. Installez-le avec : pip install faster-whisper"
            )

    def _init_tts(self) -> None:
        chain = (
            [self.tts_cfg.backend]
            + [b for b in self.tts_cfg.fallback_chain if b != self.tts_cfg.backend]
        )
        backend_initializers = {
            "coqui":   self._init_coqui,
            "piper":   self._init_piper,
            "gtts":    self._init_gtts,
            "pyttsx3": self._init_pyttsx3,
        }
        for backend in chain:
            init_fn = backend_initializers.get(backend)
            if init_fn is None:
                continue
            try:
                init_fn()
                self.tts_backend = backend
                logger.info("Moteur de synthèse actif : %s", backend)
                return
            except Exception as exc:
                logger.warning(
                    "Moteur '%s' indisponible : %s — essai du suivant", backend, exc
                )

        raise RuntimeError(
            "Aucun moteur de synthèse vocale disponible. "
            "Installez au minimum : pip install coqui-tts sounddevice soundfile"
        )

    # ------------------------------------------------------------------
    # Initialisation Coqui VITS — voix neurale française hors ligne
    # ------------------------------------------------------------------

    def _init_coqui(self) -> None:
        try:
            from TTS.api import TTS as CoquiTTS
            import sounddevice  # noqa: F401
            import soundfile    # noqa: F401
        except ImportError:
            raise RuntimeError(
                "Module Coqui manquant. Installez-le avec : pip install coqui-tts sounddevice soundfile"
            )
        logger.info("Chargement de Coqui '%s'...", self.tts_cfg.coqui_model)
        self._coqui_model = CoquiTTS(
            model_name=self.tts_cfg.coqui_model,
            progress_bar=False,
            gpu=False,
        )
        logger.info("Coqui prêt")

    # ------------------------------------------------------------------
    # Initialisation Piper — voix neurale française hors ligne, très rapide
    # ------------------------------------------------------------------

    def _init_piper(self) -> None:
        try:
            import piper  # noqa: F401
        except ImportError:
            raise RuntimeError("Module piper-tts manquant. Installez-le avec : pip install piper-tts")
        logger.info("Piper disponible — modèle '%s'", self.tts_cfg.piper_model)

    # ------------------------------------------------------------------
    # Initialisation Google Synthèse vocale — en ligne
    # ------------------------------------------------------------------

    def _init_gtts(self) -> None:
        try:
            import gtts    # noqa: F401
            import pygame  # noqa: F401
        except ImportError:
            raise RuntimeError(
                "Modules gTTS ou pygame manquants. Installez-les avec : pip install gTTS pygame"
            )
        logger.info("Google Synthèse vocale initialisée")

    # ------------------------------------------------------------------
    # Initialisation pyttsx3 — solution de secours ultime
    # ------------------------------------------------------------------

    def _init_pyttsx3(self) -> None:
        try:
            import pyttsx3
        except ImportError:
            raise RuntimeError(
                "Module pyttsx3 manquant. Installez-le avec : pip install pyttsx3"
            )

        engine = pyttsx3.init()
        engine.setProperty("rate",   self.tts_cfg.speech_rate)
        engine.setProperty("volume", self.tts_cfg.volume)
        self._select_pyttsx3_french_voice(engine)
        self._tts_engine = engine
        logger.info("pyttsx3 initialisé (voix système)")

    @staticmethod
    def _select_pyttsx3_french_voice(engine) -> bool:
        """Sélectionne la meilleure voix française disponible par ordre de priorité.
        Retourne True si une voix française a été trouvée et appliquée.
        """
        for priority in ("fr_FR", "fr-FR", "french", "fr"):
            for v in engine.getProperty("voices"):
                name_lower = v.name.lower()
                id_lower   = v.id.lower()
                if priority.lower() in id_lower or priority.lower() in name_lower:
                    engine.setProperty("voice", v.id)
                    logger.info(
                        "pyttsx3 : voix française sélectionnée : %s (%s)", v.name, v.id
                    )
                    return True
        logger.warning(
            "Aucune voix française trouvée dans pyttsx3. "
            "Sur Linux : sudo apt install espeak-ng-data"
        )
        return False

    # ------------------------------------------------------------------
    # Synthèse vocale — TOUJOURS bloquante dans le fil principal
    # ------------------------------------------------------------------

    def interrupt_and_speak(self, text: str) -> None:
        """Coupe l'audio en cours PUIS parle. Réservé aux alertes STOP urgentes."""
        self._stop_audio()
        self.speak(text)

    def _stop_audio(self) -> None:
        """Arrête immédiatement la lecture audio (tous moteurs)."""
        try:
            if self.tts_backend in ("coqui", "piper"):
                import sounddevice as sd
                sd.stop()
            elif self.tts_backend == "gtts":
                try:
                    import pygame
                    if pygame.mixer.get_init():
                        pygame.mixer.music.stop()
                except Exception:
                    pass
        except Exception as exc:
            logger.debug("_stop_audio : %s", exc)

    def speak(self, text: str, *, blocking: bool = True) -> None:
        """Synthèse vocale en français natif.

        blocking=True (par défaut) : retourne APRÈS la fin de la lecture.
        blocking=False             : usage exceptionnel uniquement —
                                     par exemple, phrases de patience émises
                                     par PatienceManager pendant qu'un autre fil
                                     attend le modèle de langage.
        RÈGLE : ne JAMAIS appeler avec blocking=False juste avant écoute().
        """
        if not text or not text.strip():
            return
        text = sanitize_tts(text, filler_patterns=self.tts_cfg.filler_patterns)
        if not text:
            return
        logger.info("Synthèse [%s] : '%s'", self.tts_backend, text[:80])

        dispatch = {
            "coqui":   self._speak_coqui,
            "piper":   self._speak_piper,
            "gtts":    self._speak_gtts,
            "pyttsx3": self._speak_pyttsx3,
        }
        fn = dispatch.get(self.tts_backend)
        if fn is None:
            logger.error("Moteur de synthèse inconnu : %s", self.tts_backend)
            print("[Synthèse] " + text)
            return
        fn(text, blocking)

    # ------------------------------------------------------------------
    # Signaux d'ambiance — retour sonore court pendant les attentes
    # ------------------------------------------------------------------

    def play_earcon(self, profile: str) -> None:
        """Joue un signal d'ambiance court et non bloquant. Échec silencieux."""
        params = self.tts_cfg.earcon_profiles.get(profile)
        if params is None:
            return
        try:
            threading.Thread(
                target=self._play_earcon_sync, args=(params,), daemon=True
            ).start()
        except Exception as exc:
            logger.debug("play_earcon : %s", exc)

    def _play_earcon_sync(self, params: Tuple[float, float, float]) -> None:
        freq, duration, amplitude = params
        try:
            import sounddevice as sd
            sample_rate = self.tts_cfg.earcon_sample_rate
            n_samples = int(sample_rate * duration)
            tone = [
                amplitude * math.sin(2 * math.pi * freq * (i / sample_rate))
                for i in range(n_samples)
            ]
            sd.play(tone, sample_rate)
            sd.wait()
        except Exception as exc:
            logger.debug("Signal d'ambiance indisponible (%s), ignoré", exc)

    # ------------------------------------------------------------------
    # Atomes de lecture audio fichier -> haut-parleur, réutilisés par
    # les moteurs Coqui et Piper (même schéma : synthèse -> fichier wav
    # temporaire -> lecture sounddevice -> nettoyage).
    # ------------------------------------------------------------------

    def _read_wav(self, path: str):
        import soundfile as sf
        return sf.read(path, dtype="float32")

    def _play_wav_with_lock(self, data, sample_rate: int) -> None:
        import sounddevice as sd
        with self._lock_tts:
            sd.play(data, sample_rate)
            sd.wait()

    def _dispatch_playback(self, data, sample_rate: int, blocking: bool) -> None:
        if blocking:
            self._play_wav_with_lock(data, sample_rate)
        else:
            threading.Thread(
                target=self._play_wav_with_lock, args=(data, sample_rate), daemon=True
            ).start()

    @staticmethod
    def _cleanup_tmp_file(tmp_path: Optional[str]) -> None:
        if tmp_path and os.path.exists(tmp_path):
            try:
                os.unlink(tmp_path)
            except OSError:
                pass

    # ------------------------------------------------------------------
    # Moteur Coqui — référence qualité
    # ------------------------------------------------------------------

    def _speak_coqui(self, text: str, blocking: bool) -> None:
        """Synthèse Coqui (réseau de neurones) + lecture sounddevice.

        La lecture est sérialisée via self._lock_tts pendant toute sa durée
        réelle (y compris en non bloquant, via un fil dédié) : sans cela, un
        appel concurrent peut démarrer une nouvelle lecture sur le flux audio
        par défaut avant la fin de la précédente, qui est alors coupée net.
        """
        tmp_path: Optional[str] = None
        try:
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
                tmp_path = f.name

            with self._lock_tts:
                self._coqui_model.tts_to_file(text=text, file_path=tmp_path)

            data, sr = self._read_wav(tmp_path)
            self._dispatch_playback(data, sr, blocking)

        except Exception as exc:
            logger.error("Coqui erreur : %s", exc)
            print("[Synthèse] " + text)
        finally:
            self._cleanup_tmp_file(tmp_path)

    # ------------------------------------------------------------------
    # Moteur Piper — latence minimale
    # ------------------------------------------------------------------

    def _run_piper_cli(self, text: str, tmp_path: str) -> None:
        import subprocess
        result = subprocess.run(
            ["piper", "--model", self.tts_cfg.piper_model, "--output_file", tmp_path],
            input=text.encode("utf-8"),
            capture_output=True,
            timeout=self.tts_cfg.piper_timeout_s,
        )
        if result.returncode != 0:
            raise RuntimeError(
                "piper code de retour=%d : %s" % (
                    result.returncode, result.stderr.decode()
                )
            )

    def _speak_piper(self, text: str, blocking: bool) -> None:
        """Synthèse Piper (CLI externe) + lecture sounddevice.

        Lecture sérialisée via self._lock_tts pour toute sa durée réelle
        (cf. _speak_coqui) afin qu'un appel concurrent ne coupe pas une
        phrase en cours de diffusion.
        """
        tmp_path: Optional[str] = None
        try:
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
                tmp_path = f.name

            self._run_piper_cli(text, tmp_path)

            data, sr = self._read_wav(tmp_path)
            self._dispatch_playback(data, sr, blocking)

        except FileNotFoundError:
            logger.error("Exécutable 'piper' introuvable. pip install piper-tts")
            print("[Synthèse] " + text)
        except Exception as exc:
            logger.error("Piper erreur : %s", exc)
            print("[Synthèse] " + text)
        finally:
            self._cleanup_tmp_file(tmp_path)

    # ------------------------------------------------------------------
    # Moteur Google Synthèse vocale — en ligne
    # ------------------------------------------------------------------

    def _speak_gtts(self, text: str, blocking: bool) -> None:
        """Synthèse Google (gTTS) + lecture pygame.

        Robustesse :
        - Toute lecture (bloquante ou non) est sérialisée via self._lock_tts.
          Sans ce verrou, un appel concurrent (fil principal pendant que
          PatienceManager parle encore, ou deux rappels de patience rapprochés)
          réinitialise le mixeur en pleine lecture — la phrase précédente est
          coupée net.
        - Le fichier temporaire n'est supprimé qu'après la fin RÉELLE de la
          lecture (boucle get_busy()), jamais après un simple délai fixe.
        """
        def _play_and_cleanup() -> None:
            tmp_path: Optional[str] = None
            try:
                from gtts import gTTS
                import pygame

                tts = gTTS(text=text, lang=self.language, slow=False)
                with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
                    tmp_path = f.name
                tts.save(tmp_path)

                with self._lock_tts:
                    if pygame.mixer.get_init():
                        pygame.mixer.quit()
                    pygame.mixer.init(frequency=22050, size=-16, channels=1, buffer=512)
                    pygame.mixer.music.load(tmp_path)
                    pygame.mixer.music.play()
                    while pygame.mixer.music.get_busy():
                        time.sleep(0.05)
                    pygame.mixer.quit()

            except Exception as exc:
                logger.error("Google Synthèse vocale erreur : %s", exc)
                print("[Synthèse] " + text)
            finally:
                self._cleanup_tmp_file(tmp_path)

        if blocking:
            _play_and_cleanup()
        else:
            threading.Thread(target=_play_and_cleanup, daemon=True).start()

    # ------------------------------------------------------------------
    # Moteur pyttsx3 — solution de secours ultime
    # ------------------------------------------------------------------

    def _speak_pyttsx3(self, text: str, blocking: bool) -> None:
        """Synthèse pyttsx3 (solution de secours ultime).

        Le verrou est tenu pendant toute la durée réelle de runAndWait(),
        y compris en non bloquant (via un fil dédié) : le moteur pyttsx3
        n'est pas conçu pour des appels concurrents.
        """
        def _say_and_wait() -> None:
            with self._lock_tts:
                try:
                    self._tts_engine.say(text)
                    self._tts_engine.runAndWait()
                except Exception as exc:
                    logger.error("pyttsx3 erreur : %s", exc)
                    print("[Synthèse] " + text)

        if blocking:
            _say_and_wait()
        else:
            threading.Thread(target=_say_and_wait, daemon=True).start()

    # ------------------------------------------------------------------
    # Reconnaissance vocale — fragment avec détection automatique de voix
    # ------------------------------------------------------------------

    def _capture_audio(self, *, pause_threshold: float, phrase_time_limit: int, listen_timeout: float):
        """Capture brute du flux micro -> objet audio SpeechRecognition."""
        import speech_recognition as sr

        original = self._recognizer.pause_threshold
        self._recognizer.pause_threshold = pause_threshold
        try:
            with sr.Microphone() as src:
                logger.info(
                    "Écoute (silence=%.1fs, max=%ds)...",
                    pause_threshold, phrase_time_limit,
                )
                self._recognizer.adjust_for_ambient_noise(src, duration=self.stt_cfg.ambient_duration)
                return self._recognizer.listen(
                    src,
                    timeout=listen_timeout,
                    phrase_time_limit=phrase_time_limit,
                )
        finally:
            self._recognizer.pause_threshold = original

    @staticmethod
    def _audio_to_tmp_wav(audio) -> str:
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            tmp_path = f.name
            f.write(audio.get_wav_data())
        return tmp_path

    def listen_chunk(
        self,
        *,
        pause_threshold:   Optional[float] = None,
        phrase_time_limit: Optional[int]   = None,
        listen_timeout:    Optional[float] = None,
        initial_prompt:    Optional[str] = None,
    ) -> str:
        """Capture un fragment de parole et le transcrit.

        Les seuils non fournis sont pris dans self.stt_cfg (paramétrable).

        initial_prompt (Whisper uniquement) : biais lexical optionnel pour
        orienter la transcription vers un vocabulaire attendu. Ignoré sur le
        moteur Google.

        Retourne :
            Le texte transcrit (non vide).

        Lève :
            RuntimeError si la capture ou la transcription échoue,
            ou si aucune voix n'est détectée dans le délai imparti.
        """
        import speech_recognition as sr

        pause_threshold   = self.stt_cfg.silence_timeout if pause_threshold is None else pause_threshold
        phrase_time_limit = self.stt_cfg.phrase_time_limit if phrase_time_limit is None else phrase_time_limit
        listen_timeout    = self.stt_cfg.listen_timeout if listen_timeout is None else listen_timeout

        tmp_path: Optional[str] = None
        try:
            audio = self._capture_audio(
                pause_threshold=pause_threshold,
                phrase_time_limit=phrase_time_limit,
                listen_timeout=listen_timeout,
            )
            tmp_path = self._audio_to_tmp_wav(audio)

            if self.stt_backend == "whisper":
                return self._transcribe_whisper(tmp_path, initial_prompt=initial_prompt)
            else:
                return self._transcribe_google(audio)

        except sr.WaitTimeoutError as exc:
            raise RuntimeError("Aucune voix détectée dans le délai imparti") from exc

        finally:
            self._cleanup_tmp_file(tmp_path)

    def listen_short(self, question: str, timeout: float = 8.0, initial_prompt: Optional[str] = None) -> str:
        """Pose une question brève et attend une réponse courte.
        Retourne une chaîne vide en cas d'absence de réponse (aucune exception propagée).

        Utilise les mêmes seuils d'écoute que la boucle de questions-réponses
        (déjà fiables en usage réel) plutôt que des seuils plus courts : un silence
        de coupure trop bref clipe une prononciation hésitante (thème technique,
        mot inhabituel) ou un simple "oui" arrivant juste après la synthèse vocale.

        initial_prompt : transmis à Whisper pour biaiser la reconnaissance vers
        un vocabulaire attendu (cf. listen_chunk).
        """
        self.speak(question)
        self.speak(pick("listening", self.tts_cfg.phrase_bank))
        time.sleep(self.tts_cfg.settle_after_speak_s)  # laisse l'écho de la synthèse se dissiper
        try:
            return self.listen_chunk(
                pause_threshold=self.stt_cfg.silence_timeout,
                phrase_time_limit=self.stt_cfg.phrase_time_limit,
                listen_timeout=timeout,
                initial_prompt=initial_prompt,
            )
        except RuntimeError as exc:
            logger.info("listen_short : aucune réponse (%s)", exc)
            return ""

    def _transcribe_whisper(self, wav_path: str, initial_prompt: Optional[str] = None) -> str:
        try:
            segments_gen, info = self._whisper_model.transcribe(
                wav_path,
                language=self.language,
                beam_size=self.stt_cfg.whisper_beam_size,
                initial_prompt=initial_prompt,
            )
        except TypeError:
            # Repli : version de faster-whisper ne supportant pas initial_prompt
            logger.debug(
                "Whisper : 'initial_prompt' non supporté par cette version, "
                "repli sans biais lexical"
            )
            segments_gen, info = self._whisper_model.transcribe(
                wav_path,
                language=self.language,
                beam_size=self.stt_cfg.whisper_beam_size,
            )
        logger.debug(
            "Whisper : langue=%s (%.0f%%)",
            info.language, info.language_probability * 100,
        )
        text = " ".join(seg.text.strip() for seg in segments_gen).strip()
        if not text:
            raise RuntimeError("La reconnaissance vocale n'a produit aucun texte")
        logger.info("Fragment reconnu : '%s'", text[:100])
        return text

    def _transcribe_google(self, audio) -> str:
        import speech_recognition as sr
        lang = "fr-FR" if self.language == "fr" else (self.language + "-" + self.language.upper())
        try:
            text = self._recognizer.recognize_google(audio, language=lang)
            logger.info("Reconnaissance Google : '%s'", text[:100])
            return text
        except sr.UnknownValueError:
            raise RuntimeError("Reconnaissance Google : audio incompréhensible")
        except sr.RequestError as exc:
            raise RuntimeError("Reconnaissance Google : erreur de service : %s" % exc)

    # ------------------------------------------------------------------
    # Nettoyage
    # ------------------------------------------------------------------

    def close(self) -> None:
        self._stop_audio()
        if self._tts_engine is not None:
            try:
                with self._lock_tts:
                    self._tts_engine.stop()
            except Exception:
                pass
        logger.info("VoiceIO fermé")


# ============================================================================
# VRScenarioApp — orchestration principale
# ============================================================================

class VRScenarioApp:
    """
    Flux en deux phases :

    PHASE 1 — Génération et présentation du scénario
      - Saisie vocale du thème
      - Le modèle de langage génère un scénario structuré
      - Construction de la session de scénario
      - Lecture du résumé oral par synthèse vocale

    PHASE 2 — Questions et réponses supervisées
      - L'utilisateur pose librement ses questions à voix haute
      - Le modèle répond en s'appuyant sur le scénario généré
      - Le superviseur évalue chaque échange : CONTINUER / CONSEIL / STOP
      - Un mot de sortie clôt proprement la session

    Gestion de la patience
    ----------------------
    Toute attente potentiellement longue (génération de scénario, appel
    au modèle en questions-réponses) est encadrée par PatienceManager.

    Paramétrage de la discussion de scénario
    -----------------------------------------
    La stratégie d'obtention d'une réponse Q&R est une liste ordonnée de
    fonctions atomiques (self._answer_strategies), chacune tentée jusqu'à
    succès. Pour remplacer entièrement la logique de discussion du scénario,
    il suffit de fournir config.qa.discuss_scenario_fn : la stratégie
    "personnalisée" est alors essayée en premier.
    """

    def __init__(self, io: VoiceIO, config: Optional[AppConfig] = None) -> None:
        self.io = io
        self.cfg = config or AppConfig()
        self.patience = PatienceManager(io, self.cfg.patience)

        # Chaîne de stratégies de réponse Q&R, dans l'ordre de tentative.
        # Chaque stratégie est une fonction atomique (question, session, config) -> Optional[str].
        self._answer_strategies: List[Callable[[str, Any, Any], Optional[str]]] = [
            self._answer_via_custom_fn,
            self._answer_via_library,
            self._answer_via_direct_llm,
        ]

    def run(self) -> None:
        self._welcome()
        topic      = self._ask_topic()
        config     = self._setup_llm()
        supervisor = SupervisorLLM(
            config,
            supervisor_cfg=self.cfg.supervisor,
            retry_cfg=self.cfg.retry,
            endpoint_cfg=LlmEndpointConfig(),
        )

        # -- Phase 1 : génération et présentation -------------------------
        scenario_session = self._generate_and_announce(topic, config, transcription=topic)

        # -- Phase 2 : questions-réponses supervisées ---------------------
        self._qa_loop(scenario_session, supervisor, config)

        self._goodbye()

    # ------------------------------------------------------------------
    # Phase 1 : génération du scénario
    # ------------------------------------------------------------------

    def _welcome(self) -> None:
        print("\n" + "=" * 60)
        print("  APPLICATION VOCALE — SCÉNARIOS DE FORMATION EN RÉALITÉ VIRTUELLE")
        print("=" * 60)
        self.io.speak(
            "Bienvenue dans votre assistant vocal de scénarios de formation. "
            "Je vais générer un scénario à partir du thème que vous me donnerez, "
            "vous en présenter les grandes lignes, "
            "puis répondre à vos questions. "
            "Dites terminer à tout moment pour clore la session."
        )

    def _capture_topic_attempt(self, prompt: str) -> str:
        """Tente une capture du thème ; absorbe toute erreur inattendue de la
        couche vocale (microphone, moteur STT) sans interrompre la session."""
        try:
            return self.io.listen_short(prompt, initial_prompt=self.cfg.stt.topic_prompt_bias)
        except Exception as exc:
            logger.warning("Capture du thème échouée : %s", exc)
            return ""

    def _ask_topic(self) -> str:
        """Capture le thème par la voix avec confirmation orale explicite.

        Stratégie (paramétrée par self.cfg.topic) :
          1. Capture du thème (écoute courte, déjà tolérante au silence).
          2. Confirmation orale explicite ("Le thème retenu est X, correct ?").
          3. Nouvelle tentative si infirmé, absent ou ambigu — jusqu'à
             cfg.topic.max_attempts.
          4. Repli sur cfg.topic.default_fallback_topic si aucune confirmation
             n'est obtenue (dégradation silencieuse).
        """
        topic_cfg = self.cfg.topic
        prompt = topic_cfg.initial_prompt_text

        for attempt in range(1, topic_cfg.max_attempts + 1):
            text = self._capture_topic_attempt(prompt)

            if text and self._confirm_topic(text):
                self.io.speak("Très bien. Le thème retenu est : " + text + ".")
                logger.info("Thème confirmé : '%s'", text)
                print("\nThème : " + text)
                return text

            logger.info(
                "Thème non confirmé (tentative %d/%d) : '%s'",
                attempt, topic_cfg.max_attempts, text,
            )
            if attempt < topic_cfg.max_attempts:
                prompt = topic_cfg.retry_prompt_text
                self.io.speak("D'accord, reprenons.")

        text = topic_cfg.default_fallback_topic
        self.io.speak(
            "Je n'arrive pas à confirmer le thème. "
            "Je vais utiliser " + text + " par défaut."
        )
        logger.info("Thème : repli par défaut '%s'", text)
        print("\nThème : " + text)
        return text

    def _confirm_topic(self, topic: str) -> bool:
        """Demande une confirmation orale explicite du thème compris.

        Un "oui"/"non" isolé est plus difficile à transcrire correctement
        qu'une phrase complète : on retente donc la question de confirmation
        elle-même, jusqu'à cfg.topic.confirm_max_attempts fois, plutôt que de
        forcer l'utilisateur à reprononcer tout le thème pour un simple aléa
        de reconnaissance sur "oui".
        """
        topic_cfg = self.cfg.topic
        question = "Le thème retenu est : " + topic + ". Est-ce correct ? Dites oui ou non."

        for attempt in range(1, topic_cfg.confirm_max_attempts + 1):
            answer = self._capture_yesno_attempt(question)

            if any(w in answer for w in topic_cfg.confirm_no_words):
                return False
            if any(w in answer for w in topic_cfg.confirm_yes_words):
                return True

            if attempt < topic_cfg.confirm_max_attempts:
                question = "Je n'ai pas compris. Dites simplement oui, ou non."

        return False

    def _capture_yesno_attempt(self, question: str) -> str:
        try:
            return self.io.listen_short(
                question, initial_prompt=self.cfg.stt.yesno_prompt_bias
            ).lower()
        except Exception as exc:
            logger.debug("_capture_yesno_attempt : %s", exc)
            return ""

    def _generate_and_announce(self, topic: str, config, transcription: str = "") -> "ScenarioSession | None":
        """
        Appelle le modèle pour générer le scénario, construit la session,
        et lit le résumé oral. Retourne None si la génération échoue (les
        questions-réponses restent possibles).

        La génération peut prendre plusieurs secondes : elle est encadrée par
        PatienceManager.
        """
        print("\nGénération du scénario en cours…")

        scenario_json, scenario_text = self._run_scenario_generation(topic, config, transcription=transcription)

        if not scenario_json and not scenario_text:
            self.io.speak(
                "La génération du scénario n'a pas abouti. "
                "Vous pouvez néanmoins me poser vos questions directement."
            )
            return None

        session = self._build_scenario_session(topic, scenario_json, scenario_text)
        self._announce_scenario(scenario_json, scenario_text)
        return session

    def _run_scenario_generation(self, topic: str, config, transcription: str = "") -> Tuple[Dict[str, Any], str]:
        """Exécute la génération du scénario sous supervision de PatienceManager."""
        result_holder: Dict[str, Any] = {"json": {}, "text": ""}

        def _do_generate():
            result_holder["json"], result_holder["text"] = self._generate_scenario(topic, config, transcription=transcription)

        self.patience.run_with_patience(_do_generate)
        return result_holder["json"], result_holder["text"]

    def _generate_scenario(self, topic: str, config, transcription: str = "") -> Tuple[Dict[str, Any], str]:
        """Tente la génération via la bibliothèque, puis l'appel direct au modèle."""
        try:
            from vr_scenario_lib.scenario import generate_scenario as lib_generate
            result = lib_generate(topic=topic, llm_config=config, transcription=transcription)
            if isinstance(result, tuple):
                scenario_text, scenario_json = result[0], result[1]
            else:
                scenario_text = getattr(result, "text", str(result))
                scenario_json = getattr(result, "json", {})
            logger.info(
                "Scénario généré via la bibliothèque (%d caractères)", len(scenario_text)
            )
            return scenario_json, scenario_text
        except Exception as exc:
            logger.warning("Bibliothèque indisponible : %s — génération directe", exc)
            return self._generate_via_llm(topic, config)

    @staticmethod
    def _build_scenario_session(topic: str, scenario_json: Dict[str, Any], scenario_text: str):
        now = datetime.now(timezone.utc).isoformat()
        try:
            from vr_scenario_lib.scenario_store import ScenarioSession
            session = ScenarioSession(
                scenario_id   = str(uuid.uuid4()),
                topic         = topic,
                scenario_text = scenario_text,
                scenario_json = scenario_json,
                created_at    = now,
                updated_at    = now,
            )
            logger.info("Session créée (identifiant=%s)", session.scenario_id)
            return session
        except Exception as exc:
            logger.warning("Création de session impossible : %s", exc)
            return None

    def _generate_via_llm(self, topic: str, config) -> Tuple[Dict[str, Any], str]:
        """Appel direct au modèle pour générer le scénario.
        Retourne ({}, "") en cas d'échec, via le scénario statique de repli.
        """
        if config is None:
            return self._fallback_static_scenario(topic)

        user_msg = "Génère un scénario de formation en réalité virtuelle sur le thème : " + topic

        try:
            raw = self._call_llm_raw(
                system     = self.cfg.scenario_gen.system_prompt,
                user       = user_msg,
                config     = config,
                max_tokens = self.cfg.scenario_gen.max_tokens,
            )
        except Exception as exc:
            logger.error("Génération par le modèle échouée : %s", exc)
            return self._fallback_static_scenario(topic)

        try:
            obj = extract_first_json_object(raw)
            if obj is None:
                raise ValueError("Structure JSON introuvable")
        except Exception as exc:
            logger.error("Analyse du scénario échouée : %s | brut=%s", exc, raw[:200])
            return self._fallback_static_scenario(topic)

        text = self._json_to_text(obj, topic)
        return obj, text

    @staticmethod
    def _json_to_text(obj: Dict[str, Any], topic: str) -> str:
        """Convertit le scénario structuré en texte lisible."""
        lines = ["# SCÉNARIO DE FORMATION — " + topic.upper(), ""]
        titre = obj.get("titre", topic)
        lines += ["## " + titre, ""]

        objectifs = obj.get("objectifs", [])
        if objectifs:
            lines.append("### Objectifs")
            for o in objectifs:
                lines.append("- " + str(o))
            lines.append("")

        for etape in obj.get("grandes_lignes", []):
            num    = etape.get("etape", "")
            titre_e = etape.get("titre", "")
            desc   = etape.get("description", "")
            lines.append("### Étape %s : %s" % (num, titre_e))
            lines.append(desc)
            lines.append("")

        procs = obj.get("procedures_cles", [])
        if procs:
            lines.append("### Procédures clés")
            for p in procs:
                lines.append("- " + str(p))
            lines.append("")

        vigilance = obj.get("points_vigilance", [])
        if vigilance:
            lines.append("### Points de vigilance")
            for v in vigilance:
                lines.append("- " + str(v))
            lines.append("")

        return "\n".join(lines)

    @staticmethod
    def _fallback_static_scenario(topic: str) -> Tuple[Dict[str, Any], str]:
        """Scénario minimal si le modèle de langage est inaccessible."""
        obj = {
            "titre": "Scénario " + topic,
            "objectifs": [
                "Comprendre les principes fondamentaux de " + topic,
                "Maîtriser les procédures de sécurité essentielles",
                "Réagir de façon appropriée aux situations d'urgence",
            ],
            "grandes_lignes": [
                {
                    "etape": 1,
                    "titre": "Préparation",
                    "description": "Vérifier les équipements et les protections individuelles avant toute intervention.",
                },
                {
                    "etape": 2,
                    "titre": "Intervention",
                    "description": "Appliquer les procédures standard en respectant les consignes de sécurité.",
                },
                {
                    "etape": 3,
                    "titre": "Clôture",
                    "description": "Consigner les actions effectuées et signaler tout incident survenu.",
                },
            ],
            "procedures_cles": [
                "Vérifier les équipements avant toute intervention",
                "Respecter les périmètres de sécurité",
                "Alerter la hiérarchie en cas d'incident",
            ],
            "points_vigilance": [
                "Ne jamais intervenir seul",
                "Toujours porter les protections adaptées à la situation",
            ],
            "resume_oral": (
                "Ce scénario porte sur le thème " + topic + ". "
                "Il se déroule en trois étapes : la préparation du matériel, "
                "l'intervention selon les procédures standard, "
                "et la clôture avec consignation des actions effectuées."
            ),
        }
        text = VRScenarioApp._json_to_text(obj, topic)
        return obj, text

    def _print_scenario_debug(self, scenario_json: Dict[str, Any], scenario_text: str) -> None:
        print("\n" + "=" * 60)
        print("  SCÉNARIO TEXTUEL")
        print("=" * 60)
        print(scenario_text)
        print("=" * 60)
        print("\n" + "=" * 60)
        print("  SCÉNARIO GÉNÉRÉ (JSON)")
        print("=" * 60)
        print(json.dumps(scenario_json, indent=2, ensure_ascii=False))
        print("=" * 60 + "\n")

    @staticmethod
    def _build_oral_summary(scenario_json) -> str:
        if isinstance(scenario_json, list):
            if not scenario_json:
                return "Le scénario vient d'être généré, mais il est vide."
            scenario_json = scenario_json[0] if isinstance(scenario_json[0], dict) else {}
        if not isinstance(scenario_json, dict):
            return "Le scénario vient d'être généré."
        resume = scenario_json.get("resume_oral", "")
        if resume:
            return resume
        titre = scenario_json.get("titre", "le scénario")
        etapes = scenario_json.get("grandes_lignes", [])
        if etapes:
            noms = ", ".join(str(e.get("titre", "")) for e in etapes[:4])
            return (
                "Le scénario intitulé " + titre
                + " se déroule en " + str(len(etapes))
                + " étapes : " + noms + "."
            )
        return "Le scénario " + titre + " vient d'être généré."

    def _announce_scenario(self, scenario_json, scenario_text: str) -> None:
        """Présente les grandes lignes du scénario à voix haute."""
        self._print_scenario_debug(scenario_json, scenario_text)

        if isinstance(scenario_json, list):
            if not scenario_json:
                scenario_json = {}
            elif isinstance(scenario_json[0], dict):
                scenario_json = scenario_json[0]
            else:
                scenario_json = {}

        resume = self._build_oral_summary(scenario_json)
        self.io.speak("Voici les grandes lignes de votre scénario.")
        self.io.speak(resume)

        vigilance = scenario_json.get("points_vigilance", []) if isinstance(scenario_json, dict) else []
        if vigilance:
            points = " et ".join(vigilance[:3])
            self.io.speak("Les points de vigilance à retenir sont : " + points + ".")

        self.io.speak(
            "Le scénario est prêt. "
            "Posez-moi vos questions quand vous voulez. "
            "Dites terminer pour clore la session."
        )

    # ------------------------------------------------------------------
    # Phase 2 : questions-réponses supervisées
    # ------------------------------------------------------------------

    def _is_exit_word(self, question: str) -> bool:
        return any(w in question.lower() for w in self.cfg.exit.exit_words)

    def _handle_qa_timeout(self, consecutive_timeouts: int, exc: Exception) -> Tuple[int, bool]:
        """Traite un timeout d'écoute en Q&R.
        Retourne (nouveau_compteur, doit_continuer_la_boucle).
        """
        qa_cfg = self.cfg.qa
        consecutive_timeouts += 1
        logger.info(
            "Délai Q&R %d/%d : %s", consecutive_timeouts, qa_cfg.max_timeouts, exc
        )

        if consecutive_timeouts >= qa_cfg.max_timeouts:
            if self._ask_continue_qa():
                return 0, True
            return consecutive_timeouts, False
        elif consecutive_timeouts == qa_cfg.soft_nudge_at:
            self.io.speak(pick("soft_nudge", self.cfg.tts.phrase_bank))
        return consecutive_timeouts, True

    def _process_supervision(self, narrator: NarratorSession, supervisor: SupervisorLLM,
                              question: str, answer: str) -> bool:
        """Évalue l'échange via le superviseur et agit selon sa décision.
        Retourne False si la session Q&R doit s'arrêter.
        """
        exchange = "Question : " + question + "\nRéponse : " + answer
        decision = supervisor.analyse(narrator, exchange)
        logger.info(
            "Superviseur Q&R : %s | '%s'",
            decision.decision.value,
            decision.message[:60] if decision.message else "",
        )

        if decision.decision == Decision.CONSEIL:
            print("\n[CONSEIL] " + decision.message)
            self.io.speak(decision.message)

        elif decision.decision == Decision.STOP:
            print("\n[STOP] " + decision.message)
            self.io.interrupt_and_speak(decision.message)
            if not self._handle_stop_qa():
                return False

        return True

    def _qa_loop(
        self,
        scenario_session,   # ScenarioSession | None
        supervisor: SupervisorLLM,
        config,
    ) -> None:
        """Boucle de questions et réponses supervisées.

        Gestion du silence en trois niveaux :
          Niveau 1 — silence léger    : on relance l'écoute sans rien dire
          Niveau 2 — relance douce    : après le premier délai, une phrase
                                        courte rassure sans interroger
          Niveau 3 — silence prolongé : après plusieurs délais, question
                                        explicite pour continuer ou terminer
        """
        print("\n" + "-" * 60)
        print("[ SESSION DE QUESTIONS — posez vos questions ]")
        print("-" * 60)

        narrator = NarratorSession(
            topic=scenario_session.topic if scenario_session else "général"
        )
        consecutive_timeouts = 0

        while True:
            # ---- 1. Capture de la question ---------------------------------
            self.io.speak(pick("listening", self.cfg.tts.phrase_bank))
            try:
                question = self.io.listen_chunk()
                consecutive_timeouts = 0
            except RuntimeError as exc:
                consecutive_timeouts, keep_going = self._handle_qa_timeout(consecutive_timeouts, exc)
                if not keep_going:
                    break
                continue

            # ---- 2. Détection d'un mot de sortie ---------------------------
            if self._is_exit_word(question):
                print("\nSortie Q&R : '%s'" % question)
                break

            print("\n[Question] " + question)
            narrator.add_chunk(question)

            # ---- 3. Réponse du modèle (avec patience) ----------------------
            answer = self.patience.run_with_patience(
                self._get_answer, question, scenario_session, config
            )
            print("[Réponse] " + answer)
            self.io.speak(answer)

            # ---- 4. Supervision de l'échange -------------------------------
            if not self._process_supervision(narrator, supervisor, question, answer):
                break

    # ------------------------------------------------------------------
    # Obtention de la réponse Q&R — chaîne de stratégies paramétrable
    # ------------------------------------------------------------------
    # Chaque stratégie est une fonction atomique indépendante. La chaîne est
    # parcourue dans l'ordre jusqu'à ce qu'une stratégie renvoie une réponse
    # exploitable. Pour paramétrer entièrement la discussion de scénario,
    # fournir AppConfig.qa.discuss_scenario_fn : voir _answer_via_custom_fn.
    # ------------------------------------------------------------------

    def _answer_via_custom_fn(self, question: str, scenario_session, config) -> Optional[str]:
        """Stratégie injectée par l'appelant (paramétrage explicite demandé :
        'le scénario discuter soit paramétrable'). Signature attendue :
        fn(session, user_message, llm_config) -> str.
        """
        fn = self.cfg.qa.discuss_scenario_fn
        if fn is None:
            return None
        try:
            reply = fn(scenario_session, question, config)
            if reply and reply.strip():
                return postprocess_qa_answer(reply.strip(), self.cfg.qa)
        except Exception as exc:
            logger.warning("discuss_scenario_fn personnalisée en erreur : %s — repli", exc)
        return None

    def _answer_via_library(self, question: str, scenario_session, config) -> Optional[str]:
        """Stratégie par défaut : vr_scenario_lib.scenario.discuss_scenario."""
        if scenario_session is None or config is None:
            return None
        try:
            from vr_scenario_lib.scenario import discuss_scenario
            reply = discuss_scenario(
                session      = scenario_session,
                user_message = question,
                llm_config   = config,
            )
            if reply and reply.strip():
                return postprocess_qa_answer(reply.strip(), self.cfg.qa)
        except Exception as exc:
            logger.warning("discuss_scenario erreur : %s — appel direct", exc)
        return None

    def _answer_via_direct_llm(self, question: str, scenario_session, config) -> Optional[str]:
        """Stratégie de repli : appel direct au modèle avec contexte du scénario."""
        if config is None:
            return None
        context = (
            scenario_session.scenario_text[: self.cfg.qa.scenario_context_chars]
            if scenario_session and scenario_session.scenario_text
            else ""
        )
        user_msg = (
            ("Contexte du scénario :\n" + context + "\n\n" if context else "")
            + "Question de l'apprenant : " + question
        )
        try:
            reply = self._call_llm_raw(
                system     = self.cfg.qa.system_prompt,
                user       = user_msg,
                config     = config,
                max_tokens = self.cfg.qa.max_tokens,
            ).strip()
            return postprocess_qa_answer(reply, self.cfg.qa)
        except Exception as exc:
            logger.error("Appel direct Q&R erreur : %s", exc)
        return None

    def _get_answer(self, question: str, scenario_session, config) -> str:
        """
        Obtient une réponse du modèle à la question posée, en essayant
        chaque stratégie de self._answer_strategies dans l'ordre, jusqu'à
        succès. Priorité : fonction personnalisée injectée, puis
        discuss_scenario() de la bibliothèque, puis appel direct, puis
        message de repli.
        """
        for strategy in self._answer_strategies:
            answer = strategy(question, scenario_session, config)
            if answer is not None:
                return answer
        return self.cfg.qa.fallback_message

    # ------------------------------------------------------------------
    # Appel unifié au modèle de langage — bibliothèque, puis HTTP + retry
    # ------------------------------------------------------------------

    def _call_llm_raw(self, *, system: str, user: str, config, max_tokens: int) -> str:
        """Appel unifié au modèle de langage : bibliothèque, puis appel direct
        avec retry (cf. call_with_retry). Lève RuntimeError si toutes les
        tentatives échouent, pour que l'appelant applique son propre repli.
        """
        via_library = try_call_llm_via_library(
            system=system, user=user, config=config, max_tokens=max_tokens,
        )
        if via_library is not None:
            return via_library

        import urllib.error

        def _attempt() -> str:
            return perform_chat_http_call(
                system=system, user=user, config=config, max_tokens=max_tokens,
                endpoint_cfg=LlmEndpointConfig(), timeout_s=self.cfg.retry.call_timeout_s,
            )

        def _on_failed(attempt: int, total: int, exc: Exception) -> None:
            logger.warning("Appel LLM échoué (tentative %d/%d) : %s", attempt, total, exc)

        return call_with_retry(
            _attempt,
            retry_cfg=self.cfg.retry,
            retryable_exceptions=(urllib.error.URLError, TimeoutError, ValueError, KeyError),
            on_attempt_failed=_on_failed,
        )

    # ------------------------------------------------------------------
    # Fonctions auxiliaires
    # ------------------------------------------------------------------

    def _ask_continue_qa(self) -> bool:
        text = self.io.listen_short(pick("no_response_continue_check", self.cfg.tts.phrase_bank))
        if not text:
            return False
        return any(
            w in text.lower()
            for w in {"oui", "yes", "continuer", "continue", "si", "d'accord", "bien sûr"}
        )

    def _handle_stop_qa(self) -> bool:
        """Pause après une alerte STOP en phase questions-réponses. Retourne True pour reprendre."""
        self.io.speak(
            "La session est interrompue suite à cette alerte. "
            "Dites reprendre pour continuer vos questions, "
            "ou terminer pour clore la session."
        )
        text = ""
        try:
            text = self.io.listen_chunk(
                pause_threshold   = 2.0,
                phrase_time_limit = 10,
                listen_timeout    = 12,
            )
        except RuntimeError:
            pass
        if any(w in text.lower() for w in {"reprendre", "continuer", "oui", "yes", "d'accord"}):
            self.io.speak("Très bien. Je reste à l'écoute de vos questions.")
            return True
        return False

    def _goodbye(self) -> None:
        self.io.speak(
            "Merci pour cette session de formation. "
            "J'espère que ce scénario vous a été utile. "
            "À très bientôt."
        )
        print("\nAu revoir !\n")

    # ------------------------------------------------------------------
    # Configuration du modèle de langage
    # ------------------------------------------------------------------

    def _setup_llm(self):
        try:
            from vr_scenario_lib.config import build_llm_config
            return build_llm_config()
        except Exception as exc:
            logger.warning(
                "Configuration du modèle indisponible : %s — mode dégradé (scénarios statiques)",
                exc,
            )
            return None


# ============================================================================
# Interface en ligne de commande
# ============================================================================

def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description=(
            "Application vocale de supervision de scénarios de formation en réalité virtuelle"
        ),
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    p.add_argument(
        "--stt-backend", default="whisper", choices=["whisper", "google"],
        help="Moteur de reconnaissance vocale.",
    )
    p.add_argument(
        "--tts-backend", default=TTS_DEFAULT_BACKEND,
        choices=["coqui", "piper", "gtts", "pyttsx3"],
        help=(
            "Moteur de synthèse vocale. "
            "Les options 'coqui' et 'piper' fonctionnent entièrement hors ligne."
        ),
    )
    p.add_argument(
        "--language", default="fr",
        help="Code de langue au format ISO 639-1 (fr par défaut).",
    )
    p.add_argument(
        "--whisper-model", default=WHISPER_DEFAULT_MODEL,
        choices=["tiny", "base", "small", "medium", "large"],
        help="Taille du modèle Whisper. L'option 'small' est recommandée pour le français.",
    )
    p.add_argument(
        "--coqui-model", default=COQUI_MODEL_FR,
        help="Identifiant du modèle Coqui.",
    )
    p.add_argument(
        "--piper-model", default=PIPER_MODEL_FR,
        help="Nom du modèle Piper (exemple : fr_FR-tom-medium).",
    )
    p.add_argument(
        "--debug", action="store_true",
        help="Active les journaux de débogage complets.",
    )
    return p.parse_args()


def build_voice_io(config: AppConfig) -> VoiceIO:
    """Construit VoiceIO à partir de la configuration agrégée."""
    return VoiceIO(stt=config.stt, tts=config.tts)


def main(*, discuss_scenario_fn: Optional[Callable[[Any, str, Any], str]] = None) -> None:
    """Point d'entrée.

    discuss_scenario_fn : point d'extension explicite pour paramétrer la
    discussion de scénario sans modifier le code (cf. QaConfig.discuss_scenario_fn).
    """
    args = _parse_args()
    config = build_app_config(args, discuss_scenario_fn=discuss_scenario_fn)
    if config.debug:
        logging.getLogger().setLevel(logging.DEBUG)

    io = build_voice_io(config)
    app = VRScenarioApp(io, config)
    try:
        app.run()
    except KeyboardInterrupt:
        print("\nSession interrompue par l'utilisateur.")
    finally:
        io.close()


if __name__ == "__main__":
    main()