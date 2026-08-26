"""
ISPPV1 2023
Study Case: Breakout

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the specialization of PowerUp to add two more ball to the game.
"""

import random
from typing import TypeVar

from gale.factory import Factory

import settings
from src.Ball import Ball
from src.powerups.PowerUp import PowerUp

class Bazooka(PowerUp):
    def __init__(self, x: int, y: int) -> None:
        super().__init__(x, y, 4)

    def take(self, play_state: TypeVar("PlayState")) -> None:
        play_state.bazooka_timer = settings.BAZOOKA_TIME
        settings.SOUNDS["grab_bazooka"].stop()
        settings.SOUNDS["grab_bazooka"].play()
        self.active = False
