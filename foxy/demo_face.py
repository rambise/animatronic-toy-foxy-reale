"""Demo da terminale (headless) del riconoscimento facciale.

Uso:
    python -m foxy.demo_face

Stampa a schermo il nome riconosciuto ogni volta che vede un volto.
Utile per testare la telecamera e il modello via SSH, senza monitor
collegato al Raspberry Pi.
"""
import time

import cv2

from foxy import config
from foxy.face_id import FaceIdentifier


def run():
    identifier = FaceIdentifier()
    if not identifier.is_trained:
        print("Modello non addestrato. Usa prima foxy.enroll_face e foxy.train_face.")
        return

    cam = cv2.VideoCapture(config.CAMERA_INDEX)
    if not cam.isOpened():
        print(f"Impossibile aprire la telecamera (indice {config.CAMERA_INDEX}).")
        return

    print("In ascolto sulla telecamera. CTRL+C per interrompere.")
    try:
        while True:
            ok, frame = cam.read()
            if not ok:
                continue

            name, confidence = identifier.identify(frame)
            if name is not None:
                print(f"Riconosciuto: {name} (confidenza={confidence:.1f})")

            time.sleep(0.5)
    except KeyboardInterrupt:
        print("Interrotto.")
    finally:
        cam.release()


if __name__ == "__main__":
    run()
