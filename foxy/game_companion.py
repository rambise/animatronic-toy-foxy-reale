"""Companion sperimentale per videogiochi: Cassidy guarda lo schermo e commenta.

Uso:
    python -m foxy.game_companion

Punta una telecamera (anche una economica USB, separata da quella usata
per il riconoscimento volto) verso lo schermo su cui stai giocando. Ogni
tot secondi Cassidy scatta una foto, la manda all'IA per un commento breve,
e lo dice ad alta voce.

Limiti onesti: questo NON fa "giocare" Cassidy con te. E' una compagna che
guarda e commenta, come un'amica seduta vicino - non preme pulsanti, non
conosce lo stato interno del gioco (vita, inventario, ecc.), e puo'
descrivere male scene veloci o confuse. Automatizzare l'input (far
"giocare" fisicamente Cassidy) e' realistico solo per giochi molto semplici
e richiederebbe hardware aggiuntivo (es. un microcontrollore configurato
come gamepad USB) - non e' incluso in questo modulo.
"""
import base64
import time

import anthropic
import cv2

from foxy import config
from foxy.emotion import split_response
from foxy.text_to_speech import TextToSpeech

SYSTEM_PROMPT = """Sei Cassidy, una piccola robot volpe-pirata che guarda un'amica o un amico
giocare ai videogiochi, seduta vicino allo schermo. Commenta brevemente
quello che vedi nell'immagine: l'azione, la scena, qualcosa di
divertente o utile. Massimo 2 frasi, tono amichevole e giocoso, come
un'amica che guarda e fa il tifo - non un narratore robotico.

Se l'immagine non mostra chiaramente un videogioco (schermo nero, menu
generico, niente di interessante), rispondi con una sola parola:
SILENZIO

Altrimenti rispondi col commento, seguito su una riga a parte dal tag
dell'emozione tra: felice, sorpreso, curioso, neutro. Esempio:

Occhio a quel nemico dietro l'angolo!
[EMOZIONE:sorpreso]
"""


class GameCompanion:
    def __init__(self):
        self._client = anthropic.Anthropic()
        self._tts = TextToSpeech()

    def _capture_frame_b64(self):
        cam = cv2.VideoCapture(config.GAME_CAMERA_INDEX)
        try:
            ok, frame = cam.read()
        finally:
            cam.release()
        if not ok:
            return None
        ok, buffer = cv2.imencode(".png", frame)
        if not ok:
            return None
        return base64.standard_b64encode(buffer).decode("utf-8")

    def comment_once(self):
        image_b64 = self._capture_frame_b64()
        if image_b64 is None:
            print("Impossibile acquisire l'immagine dalla telecamera.")
            return

        response = self._client.messages.create(
            model=config.CLAUDE_MODEL,
            max_tokens=150,
            system=SYSTEM_PROMPT,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/png",
                                "data": image_b64,
                            },
                        },
                        {"type": "text", "text": "Ecco cosa vedi ora sullo schermo."},
                    ],
                }
            ],
            output_config={"effort": "low"},
        )

        raw_text = next((b.text for b in response.content if b.type == "text"), "")
        if raw_text.strip().upper().startswith("SILENZIO"):
            return

        spoken_text, emotion = split_response(raw_text)
        if not spoken_text:
            return

        print(f"Cassidy: {spoken_text} [{emotion}]")
        self._tts.say(spoken_text, emotion)


def run():
    companion = GameCompanion()
    print("Cassidy sta guardando lo schermo. CTRL+C per fermarlo.")
    try:
        while True:
            companion.comment_once()
            time.sleep(config.GAME_COMMENT_INTERVAL_S)
    except KeyboardInterrupt:
        print("Cassidy smette di guardare.")


if __name__ == "__main__":
    run()
