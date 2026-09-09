"""
ISPPV1 2023
Study Case: Throw a Bird

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the class Bird: the parrot sitting in the slingshot,
ported from main.script + the parrot.go. It is a plain dynamic circle
body -- heavy, invulnerable (no destructible.script attached, matching
the original) -- driven entirely by PlayState (aiming/panning/flinging
live there, since in the original they are main.script's own concerns,
not the parrot's).
"""

import math

import pygame

from gale.physics.shapes import CircleShape
from gale.physics.world import World

import settings
from src.definitions.entity import BIRD, density_for_circle


class Bird:
    def __init__(self, world: World, x: float, y: float) -> None:
        self.radius: float = BIRD["radius"]
        self.mass: float = BIRD["mass"]

        density = density_for_circle(self.mass, self.radius)
        self.body = world.create_dynamic_body(
            x,
            y,
            CircleShape(
                radius=self.radius,
                density=density,
                friction=BIRD["friction"],
                restitution=BIRD["restitution"],
            ),
        )
        self.body.set_damping(BIRD["linear_damping"], BIRD["angular_damping"])
        self.body.user_data = self

        self.initial_position = pygame.Vector2(x, y)
        self.image = settings.TEXTURES[BIRD["sprite"]]

    @property
    def position(self) -> pygame.Vector2:
        return self.body.position

    def reset(self) -> None:
        """
        Put the bird back to rest in the slingshot, ready for another
        throw -- ported from main.script's idle_frames > 100 branch.
        """
        self.body.position = self.initial_position
        self.body.angle = 0.0
        self.body.velocity = (0, 0)
        self.body.angular_velocity = 0.0

    def render(self, surface: pygame.Surface, camera) -> None:
        diameter = max(1, round(self.radius * 2 * camera.zoom))
        scaled = pygame.transform.smoothscale(self.image, (diameter, diameter))
        rotated = pygame.transform.rotate(scaled, -math.degrees(self.body.angle))
        rect = rotated.get_rect(center=camera.world_to_screen(self.body.position))
        surface.blit(rotated, rect)
