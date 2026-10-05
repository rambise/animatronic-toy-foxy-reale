import re

_EMOTION_TAG_RE = re.compile(r"\[EMOZIONE:\s*(\w+)\s*\]", re.IGNORECASE)
VALID_EMOTIONS = {"felice", "triste", "sorpreso", "curioso", "affettuoso", "neutro"}


def split_response(raw_text: str):
    """Separa il testo da dire ad alta voce dal tag [EMOZIONE:...] che
    l'IA aggiunge in fondo alle sue risposte (vedi foxy/personality.py)."""
    match = _EMOTION_TAG_RE.search(raw_text)
    emotion = "neutro"
    if match:
        candidate = match.group(1).lower()
        if candidate in VALID_EMOTIONS:
            emotion = candidate
        raw_text = raw_text[: match.start()]
    return raw_text.strip(), emotion
