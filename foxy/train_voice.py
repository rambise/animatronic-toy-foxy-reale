"""Addestra il riconoscitore vocale sui campioni in voice_dataset/.

Uso:
    python -m foxy.train_voice

Richiede che tu abbia gia' registrato almeno due persone con
`foxy.enroll_voice` (serve piu' di una classe per addestrare il classificatore).
"""
from pathlib import Path

import joblib
import soundfile as sf
from sklearn.svm import SVC

from foxy import config
from foxy.voice_id import extract_features


def train():
    dataset_dir = Path(config.VOICE_DATASET_DIR)
    if not dataset_dir.exists():
        print(f"Nessun dato in {dataset_dir}. Usa prima foxy.enroll_voice.")
        return

    people = sorted(p.name for p in dataset_dir.iterdir() if p.is_dir())
    if len(people) < 2:
        print("Servono almeno 2 persone registrate per addestrare il classificatore.")
        return

    features = []
    labels = []

    for person in people:
        wav_paths = list((dataset_dir / person).glob("*.wav"))
        for wav_path in wav_paths:
            audio, sample_rate = sf.read(str(wav_path))
            features.append(extract_features(audio, sample_rate))
            labels.append(person)
        print(f"{person}: {len(wav_paths)} campioni")

    classifier = SVC(kernel="linear", probability=True)
    classifier.fit(features, labels)

    model_path = Path(config.VOICE_MODEL_PATH)
    model_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(classifier, model_path)

    print(f"Modello addestrato su {len(people)} persone: {', '.join(people)}")
    print(f"Salvato in {model_path}")


if __name__ == "__main__":
    train()
