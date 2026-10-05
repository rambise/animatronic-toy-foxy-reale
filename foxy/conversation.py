"""Loop di conversazione completo di Foxy.

Uso:
    python -m foxy.conversation

Quando qualcuno si avvicina (sensore di presenza), Foxy ascolta,
riconosce chi sta parlando (volto + voce), risponde con l'IA
conversazionale, parla con Piper e fa un piccolo gesto con la testa in
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


def run():
    presence = PresenceSensor()
    head = HeadServo()
    chat = ChatEngine()
    stt = SpeechToText()
    tts = TextToSpeech()
    face_identifier = FaceIdentifier()
    voice_identifier = VoiceIdentifier()

    print("Foxy e' pronto a chiacchierare. In ascolto sul sensore di presenza...")
    try:
        while True:
            if not presence.is_someone_near():
                time.sleep(0.2)
                continue

            print("Qualcuno si e' avvicinato, ascolto...")
            text, audio = stt.listen_and_transcribe()
            if not text:
                continue

            speaker_name = None
            if face_identifier.is_trained:
                speaker_name = _snapshot_face_name(face_identifier)
            if (not speaker_name or speaker_name == "sconosciuto") and voice_identifier.is_trained:
                voice_name, _ = voice_identifier.identify(audio, config.VOICE_SAMPLE_RATE)
                speaker_name = voice_name or speaker_name

            print(f"[{speaker_name or 'sconosciuto'}] {text}")

            spoken_text, emotion = chat.reply(text, speaker_name)
            print(f"Foxy: {spoken_text} [{emotion}]")

            tts.say(spoken_text, emotion)
            head.express_emotion(emotion)
    except KeyboardInterrupt:
        print("Arresto di Foxy...")
    finally:
        presence.close()
        head.close()


if __name__ == "__main__":
    run()
