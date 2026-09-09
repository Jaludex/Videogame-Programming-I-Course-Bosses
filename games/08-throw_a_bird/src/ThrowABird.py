"""
ISPPV1 2023
Study Case: Throw a Bird

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the class ThrowABird, a specialization of gale.Game.
Unlike lesson 07 (a StateStack, for menus/dialogue layered over the
world), this is a single continuous physics sandbox -- the original has
no win/lose condition at all, so a gale.state.StateMachine with just
"play" and a "victory" screen (added on request, once every alien is
destroyed -- see Level.all_enemies_defeated) is all it needs, the same
minimal shape examples/hillclimb and examples/leap use for their own
state machines.
"""

import pygame

from gale.game import Game
from gale.input_handler import InputData
from gale.state import StateMachine

from src.states.game.PlayState import PlayState
from src.states.game.VictoryState import VictoryState


class ThrowABird(Game):
    def init(self) -> None:
        self.state_machine = StateMachine(
            {"play": PlayState, "victory": VictoryState}
        )
        self.state_machine.change("play")

    def fixed_update(self) -> None:
        # Only PlayState drives a physics World; VictoryState has none,
        # so this is a no-op while it's current.
        state = self.state_machine.current
        fixed_update = getattr(state, "fixed_update", None)
        if fixed_update is not None:
            fixed_update()

    def update(self, dt: float) -> None:
        self.state_machine.update(dt)

    def render(self, surface: pygame.Surface) -> None:
        self.state_machine.render(surface)

    def on_input(self, input_id: str, input_data: InputData) -> None:
        if input_id == "quit" and input_data.pressed:
            self.quit()
        else:
            self.state_machine.on_input(input_id, input_data)
