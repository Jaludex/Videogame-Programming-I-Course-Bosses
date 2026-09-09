"""
ISPPV1 2023
Study Case: Ultimate Fantasy (RPG)

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the class FadeInState: fades the screen to a solid
color over `time` seconds, then pops itself and calls on_complete (meant
to swap out whatever is now visible while the screen is fully covered).
"""

from typing import Any, Callable, Optional, Tuple

import pygame

from gale.state import BaseState
from gale.timer import Timer

import settings


class FadeInState(BaseState):
    def enter(
        self,
        color: Tuple[int, int, int] = (255, 255, 255),
        time: float = 1,
        on_complete: Optional[Callable[[], None]] = None,
    ) -> None:
        self.color = color
        self.opacity = 0.0
        self.on_complete = on_complete or (lambda: None)
        Timer.tween(time, [(self, {"opacity": 255})], on_finish=self._finish)

    def _finish(self) -> None:
        self.state_machine.pop()
        self.on_complete()

    def render(self, surface: pygame.Surface) -> None:
        overlay = pygame.Surface((settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT))
        overlay.fill(self.color)
        overlay.set_alpha(int(self.opacity))
        surface.blit(overlay, (0, 0))
