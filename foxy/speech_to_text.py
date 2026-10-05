import json
import queue
import time

import numpy as np
import sounddevice as sd
from vosk import KaldiRecognizer, Model

from foxy import config

_CHUNK_DURATION_S = 0.1
_CHUNK_SAMPLES = int(config.VOICE_SAMPLE_RATE * _CHUNK_DURATION_S)


def _rms(chunk: np.ndarray) -> float:
    return float(np.sqrt(np.mean(chunk.astype(np.float64) ** 2)))


class SpeechToText:
    """Trascrizione vocale offline con Vosk.

    Rileva da solo inizio e fine del parlato con una soglia di energia
    (VAD semplice): non serve premere un pulsante, basta parlare.
    """

    def __init__(self):
        self._model = Model(config.VOSK_MODEL_PATH)

    def listen_and_transcribe(self, max_wait_for_speech_s: float | None = None):
        """Blocca finche' non sente una frase, poi la trascrive.

        Attende in silenzio finche' il volume non supera la soglia
        (inizio parlato), registra finche' non c'e' abbastanza silenzio
        consecutivo (fine parlato), con un taglio di sicurezza massimo.

        Se max_wait_for_speech_s e' impostato e nessuno inizia a parlare
        entro quel tempo, ritorna ("", array vuoto) invece di bloccare
        per sempre - utile per alternare ascolto e commenti spontanei.

        Ritorna (testo_trascritto, audio_float32) - l'audio grezzo serve
        a VoiceIdentifier per riconoscere chi ha parlato.
        """
        recognizer = KaldiRecognizer(self._model, config.VOICE_SAMPLE_RATE)
        audio_queue: "queue.Queue" = queue.Queue()

        def callback(indata, frames, time_info, status):
            audio_queue.put(indata.copy())

        recorded_chunks = []

        with sd.InputStream(
            samplerate=config.VOICE_SAMPLE_RATE,
            channels=1,
            dtype="int16",
            blocksize=_CHUNK_SAMPLES,
            callback=callback,
        ):
            speech_started = False
            silence_start = None
            recording_start = None
            wait_start = time.time()

            while True:
                chunk = audio_queue.get()
                level = _rms(chunk)
                now = time.time()

                if not speech_started:
                    if level > config.VAD_SILENCE_RMS_THRESHOLD:
                        speech_started = True
                        recording_start = now
                        recognizer.AcceptWaveform(chunk.tobytes())
                        recorded_chunks.append(chunk)
                    elif (
                        max_wait_for_speech_s is not None
                        and (now - wait_start) > max_wait_for_speech_s
                    ):
                        return "", np.array([], dtype=np.float32)
                    continue

                recognizer.AcceptWaveform(chunk.tobytes())
                recorded_chunks.append(chunk)

                if level > config.VAD_SILENCE_RMS_THRESHOLD:
                    silence_start = None
                elif silence_start is None:
                    silence_start = now

                timed_out = (now - recording_start) > config.VAD_MAX_RECORDING_S
                silence_done = (
                    silence_start is not None
                    and (now - silence_start) > config.VAD_SILENCE_DURATION_S
                )

                if silence_done or timed_out:
                    break

        result = json.loads(recognizer.FinalResult())
        text = result.get("text", "").strip()

        if recorded_chunks:
            audio_int16 = np.concatenate(recorded_chunks, axis=0).flatten()
            audio_float32 = audio_int16.astype(np.float32) / 32768.0
        else:
            audio_float32 = np.array([], dtype=np.float32)

        return text, audio_float32
