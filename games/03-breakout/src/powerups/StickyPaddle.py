import random
from typing import TypeVar

from gale.factory import Factory

import settings
from src.Ball import Ball
from src.powerups.PowerUp import PowerUp

class StickyPaddle(PowerUp):
    def __init__(self, x: int, y: int) -> None:
        super().__init__(x, y, 5)

    def take(self, play_state: TypeVar("PlayState")) -> None:
        play_state.sticky_paddle_timer = settings.STICLY_PADDLE_TIME
        settings.SOUNDS["grab_sticky_paddle"].stop()
        settings.SOUNDS["grab_sticky_paddle"].play()
        self.active = False

