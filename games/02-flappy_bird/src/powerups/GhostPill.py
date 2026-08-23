from typing import TypeVar, Any

import pygame
import settings

from src.powerups import PowerUp

class GhostPill(PowerUp):
    def __init__(self, x: float, y: float, **kwargs) -> None:
        super().__init__(x=x, y=y, texture_key="ghostpill")
    
    def take(self, gamemode: TypeVar("HardMode")) -> None:
        gamemode.invincible_timer = settings.POWERUP_DURATION
        pygame.mixer.music.stop()
        pygame.mixer.music.load(settings.MUSICS["invincible"])
        pygame.mixer.music.play()
        self.active = False