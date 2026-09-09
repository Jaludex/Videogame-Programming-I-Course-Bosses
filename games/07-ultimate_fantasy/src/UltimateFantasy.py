"""
ISPPV1 2023
Study Case: Ultimate Fantasy (RPG)

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the class UltimateFantasy, a specialization of
gale.Game. Unlike every prior port in this series (00-06), which used a
single gale.state.StateMachine, this project's original Lua source uses a
StateStack (src/states/StateStack.lua): states are pushed on top of one
another (dialogue over the world, a fade over a menu, ...), rendering the
whole stack bottom-to-top every frame but only updating/routing input to
the top one. gale.state.StateStack matches that exact semantics, so it is
used directly here instead of StateMachine.
"""

import pygame

from gale.game import Game
from gale.input_handler import InputData
from gale.state import StateStack

from src.states.game.StartState import StartState


class UltimateFantasy(Game):
    def init(self) -> None:
        self.state_stack = StateStack()
        self.state_stack.push(StartState(self.state_stack))

    def update(self, dt: float) -> None:
        self.state_stack.update(dt)

    def render(self, surface: pygame.Surface) -> None:
        self.state_stack.render(surface)

    def on_input(self, input_id: str, input_data: InputData) -> None:
        if input_id == "quit" and input_data.pressed:
            self.quit()
        else:
            self.state_stack.on_input(input_id, input_data)
