import pygame

import settings

class Rocket:
    def __init__(self, x: int, y: int) -> None:
        self.x = x
        self.y = y
        self.vy = 0
        self.width: int = 10
        self.height: int = 16
        self.active = True

    def collides(self, another) -> bool:
        return self.get_collision_rect().colliderect(another.get_collision_rect())

    def get_collision_rect(self) -> pygame.Rect:
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def get_explosion_rect(self) -> pygame.Rect:
        return pygame.Rect(self.x + (self.width // 2) - 32, self.y - 32, 64, 64)

    def explodes(self):
        self.active = False
        settings.SOUNDS["rocket_hit"].play()

    def update(self, dt: float) -> None:
        self.vy += settings.ROCKET_ACCELERATION * dt

        self.y += self.vy * dt

        if self.y <= -self.height:
            self.active = False

    def render(self, surface):
        surface.blit(
            settings.TEXTURES["spritesheet"], (self.x, self.y), settings.FRAMES["rocket"]
        )