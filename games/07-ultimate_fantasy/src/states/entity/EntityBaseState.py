"""
ISPPV1 2023
Study Case: Ultimate Fantasy (RPG)

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the class EntityBaseState, the base for NPC/Character/
Enemy per-entity states.
"""

from typing import Any, TypeVar

import pygame

from gale.state import BaseState, StateMachine


class EntityBaseState(BaseState):
    def __init__(self, entity: Any, state_machine: StateMachine) -> None:
        super().__init__(state_machine)
        self.entity = entity

    def process_ai(self, params: Any, dt: float) -> None:
        pass

    def render(self, surface: pygame.Surface) -> None:
        self.entity.render_sprite(surface)
