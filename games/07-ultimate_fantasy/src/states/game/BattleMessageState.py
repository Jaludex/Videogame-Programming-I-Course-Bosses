"""
ISPPV1 2023
Study Case: Ultimate Fantasy (RPG)

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the class BattleMessageState: the bottom-bar textbox
used for every battle announcement ("Turn for X!", damage results,
victory, ...). Enemies keep animating underneath while it's shown.

When can_input is False (used for the EXP-gain message), the textbox
does not auto-advance/close on player input -- the caller is expected to
pop this state itself once it is done (e.g. after a Timer-driven bar
tween finishes), matching the original's canInput=false messages that are
driven purely by timers rather than by the player.
"""

from typing import Any, Callable, Optional

import pygame

from gale.state import BaseState
from gale.ui.text_box import TextBox

import settings


class BattleMessageState(BaseState):
    def enter(
        self,
        battle_state: Any,
        message: str = "",
        on_close: Optional[Callable[[], None]] = None,
        can_input: bool = True,
    ) -> None:
        self.battle_state = battle_state
        self.can_input = can_input
        self._on_close = on_close or (lambda: None)
        self.textbox = TextBox(
            0,
            settings.VIRTUAL_HEIGHT - 64,
            settings.VIRTUAL_WIDTH,
            64,
            message,
            font=settings.FONTS["medium"],
            lines_per_page=3,
            on_close=self._on_textbox_close,
        )

    def _on_textbox_close(self) -> None:
        self.state_machine.pop()
        self._on_close()

    def update(self, dt: float) -> None:
        for enemy in self.battle_state.enemies:
            if not enemy.dead:
                enemy.update(dt)

    def on_input(self, input_id: str, input_data: Any) -> None:
        if not self.can_input:
            return

        if input_id in ("space", "enter") and input_data.pressed:
            self.textbox.advance()

    def render(self, surface: pygame.Surface) -> None:
        self.textbox.render(surface)
