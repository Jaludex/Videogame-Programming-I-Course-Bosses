"""
ISPPV1 2023
Study Case: The Legend of the Princess (ARPG)

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the class PlayerSwingSwordState.
"""

from typing import TypeVar

import pygame

from gale.state import StateMachine

import settings
from src.GameObject import GameObject
from src.Projectile import Projectile

from src.states.entity.BaseEntityState import BaseEntityState


class PlayerShotBowState(BaseEntityState):
    def __init__(
        self,
        player: TypeVar("Player"),
        state_machine: StateMachine,
        dungeon: TypeVar("Dungeon"),
    ) -> None:
        super().__init__(player, state_machine)
        self.dungeon = dungeon

        # Render offset for spaced character sprite.
        self.entity.offset_y = 5
        self.entity.offset_x = 8

        direction = self.entity.direction

        # if direction == "left":
        #     width, height = 8, 16
        #     x = self.entity.x - width
        #     y = self.entity.y + 2
        # elif direction == "right":
        #     width, height = 8, 16
        #     x = self.entity.x + self.entity.width
        #     y = self.entity.y + 2
        # elif direction == "up":
        #     width, height = 16, 8
        #     x = self.entity.x
        #     y = self.entity.y - height
        # else:
        #     width, height = 16, 8
        #     x = self.entity.x
        #     y = self.entity.y + self.entity.height

        self.entity.change_animation(f"bow-{direction}")
        self.entity.current_animation.times_played = 0

    def enter(self) -> None:
        #BOW SOUNDS
        self.entity.current_animation.reset()
        return

    def update(self, dt: float) -> None:
        self.entity.interact_requested = False
        self.entity.fire_requested = False
        self.entity.sword_requested = False

        if self.entity.current_animation.times_played > 0:
            self.entity.bow.fire(self.entity, self.dungeon.current_room)
            
            self.entity.current_animation.times_played = 0
            self.entity.change_state("idle")

    def render(self, surface: pygame.Surface) -> None:
        anim = self.entity.current_animation
        self.entity.render_sprite(surface, anim.texture_id, anim.get_current_frame())
