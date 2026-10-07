import random
from pathlib import Path

import pygame

from foxy import config


class SoundPlayer:
    """Riproduce un suono a caso dalla cartella dei suoni di Cassidy."""

    def __init__(self):
        pygame.mixer.init()
        sounds_dir = Path(config.SOUNDS_DIR)
        self._sound_files = sorted(
            p for p in sounds_dir.glob("*") if p.suffix.lower() in (".wav", ".ogg", ".mp3")
        )

    def play_random(self):
        if not self._sound_files:
            return
        sound_file = random.choice(self._sound_files)
        pygame.mixer.music.load(str(sound_file))
        pygame.mixer.music.play()

    def close(self):
        pygame.mixer.quit()
