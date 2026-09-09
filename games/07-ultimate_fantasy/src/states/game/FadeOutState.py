"""
ISPPV1 2023
Study Case: Ultimate Fantasy (RPG)

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the class FadeOutState: the mirror of FadeInState --
fades a solid color color back to transparent, revealing whatever is
underneath, then pops itself and calls on_complete.
"""

from typing import Callable, Optional, Tuple

import pygame

from gale.state import BaseState
from gale.timer import Timer

import settings


class FadeOutState(BaseState):
    def enter(
        self,
        color: Tuple[int, int, int] = (255, 255, 255),
        time: float = 1,
        on_complete: Optional[Callable[[], None]] = None,
    ) -> None:
        self.color = color
        self.opacity = 255.0
        self.on_complete = on_complete or (lambda: None)
        Timer.tween(time, [(self, {"opacity": 0})], on_finish=self._finish)

    def _finish(self) -> None:
        self.state_machine.pop()
        self.on_complete()

    def render(self, surface: pygame.Surface) -> None:
        overlay = pygame.Surface((settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT))
        overlay.fill(self.color)
        overlay.set_alpha(int(self.opacity))
        surface.blit(overlay, (0, 0))
