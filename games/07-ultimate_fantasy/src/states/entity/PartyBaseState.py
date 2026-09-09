"""
ISPPV1 2023
Study Case: Ultimate Fantasy (RPG)

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the class PartyBaseState, the base for the Party's own
(as opposed to per-Character) idle/walk states.
"""

from typing import Any, TypeVar

import pygame

from gale.state import BaseState, StateMachine


class PartyBaseState(BaseState):
    def __init__(self, party: TypeVar("Party"), state_machine: StateMachine) -> None:
        super().__init__(state_machine)
        self.party = party

    def render(self, surface: pygame.Surface) -> None:
        for character in self.party.characters.values():
            if not character.dead:
                character.render(surface)
