"""
ISPPV1 2023
Study Case: Flappy Bird

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the definition of the class World: the scrolling
background/ground, and the log pairs the bird must fly through.
"""

import random
from typing import List, Optional

import pygame

from gale.factory import Factory

import settings
from src.logpairs import LogPair
from src.logpairs import MovingLogPair
from src.modes import GameModeStrat


class World:
    def __init__(self) -> None:
        self.background_x: float = 0.0
        self.ground_x: float = 0.0
        self.logs: List[LogPair] = []

    def reset(self, generate_logs: bool) -> None:
        self.generate_logs = generate_logs

    def collides_with_border(self, rect: pygame.Rect) -> bool:
        if rect.bottom >= settings.VIRTUAL_HEIGHT or rect.top <= 0 or rect.left <= 0 or rect.right >= settings.VIRTUAL_WIDTH:
            return True

    def collides_with_log(self, rect: pygame.Rect):
        return any(log_pair.collides(rect) for log_pair in self.logs)

    def update_scored(self, rect: pygame.Rect) -> bool:
        return any(log_pair.update_scored(rect) for log_pair in self.logs)

    def append_log(self, log: LogPair) -> None:
        self.logs.append(log)

    def update(self, dt: float) -> None:
        self.background_x += -settings.BACK_SCROLL_SPEED * dt

        if self.background_x <= -settings.BACKGROUND_LOOPING_POINT:
            self.background_x = 0

        self.ground_x += -settings.MAIN_SCROLL_SPEED * dt

        if self.ground_x <= -settings.VIRTUAL_WIDTH:
            self.ground_x = 0

        for log_pair in self.logs:
            log_pair.update(dt)

        self.logs = [log_pair for log_pair in self.logs if not log_pair.is_out_of_game()]

    def render(self, surface: pygame.Surface) -> None:
        surface.blit(settings.TEXTURES["background"], (round(self.background_x), 0))

        for log_pair in self.logs:
            log_pair.render(surface)

        surface.blit(
            settings.TEXTURES["ground"],
            (round(self.ground_x), settings.VIRTUAL_HEIGHT - settings.GROUND_HEIGHT),
        )
