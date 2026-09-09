"""
ISPPV1 2023
Study Case: Ultimate Fantasy (RPG)

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the class DialogueState: a top-left textbox for NPC
dialogue (and the intro tutorial text), advanced/closed with space/enter.
"""

from typing import Any, Callable, Optional

import pygame

from gale.state import BaseState
from gale.ui.text_box import TextBox

import settings


class DialogueState(BaseState):
    def enter(self, text: str = "", on_close: Optional[Callable[[], None]] = None) -> None:
        self._on_close = on_close or (lambda: None)
        self.textbox = TextBox(
            6,
            6,
            settings.VIRTUAL_WIDTH - 12,
            64,
            text,
            font=settings.FONTS["small"],
            lines_per_page=3,
            on_close=self._on_textbox_close,
        )

    def _on_textbox_close(self) -> None:
        self.state_machine.pop()
        self._on_close()

    def on_input(self, input_id: str, input_data: Any) -> None:
        if input_id in ("space", "enter") and input_data.pressed:
            self.textbox.advance()

    def render(self, surface: pygame.Surface) -> None:
        self.textbox.render(surface)
