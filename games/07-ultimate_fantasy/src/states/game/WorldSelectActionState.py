"""
ISPPV1 2023
Study Case: Ultimate Fantasy (RPG)

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the class SelectActionState: menu of the acting
entity's own actions.actions (whatever list its ENTITY_DEFS entry
defines) plus a trailing "Nothing" (skip turn) entry.
"""

from typing import Any, Callable, Dict, List

import pygame

from gale.state import BaseState
from gale.timer import Timer

import settings
from src.gui.Menu import Menu

class WorldSelectActionState(BaseState):
    def enter(
        self, play_state: Any, entity: Any, on_action_selected: Callable[[], None]
    ) -> None:
        self.play_state = play_state
        self.entity = entity
        self.on_action_selected = on_action_selected

        items = [
            (action["name"], self._make_selector(action)) for action in entity.actions if action["target_type"] == "character"
        ]
        items.append(("Exit", self._nothing))

        self.menu = Menu(
            0, settings.VIRTUAL_HEIGHT - 64, settings.VIRTUAL_WIDTH, 64, items=items
        )

    def _make_selector(self, action: Dict[str, Any]) -> Callable[[], None]:
        return lambda: self._select_action(action)

    def _select_action(self, action: Dict[str, Any]) -> None:
        if action["target_type"] == "enemy":
            return

        targets = list(self.play_state.world.party.characters.values())

        self.state_machine.pop()

        if action["require_target"]:
            from src.states.game.WorldSelectTargetState import WorldSelectTargetState

            self.state_machine.push(WorldSelectTargetState(self.state_machine), 
                play_state=self.play_state,
                targets=targets,
                on_target_selected=lambda target: self._resolve(action, target),
            )
        else:
            alive_targets = [target for target in targets if not target.dead]
            action["func"](self.entity, alive_targets, action.get("strength"))
            settings.SOUNDS[action["sound_effect"]].play()

    def _resolve(self, action: Dict[str, Any], target: Any) -> None:
        action["func"](self.entity, target, action.get("strength"))
        settings.SOUNDS[action["sound_effect"]].play()

    def _nothing(self) -> None:
        self.state_machine.pop()
        self.on_action_selected()

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
