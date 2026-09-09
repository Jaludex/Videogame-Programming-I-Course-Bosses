"""
ISPPV1 2023
Study Case: Ultimate Fantasy (RPG)

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the class BattleMenuState: the Fight/Run menu shown at
the start of every round.
"""

from typing import Any

import pygame

from gale.state import BaseState
from gale.timer import Timer

import settings
from src.gui.Menu import Menu


class BattleMenuState(BaseState):
    def enter(self, battle_state: Any) -> None:
        self.battle_state = battle_state
        self.menu = Menu(
            settings.VIRTUAL_WIDTH - 64,
            settings.VIRTUAL_HEIGHT - 64,
            64,
            64,
            items=[("Fight", self._fight), ("Run", self._run)],
        )

    def _fight(self) -> None:
        from src.states.game.TakeTurnState import TakeTurnState

        self.state_machine.pop()
        self.state_machine.push(
            TakeTurnState(self.state_machine), battle_state=self.battle_state
        )

    def _run(self) -> None:
        from src.states.game.BattleMessageState import BattleMessageState

        settings.SOUNDS["run"].play()
        self.state_machine.pop()
        self.state_machine.push(
            BattleMessageState(self.state_machine),
            battle_state=self.battle_state,
            message="You fled successfully!",
            on_close=self._flee,
        )

    def _flee(self) -> None:
        from src.states.game.FadeInState import FadeInState
        from src.states.game.FadeOutState import FadeOutState

        def on_fade_in_complete() -> None:
            self.state_machine.pop()
            self.state_machine.push(
                FadeOutState(self.state_machine),
                color=(255, 255, 255),
                time=1,
                on_complete=lambda: None,
            )

        self.state_machine.push(
            FadeInState(self.state_machine),
            color=(255, 255, 255),
            time=1,
            on_complete=on_fade_in_complete,
        )

    def update(self, dt: float) -> None:
        for enemy in self.battle_state.enemies:
            if not enemy.dead:
                enemy.update(dt)

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
