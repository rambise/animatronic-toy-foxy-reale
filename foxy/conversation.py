"""Loop di conversazione completo di Cassidy.

Uso:
    python -m foxy.conversation

Quando qualcuno si avvicina (sensore di presenza), Cassidy:
1. prova a riconoscere chi e' dal volto e lo saluta lei per prima, di
   sua iniziativa, se e' qualcuno che conosce
2. ascolta e risponde quando le parli
3. se resta li' vicino senza parlarle per un po', dice qualcosa di sua
   iniziativa invece di stare in silenzio

Le risposte arrivano dal cervello remoto condiviso col bot Telegram
"Toy Foxy" (foxy/brain_client.py): stessa personalita', stessi mood,
e la stessa memoria se hai configurato BRAIN_CHAT_ID. Il server genera
gia' l'audio della risposta - non serve Piper per questa modalita'.

In ogni risposta, Cassidy fa anche un piccolo gesto con la testa in base
all'emozione (mood) della risposta.

Richiede che tu abbia gia':
- addestrato il riconoscimento facciale (foxy.train_face) - opzionale
- addestrato il riconoscimento vocale (foxy.train_voice) - opzionale
- un file robot_key.txt nella radice del progetto con la chiave del robot
- Vosk e ffmpeg installati e configurati (vedi README)
"""
import time

import cv2

from foxy import config
from foxy.actuators import HeadServo
from foxy.brain_client import BrainClient, play_audio
from foxy.face_id import FaceIdentifier
from foxy.sensors import PresenceSensor
from foxy.speech_to_text import SpeechToText
from foxy.voice_id import VoiceIdentifier


def _snapshot_face_name(face_identifier: FaceIdentifier):
    cam = cv2.VideoCapture(config.CAMERA_INDEX)
    try:
        ok, frame = cam.read()
    finally:
        cam.release()
    if not ok:
        return None
    name, _ = face_identifier.identify(frame)
    return name


def _identify_speaker(face_identifier, voice_identifier, audio):
    speaker_name = None
    if face_identifier.is_trained:
        speaker_name = _snapshot_face_name(face_identifier)
    if (not speaker_name or speaker_name == "sconosciuto") and voice_identifier.is_trained:
        voice_name, _ = voice_identifier.identify(audio, config.VOICE_SAMPLE_RATE)
        speaker_name = voice_name or speaker_name
    return speaker_name


def _speak(brain, head, prompt, speaker_name):
    spoken_text, emotion, audio_b64 = brain.reply(prompt, speaker_name)
    if not spoken_text and not audio_b64:
        return
    print(f"Cassidy: {spoken_text} [{emotion}]")
    play_audio(audio_b64)
    head.express_emotion(emotion)


def run():
    presence = PresenceSensor()
    head = HeadServo()
    brain = BrainClient()
    stt = SpeechToText()
    face_identifier = FaceIdentifier()
    voice_identifier = VoiceIdentifier()

    print("Cassidy e' pronta a chiacchierare. In ascolto sul sensore di presenza...")

    was_near = False
    greeted_name = None
    last_interaction = 0.0

    try:
        while True:
            near = presence.is_someone_near()

            if not near:
                if was_near:
                    # la persona se n'e' andata: al prossimo arrivo la saluta di nuovo
                    greeted_name = None
                was_near = False
                time.sleep(0.2)
                continue

            if not was_near:
                was_near = True
                last_interaction = time.time()
                speaker_name = (
                    _snapshot_face_name(face_identifier) if face_identifier.is_trained else None
                )
                if speaker_name and speaker_name != "sconosciuto" and speaker_name != greeted_name:
                    greeted_name = speaker_name
                    print(f"Cassidy riconosce {speaker_name}: lo saluta lei per prima.")
                    greeting_prompt = (
                        f"[Si e' appena avvicinato/a {speaker_name}. Salutalo/a tu per prima, "
                        "spontaneamente, con una battuta o una domanda breve - non aspettare "
                        "che parli per primo/a.]"
                    )
                    _speak(brain, head, greeting_prompt, speaker_name)
                    last_interaction = time.time()

            text, audio = stt.listen_and_transcribe(
                max_wait_for_speech_s=config.CHAT_LISTEN_TIMEOUT_S
            )

            if text:
                speaker_name = _identify_speaker(face_identifier, voice_identifier, audio)
                print(f"[{speaker_name or 'sconosciuto'}] {text}")
                _speak(brain, head, text, speaker_name)
                last_interaction = time.time()
                continue

            if (time.time() - last_interaction) > config.CHAT_IDLE_COMMENT_AFTER_S:
                print("Silenzio prolungato: Cassidy dice qualcosa di sua iniziativa.")
                idle_prompt = (
                    "[E' da un po' che la persona e' li' vicino ma nessuno ti parla. Di' "
                    "qualcosa di tua iniziativa, breve e spontanea: un'osservazione, una "
                    "domanda, una battuta sui videogiochi, quello che ti viene.]"
                )
                _speak(brain, head, idle_prompt, None)
                last_interaction = time.time()
    except KeyboardInterrupt:
        print("Arresto di Cassidy...")
    finally:
        presence.close()
        head.close()


if __name__ == "__main__":
    run()
