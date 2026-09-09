"""
ISPPV1 2023
Study Case: Ultimate Fantasy (RPG)

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the class SelectTargetState: cycles a cursor sprite
through the (alive-only) members of a target list with left/right, and
confirms the highlighted one with enter.
"""

from typing import Any, Callable, List

import pygame

from gale.state import BaseState

import settings


class SelectTargetState(BaseState):
    def enter(
        self,
        battle_state: Any,
        targets: List[Any],
        on_target_selected: Callable[[Any], None],
    ) -> None:
        self.battle_state = battle_state
        self.targets = list(targets)
        self.on_target_selected = on_target_selected

        self.current_selection = 0
        for i, target in enumerate(self.targets):
            if not target.dead:
                self.current_selection = i
                break

    def _next_alive(self) -> None:
        n = len(self.targets)

        for step in range(1, n + 1):
            i = (self.current_selection + step) % n

            if not self.targets[i].dead:
                self.current_selection = i
                return

    def _prev_alive(self) -> None:
        n = len(self.targets)

        for step in range(1, n + 1):
            i = (self.current_selection - step) % n

            if not self.targets[i].dead:
                self.current_selection = i
                return

    def update(self, dt: float) -> None:
        for enemy in self.battle_state.enemies:
            if not enemy.dead:
                enemy.update(dt)

    def on_input(self, input_id: str, input_data: Any) -> None:
        if not input_data.pressed:
            return

        if input_id == "move_left":
            self._prev_alive()
        elif input_id == "move_right":
            self._next_alive()
        elif input_id == "enter":
            target = self.targets[self.current_selection]
            self.state_machine.pop()
            self.on_target_selected(target)

    def render(self, surface: pygame.Surface) -> None:
        target = self.targets[self.current_selection]
        surface.blit(
            settings.TEXTURES["cursor-right"],
            (target.x - settings.TILE_SIZE, target.y),
        )
