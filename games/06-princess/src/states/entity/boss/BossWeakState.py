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

from gale.timer import Timer

from src.states.entity.BaseEntityState import BaseEntityState


class BossWeakState(BaseEntityState):
    def enter(self) -> None:
        self.entity.change_animation("idle-weak")

        def return_to_idle():
            self.state_machine.change("idle")
        self.weak_timer = Timer.after(5, return_to_idle)

        # if self.entity.move_head_tween is not None:
        #     self.entity.move_head_tween.on_finish()
        #     self.entity.move_head_tween.remove()
        #     self.entity.move_head_tween = None
        self.entity.fire_requested = False
        self.entity.firing = False
        self.entity.weak = True
        self.entity.fire_wait_timer = 0

        self.move_head_down()
        


    def process_ai(self, room: TypeVar("Room"), dt: float) -> None:
        pass

    def move_head_down(self):
    # Centrar la cabeza horizontalmente: (Ancho del cuerpo / 2) - (Ancho de la cabeza / 2)
        self.new_head_x = self.entity.x + (self.entity.width / 2) - (self.entity.head_width / 2)
        
        # Colocar la cabeza en la base (pies): Posición Y + Alto del cuerpo - Alto de la cabeza
        self.new_head_y = self.entity.y + (1.5 * self.entity.height) - self.entity.head_height
        
        Timer.tween(
            1,
            [(self.entity, {"head_x": self.new_head_x, "head_y": self.new_head_y})],
        )   


    def render(self, surface: pygame.Surface) -> None:
        anim = self.entity.current_animation
        self.entity.render_sprite(surface, anim.texture_id, anim.get_current_frame())
