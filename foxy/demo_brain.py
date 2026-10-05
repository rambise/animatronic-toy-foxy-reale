"""Demo da terminale del cervello remoto (Lovable + Telegram).

Uso:
    python -m foxy.demo_brain

Scrivi un messaggio e ottieni la risposta vera del cervello di Foxy,
con tanto di audio. Utile per testare la connessione (chiave, chat_id)
prima di collegare microfono e sensori.
"""
from foxy.brain_client import BrainClient, play_audio


def run():
    brain = BrainClient()
    print("Foxy e' sveglia. Scrivi qualcosa (o 'esci' per chiudere).\n")
    while True:
        try:
            text = input("Tu: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nFoxy: a presto!")
            break
        if not text:
            continue
        if text.lower() in ("esci", "exit", "quit"):
            break

        spoken_text, emotion, audio_b64 = brain.reply(text)
        print(f"Foxy [{emotion}]: {spoken_text}")
        play_audio(audio_b64)


if __name__ == "__main__":
    run()
