"""Client per il cervello di Foxy ospitato su Lovable, condiviso col bot
Telegram "Toy Foxy".

Stessa personalita', stessi mood, stessa memoria (se configuri
BRAIN_CHAT_ID) della chat Telegram. Il server fa sia il ragionamento
(LLM) sia la sintesi vocale: la risposta arriva gia' con l'audio pronto
(opus), riprodotto con ffplay - non serve Piper per questa modalita'.

Adattato dallo script toy_foxy_robot.py fornito dall'utente, per
integrarlo nel resto del progetto (sensori, riconoscimento volto/voce,
gesti della testa).

CONFIGURAZIONE (sul Raspberry Pi):
    1. Installa ffmpeg: sudo apt update && sudo apt install -y ffmpeg
    2. pip install requests (gia' in requirements.txt)
    3. Crea un file robot_key.txt nella radice del progetto con dentro
       la chiave segreta del robot (una sola riga, senza spazi).
"""
import base64
import os
import subprocess
import tempfile

import requests

from foxy import config

# Il cervello Lovable usa le sue parole per i mood: qui le traduciamo
# nelle emozioni che foxy/actuators.py sa gestire. Se i gesti sembrano
# sbagliati, stampa il valore grezzo di "mood" (vedi reply()) e aggiorna
# questa mappa di conseguenza.
_MOOD_TO_EMOTION = {
    "happy": "felice", "felice": "felice", "gioioso": "felice", "playful": "felice",
    "sad": "triste", "triste": "triste",
    "surprised": "sorpreso", "sorpreso": "sorpreso",
    "curious": "curioso", "curioso": "curioso",
    "affectionate": "affettuoso", "affettuoso": "affettuoso", "loving": "affettuoso",
    "calm": "neutro", "neutral": "neutro", "neutro": "neutro",
}


def _load_key() -> str:
    if not os.path.exists(config.BRAIN_KEY_FILE):
        raise RuntimeError(
            f"Manca il file '{config.BRAIN_KEY_FILE}' con la chiave segreta del "
            "robot nella radice del progetto. Vedi il README."
        )
    # utf-8-sig invece di utf-8: ignora il BOM che Windows (es. PowerShell
    # "Out-File -Encoding utf8", o Notepad) spesso aggiunge all'inizio del
    # file - altrimenti finisce dentro la chiave e rompe l'header HTTP.
    return open(config.BRAIN_KEY_FILE, encoding="utf-8-sig").read().strip()


def play_audio(opus_b64: str | None):
    """Salva l'audio opus ricevuto dal cervello e lo riproduce con ffplay."""
    if not opus_b64:
        return
    raw = base64.b64decode(opus_b64)
    with tempfile.NamedTemporaryFile(suffix=".opus", delete=False) as f:
        f.write(raw)
        path = f.name
    try:
        subprocess.run(
            ["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet", path],
            check=False,
        )
    except FileNotFoundError:
        print("ffplay non trovato: installa ffmpeg (sudo apt install ffmpeg)")
    finally:
        try:
            os.unlink(path)
        except OSError:
            pass


class BrainClient:
    """Parla con Foxy tramite il cervello Lovable/Telegram invece dell'API
    Claude diretta (foxy/chat.py)."""

    def __init__(self):
        self._key = _load_key()

    def reply(self, user_message: str, speaker_name: str | None = None):
        """Manda un messaggio al cervello.

        Ritorna (testo_da_dire, emozione, audio_opus_base64). Non
        riproduce l'audio da solo: usa play_audio() separatamente, cosi'
        chi chiama puo' stampare/loggare prima di far parlare Foxy.
        """
        prefixed_message = user_message
        if speaker_name and speaker_name != "sconosciuto":
            prefixed_message = f"[Sta parlando {speaker_name}] {user_message}"

        payload = {"text": prefixed_message}
        if config.BRAIN_CHAT_ID is not None:
            payload["chat_id"] = config.BRAIN_CHAT_ID

        try:
            res = requests.post(
                config.BRAIN_URL,
                json=payload,
                headers={"X-Robot-Key": self._key},
                timeout=config.BRAIN_REQUEST_TIMEOUT_S,
            )
        except requests.RequestException as e:
            print(f"Errore di connessione al cervello: {e}")
            return "", "neutro", None

        if res.status_code == 401:
            print("Chiave sbagliata: controlla robot_key.txt")
            return "", "neutro", None
        if not res.ok:
            print(f"Errore {res.status_code} dal cervello: {res.text[:200]}")
            return "", "neutro", None

        data = res.json()
        raw_mood = str(data.get("mood", "neutro"))
        emotion = _MOOD_TO_EMOTION.get(raw_mood.lower(), "neutro")
        text = data.get("text", "")

        return text, emotion, data.get("audio_base64")
