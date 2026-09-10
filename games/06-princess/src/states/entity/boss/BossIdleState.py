"""
ISPPV1 2023
Study Case: The Legend of the Princess (ARPG)

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the class EntityIdleState.
"""

import random
from typing import TypeVar

import pygame

from src.states.entity.BaseEntityState import BaseEntityState
from gale.timer import Timer


class BossIdleState(BaseEntityState):
    def enter(self) -> None:
        self.entity.change_animation("idle-normal")

        self.entity.weak = False

    def update(self, dt):
        pass
        
    def process_ai(self, room: TypeVar("Room"), dt: float) -> None:
        self.entity.process_fire(dt)
        self.entity.process_head_movement(dt)

        if self.entity.fire_requested:
            self.entity.fire_requested = False

            self.entity.firing = True
            def stop_firing_head():
                self.entity.firing = False

            Timer.after(1, stop_firing_head)

            self.entity.fire(room)
    
    def render(self, surface: pygame.Surface) -> None:
        anim = self.entity.current_animation
        self.entity.render_sprite(surface, anim.texture_id, anim.get_current_frame())
