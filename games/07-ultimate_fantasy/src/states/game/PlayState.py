"""
ISPPV1 2023
Study Case: Ultimate Fantasy (RPG)

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the class PlayState: hosts the World (overworld
regions + party) for as long as the player is out of battle.
"""

from typing import Any, Dict, Optional

import pygame

from gale.save import SaveManager
from gale.state import BaseState

import settings
from src.world.World import World


class PlayState(BaseState):
    def enter(
        self,
        party_genders: Dict[int, str],
        save_data: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.world = World(self.state_machine, party_genders)

        if save_data is not None:
            self.world.load_dict(save_data)

    def save_game(self) -> None:
        SaveManager().save(settings.SAVE_SLOT, self.world.to_dict())

    def update(self, dt: float) -> None:
        self.world.update(dt)

    def on_input(self, input_id: str, input_data: Any) -> None:
        if input_id == "pause" and input_data.pressed:
            from src.states.game.PauseMenuState import PauseMenuState

            self.state_machine.push(PauseMenuState(self.state_machine), play_state=self)
            return

        self.world.on_input(input_id, input_data)

    def render(self, surface: pygame.Surface) -> None:
        self.world.render(surface)
