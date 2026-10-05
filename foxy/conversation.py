"""Loop di conversazione completo di Foxy.

Uso:
    python -m foxy.conversation

Quando qualcuno si avvicina (sensore di presenza), Foxy:
1. prova a riconoscere chi e' dal volto e lo saluta lei per prima, di
   sua iniziativa, se e' qualcuno che conosce
2. ascolta e risponde quando le parli
3. se resta li' vicino senza parlarle per un po', dice qualcosa di sua
   iniziativa invece di stare in silenzio

In ogni risposta, parla con Piper e fa un piccolo gesto con la testa in
base all'emozione della risposta.

Richiede che tu abbia gia':
- addestrato il riconoscimento facciale (foxy.train_face) - opzionale
- addestrato il riconoscimento vocale (foxy.train_voice) - opzionale
- ANTHROPIC_API_KEY impostata nell'ambiente
- Vosk e Piper installati e configurati (vedi README)
"""
import time

import cv2

from foxy import config
from foxy.actuators import HeadServo
from foxy.chat import ChatEngine
from foxy.face_id import FaceIdentifier
from foxy.sensors import PresenceSensor
from foxy.speech_to_text import SpeechToText
from foxy.text_to_speech import TextToSpeech
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


def _speak(chat, tts, head, prompt, speaker_name):
    spoken_text, emotion = chat.reply(prompt, speaker_name)
    print(f"Foxy: {spoken_text} [{emotion}]")
    tts.say(spoken_text, emotion)
    head.express_emotion(emotion)


def run():
    presence = PresenceSensor()
    head = HeadServo()
    chat = ChatEngine()
    stt = SpeechToText()
    tts = TextToSpeech()
    face_identifier = FaceIdentifier()
    voice_identifier = VoiceIdentifier()

    print("Foxy e' pronto a chiacchierare. In ascolto sul sensore di presenza...")

    was_near = False
    greeted_name = None
    last_interaction = 0.0

    try:
        while True:
            near = presence.is_someone_near()

            if not near:
                if was_near:
                    # la persona se n'e' andata: si riparte da zero al prossimo arrivo
                    chat.reset()
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
                    print(f"Foxy riconosce {speaker_name}: lo saluta lei per prima.")
                    greeting_prompt = (
                        f"[Si e' appena avvicinato/a {speaker_name}. Salutalo/a tu per prima, "
                        "spontaneamente, con una battuta o una domanda breve - non aspettare "
                        "che parli per primo/a.]"
                    )
                    _speak(chat, tts, head, greeting_prompt, speaker_name)
                    last_interaction = time.time()

            text, audio = stt.listen_and_transcribe(
                max_wait_for_speech_s=config.CHAT_LISTEN_TIMEOUT_S
            )

            if text:
                speaker_name = _identify_speaker(face_identifier, voice_identifier, audio)
                print(f"[{speaker_name or 'sconosciuto'}] {text}")
                _speak(chat, tts, head, text, speaker_name)
                last_interaction = time.time()
                continue

            if (time.time() - last_interaction) > config.CHAT_IDLE_COMMENT_AFTER_S:
                print("Silenzio prolungato: Foxy dice qualcosa di sua iniziativa.")
                idle_prompt = (
                    "[E' da un po' che la persona e' li' vicino ma nessuno ti parla. Di' "
                    "qualcosa di tua iniziativa, breve e spontanea: un'osservazione, una "
                    "domanda, una battuta sui videogiochi, quello che ti viene.]"
                )
                _speak(chat, tts, head, idle_prompt, None)
                last_interaction = time.time()
    except KeyboardInterrupt:
        print("Arresto di Foxy...")
    finally:
        presence.close()
        head.close()


if __name__ == "__main__":
    run()
