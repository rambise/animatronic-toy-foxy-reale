"""Demo da terminale del riconoscimento vocale.

Uso:
    python -m foxy.demo_voice

Registra 3 secondi di audio dal microfono e stampa chi ha parlato,
secondo il modello addestrato.
"""
import sounddevice as sd

from foxy import config
from foxy.voice_id import VoiceIdentifier

SAMPLE_DURATION_S = 3


def run():
    identifier = VoiceIdentifier()
    if not identifier.is_trained:
        print("Modello non addestrato. Usa prima foxy.enroll_voice e foxy.train_voice.")
        return

    input(f"Premi INVIO e poi parla per {SAMPLE_DURATION_S} secondi...")
    audio = sd.rec(
        int(SAMPLE_DURATION_S * config.VOICE_SAMPLE_RATE),
        samplerate=config.VOICE_SAMPLE_RATE,
        channels=1,
        dtype="float32",
    )
    sd.wait()

    name, confidence = identifier.identify(audio.flatten(), config.VOICE_SAMPLE_RATE)
    print(f"Riconosciuto: {name} (confidenza={confidence:.2f})")


if __name__ == "__main__":
    run()
