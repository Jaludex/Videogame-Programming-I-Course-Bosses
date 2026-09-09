"""
ISPPV1 2023
Study Case: Ultimate Fantasy (RPG)

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the class ShowTextState: a centered, uppercased banner
that fades in (1s), holds/fades back out (2s), then pops itself and calls
on_complete. Purely timer-driven, no player input. Used to announce the
name of the region the party just entered.
"""

from typing import Callable, Optional, Tuple

import pygame

from gale.state import BaseState
from gale.timer import Timer

import settings


class ShowTextState(BaseState):
    def enter(
        self,
        color: Tuple[int, int, int] = (0, 0, 0),
        text: str = "",
        on_complete: Optional[Callable[[], None]] = None,
    ) -> None:
        self.color = color
        self.text = text.upper()
        self.opacity = 0.0
        self.on_complete = on_complete or (lambda: None)
        Timer.tween(1, [(self, {"opacity": 255})], on_finish=self._start_fade_out)

    def _start_fade_out(self) -> None:
        Timer.tween(2, [(self, {"opacity": 0})], on_finish=self._finish)

    def _finish(self) -> None:
        self.state_machine.pop()
        self.on_complete()

    def render(self, surface: pygame.Surface) -> None:
        font = settings.FONTS["large"]
        text_surface = font.render(self.text, True, self.color)
        text_surface.set_alpha(int(self.opacity))
        rect = text_surface.get_rect(
            center=(settings.VIRTUAL_WIDTH / 2, settings.VIRTUAL_HEIGHT / 2 - 30)
        )
        surface.blit(text_surface, rect)
