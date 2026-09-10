from typing import Any

import pygame
import math
import settings

from src.Projectile import Projectile

_SPEED = 40


class DiagonalProjectile(Projectile):
    def __init__(self, obj: Any, sender: str = "player", objective_x = 0, objective_y = 0) -> None:
        super().__init__(obj, "diagonal", sender)
        start_x = obj.x + obj.width / 2
        start_y = obj.y + obj.height / 2

        dx = objective_x - start_x
        dy = objective_y - start_y

        distance = math.hypot(dx, dy)

        if distance != 0:
            self.vx = (dx / distance) * _SPEED
            self.vy = (dy / distance) * _SPEED
        else:
            self.vx = 0.0
            self.vy = 0.0
        

    def get_collision_rect(self) -> pygame.Rect:
        return self.obj.get_collision_rect().scale_by(0.7)

    def update(self, dt: float) -> None:
        if self.dead:
            return

        dx = self.vx * dt
        dy = self.vy * dt

        self.obj.y += dy

        bottom_edge = (
            settings.MAP_HEIGHT * settings.TILE_SIZE
            + settings.MAP_RENDER_OFFSET_Y
            - settings.TILE_SIZE
        )
        limit = settings.MAP_RENDER_OFFSET_Y + settings.TILE_SIZE - self.obj.height / 2

        if self.obj.y <= limit:
            self.obj.y = limit
            self.dead = True
        elif self.obj.y + self.obj.height >= bottom_edge:
            self.obj.y = bottom_edge - self.obj.height
            self.dead = True

        self.obj.x += dx

        limit_left = settings.MAP_RENDER_OFFSET_X + settings.TILE_SIZE
        limit_right = settings.VIRTUAL_WIDTH - settings.TILE_SIZE * 2
        if self.obj.x <= limit_left:
            self.obj.x = limit_left
            self.dead = True
        elif self.obj.x + self.obj.width >= limit_right:
            self.obj.x = limit_right - self.obj.width
            self.dead = True

    def render(
        self, surface: pygame.Surface, offset_x: float = 0, offset_y: float = 0
    ) -> None:
        self.obj.render(surface, offset_x, offset_y, -math.degrees(math.atan2(self.vy, self.vx)))

    def collides(self, target: Any) -> bool:
        return self.get_collision_rect().colliderect(target.get_collision_rect())
