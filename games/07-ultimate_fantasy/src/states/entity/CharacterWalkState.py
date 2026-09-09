"""
ISPPV1 2023
Study Case: Ultimate Fantasy (RPG)

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the class CharacterWalkState.
"""

from src.states.entity.EntityBaseState import EntityBaseState


class CharacterWalkState(EntityBaseState):
    def enter(self) -> None:
        self.entity.change_animation(f"walk-{self.entity.direction}")
