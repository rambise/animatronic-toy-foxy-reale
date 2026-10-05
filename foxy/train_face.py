"""Addestra il riconoscitore facciale sulle foto in face_dataset/.

Uso:
    python -m foxy.train_face

Richiede che tu abbia gia' registrato almeno una persona con
`foxy.enroll_face`.
"""
import json
from pathlib import Path

import cv2
import numpy as np

from foxy import config


def train():
    dataset_dir = Path(config.FACE_DATASET_DIR)
    if not dataset_dir.exists():
        print(f"Nessun dato in {dataset_dir}. Usa prima foxy.enroll_face.")
        return

    people = sorted(p.name for p in dataset_dir.iterdir() if p.is_dir())
    if not people:
        print(f"Nessun dato in {dataset_dir}. Usa prima foxy.enroll_face.")
        return

    images = []
    labels = []
    label_map = {}

    for label_id, person in enumerate(people):
        label_map[label_id] = person
        photo_paths = list((dataset_dir / person).glob("*.png"))
        for photo_path in photo_paths:
            img = cv2.imread(str(photo_path), cv2.IMREAD_GRAYSCALE)
            if img is None:
                continue
            images.append(img)
            labels.append(label_id)
        print(f"{person}: {len(photo_paths)} foto")

    if not images:
        print("Nessuna foto valida trovata.")
        return

    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.train(images, np.array(labels))

    model_path = Path(config.FACE_MODEL_PATH)
    model_path.parent.mkdir(parents=True, exist_ok=True)
    recognizer.write(str(model_path))

    with open(config.FACE_LABELS_PATH, "w", encoding="utf-8") as f:
        json.dump(label_map, f, ensure_ascii=False, indent=2)

    print(f"Modello addestrato su {len(people)} persone: {', '.join(people)}")
    print(f"Salvato in {model_path}")


if __name__ == "__main__":
    train()
