from typing import TypeVar, Any

import pygame

import settings


class PowerUp:
    def __init__(self, x: int, y: int, texture_key: str) -> None:
        self.x = x
        self.y = y
        self.active = True
        self.texture_key = texture_key

    def get_collision_rect(self) -> pygame.Rect:
        return pygame.Rect(self.x, self.y, settings.TEXTURES[self.texture_key].get_width(), settings.TEXTURES[self.texture_key].get_height())

    def collides(self, obj: Any) -> bool:
        return self.get_collision_rect().colliderect(obj.get_rect())

    def update(self, dt: float) -> None:
        if self.x < 0:
            self.active = False

        self.x -= settings.MAIN_SCROLL_SPEED * dt

    def render(self, surface: pygame.Surface) -> None:
        surface.blit(
            settings.TEXTURES[self.texture_key],
            self.get_collision_rect(),
        )

    def take(self, gamemode: TypeVar("HardMode")) -> None:
        raise NotImplementedError
