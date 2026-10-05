import json
from pathlib import Path

import cv2

from foxy import config


class FaceIdentifier:
    """Riconosce i volti di famiglia con LBPH (OpenCV).

    Serve prima registrare le foto con `foxy.enroll_face` e addestrare
    il modello con `foxy.train_face`.
    """

    def __init__(self):
        self._cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        )
        self._recognizer = cv2.face.LBPHFaceRecognizer_create()

        model_path = Path(config.FACE_MODEL_PATH)
        labels_path = Path(config.FACE_LABELS_PATH)
        if model_path.exists() and labels_path.exists():
            self._recognizer.read(str(model_path))
            with open(labels_path, encoding="utf-8") as f:
                self._labels = {int(k): v for k, v in json.load(f).items()}
        else:
            self._labels = {}

    @property
    def is_trained(self) -> bool:
        return bool(self._labels)

    def _largest_face(self, gray_frame):
        faces = self._cascade.detectMultiScale(gray_frame, scaleFactor=1.2, minNeighbors=5)
        if len(faces) == 0:
            return None
        return max(faces, key=lambda f: f[2] * f[3])

    def identify(self, frame_bgr):
        """Ritorna (nome, confidenza) oppure (None, None) se nessun volto o modello non addestrato.

        Un nome "sconosciuto" indica un volto rilevato ma non riconosciuto
        con sufficiente sicurezza.
        """
        if not self.is_trained:
            return None, None

        gray = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2GRAY)
        face = self._largest_face(gray)
        if face is None:
            return None, None

        x, y, w, h = face
        roi = cv2.resize(gray[y:y + h, x:x + w], (200, 200))
        label_id, confidence = self._recognizer.predict(roi)

        if confidence > config.FACE_CONFIDENCE_THRESHOLD:
            return "sconosciuto", confidence

        return self._labels.get(label_id, "sconosciuto"), confidence
