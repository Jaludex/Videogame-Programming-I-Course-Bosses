"""
ISPPV1 2023
Study Case: The Legend of the Princess (ARPG)

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the class Player.
"""

from typing import Any, Dict

from gale.factory import Factory
from gale.timer import Timer
from src.Player import Player
from src.DiagonalProjectile import DiagonalProjectile
from src.GameObject import GameObject
from src.definitions.game_objects import GAME_OBJECT_DEFS

import settings
import random

from src.Entity import Entity


class DragonBoss(Entity):
    def __init__(
            self,
            x: float,
            y: float,
            width: float,
            height: float,
            walk_speed: float,
            health: int,
            animation_defs: Dict[str, Dict[str, Any]],
            states: Dict[str, Any],
            player: Player):
        super().__init__(x, y, width, height, walk_speed, health, animation_defs, states)

        self.player = player
        self.weak = False
        self.firing = False
        self.direction = "down"
        self.active = False
        self.fire_requested = False
        
        self.head_width = 9
        self.head_height = 16
        self.head_x = self.x + (self.width - self.head_width) / 2
        self.head_y = self.y + (self.height - self.head_height) / 2

        self.move_head_tween = None

        self.fire_wait_duration = random.uniform(1.5, 3)
        self.fire_wait_timer = 0
        self.move_head_duration = random.uniform(0.8, 2)
        self.move_head_timer = 0

        self.ammo_factory = Factory(GameObject)

    def collides_with_head(self, target: Any) -> bool:
        hitbox_x = self.head_x - 4
        hitbox_y = self.head_y - 8

        return not (
            hitbox_x + self.head_width < target.x
            or hitbox_x > target.x + target.width
            or hitbox_y + self.head_height < target.y
            or hitbox_y > target.y + target.height
        )

    def process_fire(self, dt):
        if self.fire_wait_duration == 0:
            self.fire_wait_duration = random.uniform(1.5, 3)
        else:
            self.fire_wait_timer += dt

        if self.fire_wait_timer > self.fire_wait_duration:
            self.fire_wait_timer %= self.fire_wait_duration

            self.fire_wait_duration = random.uniform(0.8, 2)

            self.fire_requested = True 

    def process_head_movement(self, dt):
        if self.move_head_tween is None:
            self.move_head_timer += dt
            if self.move_head_timer > self.move_head_duration:
                self.new_head_x = random.randint(int(self.x), int(self.x + self.width - self.head_width))
                self.new_head_y = random.randint(int(self.y), int(self.y + self.height))   

                def reset_head_timer():
                    self.move_head_tween = None
                    self.move_head_timer %= self.move_head_duration
                    self.move_head_duration = random.uniform(1.5, 4)    

                self.move_head_tween = Timer.tween(
                    1,
                    [(self, {"head_x": self.new_head_x, "head_y": self.new_head_y})],
                    on_finish=reset_head_timer
                )   

    def make_weak(self):
        if not self.weak:
            self.state_machine.change("weak")

    def damage(self, dmg) -> None:
        super().damage(dmg)
        self.go_invulnerable(0.5)

    def fire(self, room):
        player = room.player

        head_center_x = self.head_x
        head_center_y = self.head_y

        fireball_obj = self.ammo_factory.create(
            head_center_x, 
            head_center_y, 
            {"definition": GAME_OBJECT_DEFS["fireball"]}
        )
        proj_x = player.x + player.width / 2
        proj_y = player.y + player.height / 2

        room.projectiles.append(DiagonalProjectile(fireball_obj, "boss", proj_x, proj_y))
        settings.SOUNDS["dragon_fire"].play()

    def render_sprite(self, surface, texture_id, frame_index):
        super().render_sprite(surface, texture_id, frame_index)

        if self.active:
            texture = settings.TEXTURES[texture_id]

            body_center_x = self.x + self.width / 2
            body_center_y = self.y + self.height / 2

            neck_frame_index = 5 if not self.weak else 10
            
            neck_frame = settings.frame(texture_id, neck_frame_index)

            for i in range(1, settings.NECK_PIECES_FOR_DRAGON_BOSS + 1):
                t = i / (settings.NECK_PIECES_FOR_DRAGON_BOSS + 1)
                
                neck_x = body_center_x + (self.head_x - body_center_x) * t
                neck_y = body_center_y + (self.head_y - body_center_y) * t

                surface.blit(texture, (neck_x - 4, neck_y - 6), neck_frame)

            head_frame_index = 3 if not self.weak else 8
            if self.firing:
                head_frame_index += 1

            head_frame = settings.frame(texture_id, head_frame_index)

            surface.blit(texture, (self.head_x - 4, self.head_y - 8), head_frame)