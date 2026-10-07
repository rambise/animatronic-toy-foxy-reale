import subprocess

import pygame

from foxy import config

# "length_scale" di Piper: valori piu' bassi = parlato piu' veloce.
# Approssimazione semplice del tono emotivo nella voce (niente vera
# modulazione di pitch, Piper non la espone facilmente da riga di comando).
_EMOTION_LENGTH_SCALE = {
    "felice": 0.9,
    "sorpreso": 0.85,
    "curioso": 0.95,
    "affettuoso": 1.05,
    "triste": 1.15,
    "neutro": 1.0,
}


class TextToSpeech:
    """Da' voce a Cassidy con Piper (sintesi vocale offline, leggera su Pi)."""

    def __init__(self):
        if not pygame.mixer.get_init():
            pygame.mixer.init()

    def say(self, text: str, emotion: str = "neutro"):
        """Sintetizza e riproduce il testo. Blocca finche' non finisce di parlare."""
        if not text:
            return

        length_scale = _EMOTION_LENGTH_SCALE.get(emotion, 1.0)

        subprocess.run(
            [
                config.PIPER_BINARY,
                "--model", config.PIPER_MODEL_PATH,
                "--output_file", config.TTS_SCRATCH_WAV_PATH,
                "--length_scale", str(length_scale),
            ],
            input=text.encode("utf-8"),
            check=True,
        )

        pygame.mixer.music.load(config.TTS_SCRATCH_WAV_PATH)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.wait(50)
