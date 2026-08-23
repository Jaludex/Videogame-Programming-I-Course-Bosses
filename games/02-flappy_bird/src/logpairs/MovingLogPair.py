"""
ISPPV1 2023
Study Case: Flappy Bird

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the definition of the class LogPair: a top log
(rendered flipped upside down) and a bottom log, LOGS_GAP pixels
apart, that scroll left together and score once the bird passes them.
"""

import pygame

import settings
from src.logpairs import LogPair

class MovingLogPair(LogPair):
    def __init__(self, x: float, y: float) -> None:
        super().__init__(x, y)
        self.press_direction = 1
        self.current_gap = settings.LOGS_GAP 

    def get_top_rect(self) -> pygame.Rect:
        return pygame.Rect(round(self.x), round(self.y), settings.LOG_WIDTH, settings.LOG_HEIGHT)

    def get_bottom_rect(self) -> pygame.Rect:
        return pygame.Rect(
            round(self.x),
            round(self.y + self.current_gap + settings.LOG_HEIGHT),
            settings.LOG_WIDTH,
            settings.LOG_HEIGHT,
        )

    def update(self, dt: float) -> None:
        super().update(dt)

        self.current_gap += self.press_direction * (settings.CLOSING_LOGS_SPEED * dt)

        if self.current_gap > settings.LOGS_GAP:
            self.current_gap = settings.LOGS_GAP
            self.press_direction = -1
        elif self.current_gap < 0:
            self.current_gap = 0
            self.press_direction = 1

            settings.SOUNDS["wood_press"].play()
        

