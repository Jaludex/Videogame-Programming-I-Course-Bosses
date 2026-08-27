import random
from typing import TypeVar

from gale.factory import Factory

import settings
from src.Ball import Ball
from src.powerups.PowerUp import PowerUp

class SafetyNet(PowerUp):
    def __init__(self, x: int, y: int) -> None:
        super().__init__(x, y, 6)

    def take(self, play_state: TypeVar("PlayState")) -> None:
        play_state.safety_net_timer = settings.SAFETY_NET_TIME
        settings.SOUNDS["grow_up"].stop()
        settings.SOUNDS["grow_up"].play()
        self.active = False