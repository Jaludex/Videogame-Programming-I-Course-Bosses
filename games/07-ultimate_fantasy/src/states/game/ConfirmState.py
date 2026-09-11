"""
ISPPV1 2023
Study Case: Ultimate Fantasy (RPG)

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the class ConfirmState: a generic "Si"/"No" dialog
pushed on top of whatever's asking. Used by PauseMenuState to warn about
unsaved progress before loading a different slot or quitting -- both
"do you want to save the current game first?", proceeding with whichever
answer the player picks either way (see PauseMenuState._load_another /
_quit).
"""

from typing import Any, Callable

import pygame

from gale.state import BaseState

import settings
from src.gui.Menu import Menu
from src.text_utils import wrap_text


class ConfirmState(BaseState):
    def enter(
        self,
        message: str,
        on_yes: Callable[[], None],
        on_no: Callable[[], None],
    ) -> None:
        self.message = message
        self.on_yes = on_yes
        self.on_no = on_no

        self.menu = Menu(
            settings.VIRTUAL_WIDTH / 2 - 50,
            settings.VIRTUAL_HEIGHT / 2 + 10,
            100,
            48,
            items=[("Yes", self._yes), ("No", self._no)],
            font=settings.FONTS["small"],
        )

    def _yes(self) -> None:
        self.state_machine.pop()
        self.on_yes()

    def _no(self) -> None:
        self.state_machine.pop()
        self.on_no()

    def update(self, dt: float) -> None:
        self.menu.update(dt)

    def on_input(self, input_id: str, input_data: Any) -> None:
        if not input_data.pressed:
            return

        if input_id == "move_up":
            self.menu.navigate((0, -1))
        elif input_id == "move_down":
            self.menu.navigate((0, 1))
        elif input_id == "enter":
            self.menu.confirm()

    def render(self, surface: pygame.Surface) -> None:
        overlay = pygame.Surface((settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT))
        overlay.set_alpha(160)
        overlay.fill((0, 0, 0))
        surface.blit(overlay, (0, 0))

        font = settings.FONTS["small"]
        max_width = settings.VIRTUAL_WIDTH - 40
        y = settings.VIRTUAL_HEIGHT / 2 - 40

        for line in wrap_text(font, self.message, max_width):
            text = font.render(line, True, (255, 255, 255))
            rect = text.get_rect(center=(settings.VIRTUAL_WIDTH / 2, y))
            surface.blit(text, rect)
            y += text.get_height() + 2

        self.menu.render(surface)
