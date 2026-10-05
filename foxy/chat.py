import os

import anthropic

from foxy import config
from foxy.emotion import split_response
from foxy.personality import SYSTEM_PROMPT


class ChatEngine:
    """Gestisce la conversazione di Foxy tramite l'API Claude.

    Richiede la variabile d'ambiente ANTHROPIC_API_KEY impostata sul
    Raspberry Pi (mai scritta nel codice).
    """

    def __init__(self):
        if not os.environ.get("ANTHROPIC_API_KEY"):
            raise RuntimeError(
                "Variabile d'ambiente ANTHROPIC_API_KEY non impostata. "
                "Vedi il README per come configurarla sul Raspberry Pi."
            )
        self._client = anthropic.Anthropic()
        self._history: list[dict] = []

    def reset(self):
        self._history = []

    def _remember(self, role: str, content: str):
        self._history.append({"role": role, "content": content})
        max_messages = config.CHAT_MAX_HISTORY_TURNS * 2
        if len(self._history) > max_messages:
            self._history = self._history[-max_messages:]

    def reply(self, user_message: str, speaker_name: str | None = None) -> tuple[str, str]:
        """Invia un messaggio a Foxy e ritorna (testo_da_dire, emozione).

        Se speaker_name e' noto (dal riconoscimento volto/voce), viene
        aggiunto al messaggio cosi' Foxy sa chi sta parlando.
        """
        prefixed_message = user_message
        if speaker_name and speaker_name != "sconosciuto":
            prefixed_message = f"[Sta parlando {speaker_name}] {user_message}"

        self._remember("user", prefixed_message)

        response = self._client.messages.create(
            model=config.CLAUDE_MODEL,
            max_tokens=config.CHAT_MAX_RESPONSE_TOKENS,
            system=[
                {"type": "text", "text": SYSTEM_PROMPT, "cache_control": {"type": "ephemeral"}}
            ],
            messages=self._history,
            output_config={"effort": "low"},
        )

        raw_text = next((b.text for b in response.content if b.type == "text"), "")
        spoken_text, emotion = split_response(raw_text)

        self._remember("assistant", raw_text)

        return spoken_text, emotion
