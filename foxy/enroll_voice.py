"""Registra campioni della voce di una persona per l'addestramento.

Uso:
    python -m foxy.enroll_voice "Nome Persona"

Registra alcuni campioni audio dal microfono e li salva in
voice_dataset/<Nome Persona>/. Dopo aver registrato tutte le persone,
lancia:
    python -m foxy.train_voice
"""
import sys
from pathlib import Path

import sounddevice as sd
import soundfile as sf

from foxy import config

NUM_SAMPLES = 10
SAMPLE_DURATION_S = 3


def enroll(person_name: str):
    dataset_dir = Path(config.VOICE_DATASET_DIR) / person_name
    dataset_dir.mkdir(parents=True, exist_ok=True)

    print(f"Registrazione voce di '{person_name}'.")
    print("Parla normalmente (una frase qualsiasi) ad ogni campione.")

    for i in range(NUM_SAMPLES):
        input(f"Premi INVIO e poi parla per {SAMPLE_DURATION_S}s (campione {i + 1}/{NUM_SAMPLES})...")
        audio = sd.rec(
            int(SAMPLE_DURATION_S * config.VOICE_SAMPLE_RATE),
            samplerate=config.VOICE_SAMPLE_RATE,
            channels=1,
            dtype="float32",
        )
        sd.wait()
        sf.write(str(dataset_dir / f"{i:03d}.wav"), audio, config.VOICE_SAMPLE_RATE)
        print("Campione salvato.")

    print(f"Registrazione completata: {NUM_SAMPLES} campioni salvati in {dataset_dir}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print('Uso: python -m foxy.enroll_voice "Nome Persona"')
        sys.exit(1)
    enroll(sys.argv[1])
