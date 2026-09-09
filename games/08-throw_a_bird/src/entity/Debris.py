"""
ISPPV1 2023
Study Case: Throw a Bird

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the class DebrisChip, ported from debris.script: a
short-lived, purely cosmetic wood-chip particle spawned when a wood
Destructible is destroyed. It never joins the physics World (the
original debris.go has no collisionobject either, just a sprite and a
scripted toss-and-spin) -- gale.timer.Tween drives its position/rotation
directly instead of a hand-rolled lerp, matching the brief's suggestion.
"""

import random

import pygame

from gale.timer import Timer

import settings


class DebrisChip:
    TOSS_DURATION = 0.5
    TOSS_DOWN_DISTANCE = 150  # world pixels

    def __init__(self, x: float, y: float) -> None:
        self.x: float = x
        self.y: float = y
        self.angle: float = 0.0
        self.scale: float = random.uniform(0.5, 0.8)
        self.alive: bool = True

        to_x = self.x + random.uniform(-10, 10)
        # debris.script subtracts 150 from y in Defold's Y-up world, which
        # is a move *down* (lower y = lower on screen there), not up --
        # the chip falls away as it spins. gale/pygame is Y-down, so the
        # equivalent "down" move is a *positive* y delta here. (A prior
        # version of this file had the sign backwards and tossed chips
        # upward instead.)
        to_y = self.y + self.TOSS_DOWN_DISTANCE

        Timer.tween(
            self.TOSS_DURATION,
            [(self, {"x": to_x, "y": to_y})],
            "in_cubic",
            on_finish=self._finish,
        )
        Timer.tween(
            self.TOSS_DURATION,
            [(self, {"angle": random.uniform(0.0, 360.0)})],
            "in_cubic",
        )

    def _finish(self) -> None:
        self.alive = False

    def render(self, surface: pygame.Surface, camera) -> None:
        image = settings.TEXTURES["debris-wood"]
        width, height = image.get_size()
        size = (
            max(1, round(width * self.scale * camera.zoom)),
            max(1, round(height * self.scale * camera.zoom)),
        )
        scaled = pygame.transform.smoothscale(image, size)
        rotated = pygame.transform.rotate(scaled, -self.angle)
        rect = rotated.get_rect(center=camera.world_to_screen((self.x, self.y)))
        surface.blit(rotated, rect)
