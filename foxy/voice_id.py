from pathlib import Path

import joblib
import numpy as np
from python_speech_features import mfcc

from foxy import config


def extract_features(audio: np.ndarray, sample_rate: int) -> np.ndarray:
    """Estrae un vettore di features MFCC medie da un segnale audio mono."""
    coeffs = mfcc(audio, samplerate=sample_rate, numcep=13)
    return coeffs.mean(axis=0)


class VoiceIdentifier:
    """Riconosce chi sta parlando tramite features MFCC + classificatore SVM.

    Serve prima registrare dei campioni con `foxy.enroll_voice` e
    addestrare il modello con `foxy.train_voice`.
    """

    def __init__(self):
        model_path = Path(config.VOICE_MODEL_PATH)
        self._classifier = joblib.load(model_path) if model_path.exists() else None

    @property
    def is_trained(self) -> bool:
        return self._classifier is not None

    def identify(self, audio: np.ndarray, sample_rate: int = config.VOICE_SAMPLE_RATE):
        """Ritorna (nome, confidenza) oppure (None, None) se il modello non e' addestrato.

        Un nome "sconosciuto" indica una voce non riconosciuta con
        sufficiente sicurezza.
        """
        if not self.is_trained:
            return None, None

        features = extract_features(audio, sample_rate).reshape(1, -1)
        probabilities = self._classifier.predict_proba(features)[0]
        best_idx = int(np.argmax(probabilities))
        confidence = float(probabilities[best_idx])
        name = self._classifier.classes_[best_idx]

        if confidence < config.VOICE_CONFIDENCE_THRESHOLD:
            return "sconosciuto", confidence

        return name, confidence
