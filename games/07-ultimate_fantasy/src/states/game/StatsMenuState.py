"""
ISPPV1 2023
Study Case: Ultimate Fantasy (RPG)

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the class StatsMenuState: shown right after a level-up,
displaying "Stat: previous + increase = current" for HP/Attack/Defense/
Magic. Any selection closes it.
"""

from typing import Any, Callable, Optional, Tuple

import pygame

from gale.state import BaseState

import settings
from src.gui.Menu import Menu


class StatsMenuState(BaseState):
    def enter(
        self,
        character: Any,
        stats: Tuple[int, int, int, int],
        on_close: Optional[Callable[[], None]] = None,
    ) -> None:
        self.character = character
        self._on_close = on_close or (lambda: None)

        hp_increase, attack_increase, defense_increase, magic_increase = stats

        rows = [
            ("HP", character.hp - hp_increase, hp_increase, character.hp),
            ("Attack", character.attack - attack_increase, attack_increase, character.attack),
            (
                "Defense",
                character.defense - defense_increase,
                defense_increase,
                character.defense,
            ),
            ("Magic", character.magic - magic_increase, magic_increase, character.magic),
        ]
        items = [
            (f"{name}: {previous} + {increase} = {current}", self.close)
            for name, previous, increase, current in rows
        ]

        self.menu = Menu(
            0,
            settings.VIRTUAL_HEIGHT - 64,
            settings.VIRTUAL_WIDTH,
            64,
            items=items,
            show_cursor=False,
            font=settings.FONTS["small"],
        )

    def close(self) -> None:
        self.state_machine.pop()
        self._on_close()

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
        self.menu.render(surface)
