"""Registra le foto del volto di una persona per l'addestramento.

Uso:
    python -m foxy.enroll_face "Nome Persona"

Scatta automaticamente delle foto dalla webcam quando rileva un volto
e le salva in face_dataset/<Nome Persona>/. Dopo aver registrato tutte
le persone, lancia:
    python -m foxy.train_face
"""
import sys
import time
from pathlib import Path

import cv2

from foxy import config

NUM_PHOTOS = 30
DELAY_BETWEEN_PHOTOS_S = 0.3


def enroll(person_name: str):
    dataset_dir = Path(config.FACE_DATASET_DIR) / person_name
    dataset_dir.mkdir(parents=True, exist_ok=True)

    cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    )
    cam = cv2.VideoCapture(config.CAMERA_INDEX)
    if not cam.isOpened():
        print(f"Impossibile aprire la telecamera (indice {config.CAMERA_INDEX}).")
        return

    print(f"Registrazione volto di '{person_name}'.")
    print("Guarda la telecamera e muovi leggermente la testa (su/giu, destra/sinistra).")

    count = 0
    try:
        while count < NUM_PHOTOS:
            ok, frame = cam.read()
            if not ok:
                continue

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = cascade.detectMultiScale(gray, scaleFactor=1.2, minNeighbors=5)
            if len(faces) == 0:
                continue

            x, y, w, h = max(faces, key=lambda f: f[2] * f[3])
            roi = cv2.resize(gray[y:y + h, x:x + w], (200, 200))
            cv2.imwrite(str(dataset_dir / f"{count:03d}.png"), roi)
            count += 1
            print(f"Foto {count}/{NUM_PHOTOS}")
            time.sleep(DELAY_BETWEEN_PHOTOS_S)
    finally:
        cam.release()

    print(f"Registrazione completata: {count} foto salvate in {dataset_dir}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print('Uso: python -m foxy.enroll_face "Nome Persona"')
        sys.exit(1)
    enroll(sys.argv[1])
