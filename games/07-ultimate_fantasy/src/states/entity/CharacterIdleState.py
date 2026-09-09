"""
ISPPV1 2023
Study Case: Ultimate Fantasy (RPG)

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the class CharacterIdleState.
"""

from src.states.entity.EntityBaseState import EntityBaseState


class CharacterIdleState(EntityBaseState):
    def enter(self) -> None:
        self.entity.change_animation(f"idle-{self.entity.direction}")
