"""
ISPPV1 2023
Study Case: Throw a Bird

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the class Destructible, ported from destructible.script:
a physics body (box or circle, per its archetype) that tracks an "energy"
(HP) value, drops through 3 damage-tier sprites as it's chipped away
(stone/wood only -- the aliens have a single sprite at every tier, just
like the original), and is destroyed once energy reaches 0.

on_collision (called from Level._apply_collision_damage, see
src/world/Level.py) is checked on every physics step for every pair of
bodies still touching, matching the Lua source's own on_collision, which
fires for as long as two bodies keep touching rather than once per
impact. An earlier version of this file applied damage only on
gale.physics.World's begin-contact event (the only "collision started"
signal it exposes), reasoning that the speed > 20 threshold already
guards against a resting stack bleeding energy every frame. That missed
a whole class of hits, though: BLOCKS in Level.py places neighbors only
a few pixels apart, so gravity settles every pair into permanent contact
within the first few steps after the level loads, at a speed under the
threshold -- and since that pair then never separates again, begin-contact
never fires for it a second time. A block later punched hard into an
already-touching neighbor (most often an alien boxed in on multiple
sides) dealt no damage through that contact no matter the impact speed.
Checking every still-touching pair every step catches that case too,
while the speed threshold keeps a merely resting contact from dealing
damage.
"""

import math

import pygame

from gale.physics.shapes import BoxShape, CircleShape
from gale.physics.world import World

import settings
from src.definitions.entity import ARCHETYPES, density_for_box, density_for_circle

# A collision against the ground reads the destructible's own speed
# instead of "the other body's" (there is no other body, the ground never
# moves) and treats the ground as if it had this fixed mass -- ported
# directly from destructible.script's on_collision ground special-case.
GROUND_EFFECTIVE_MASS = 1000

# Below this relative impact speed (pixels/second), a touch is treated as
# a rest contact, not an impact, and does no damage.
DAMAGE_SPEED_THRESHOLD = 20

# destructible.script used 0.01, but that was tuned against Defold's own
# velocity units (physics.scale = 0.02, gravity_y = -1000), which do not
# match gale's pixel/second velocities at pixels_per_meter=30 -- carried
# over as-is, a direct hit barely dented a block (~35-90 damage against
# 500-2000 energy pools, i.e. dozens of hits to destroy anything).
# Retuned by testing actual throws so a solid direct hit meaningfully
# damages/destroys blocks in a handful of hits.
DAMAGE_COEFFICIENT = 0.08


class Destructible:
    def __init__(
        self, world: World, x: float, y: float, archetype: str, angle: float = 0.0
    ) -> None:
        defn = ARCHETYPES[archetype]
        self.archetype: str = archetype

        if defn["shape"] == "box":
            self.width: float = defn["width"]
            self.height: float = defn["height"]
            density = density_for_box(defn["mass"], self.width, self.height)
            shape = BoxShape(
                self.width,
                self.height,
                density=density,
                friction=defn["friction"],
                restitution=defn["restitution"],
            )
        else:
            self.width = self.height = defn["radius"] * 2
            density = density_for_circle(defn["mass"], defn["radius"])
            shape = CircleShape(
                radius=defn["radius"],
                density=density,
                friction=defn["friction"],
                restitution=defn["restitution"],
            )

        self.body = world.create_dynamic_body(x, y, shape)
        self.body.angle = angle
        self.body.set_damping(defn["linear_damping"], defn["angular_damping"])
        self.body.user_data = self

        self.mass: float = defn["mass"]
        self.initial_energy: float = defn["energy"]
        self.energy: float = defn["energy"]
        self.spawns_debris: bool = defn["debris"]
        self.sprites = defn["sprites"]
        self.destroyed: bool = False

    @property
    def position(self) -> pygame.Vector2:
        return self.body.position

    def on_collision(self, other_body, is_ground: bool) -> None:
        if self.destroyed:
            return

        if is_ground:
            speed = self.body.velocity.length()
            other_mass = GROUND_EFFECTIVE_MASS
        else:
            speed = other_body.velocity.length()
            other = other_body.user_data
            other_mass = getattr(other, "mass", GROUND_EFFECTIVE_MASS)

        if speed <= DAMAGE_SPEED_THRESHOLD:
            return

        damage = speed * DAMAGE_COEFFICIENT * other_mass / self.mass
        self.energy -= damage

        if self.energy <= 0:
            self.destroyed = True

    def current_sprite_name(self) -> str:
        ratio = max(0.0, self.energy) / self.initial_energy
        # ceil(3 * energy / initial_energy), clamped to [1, 3], indexing
        # sprites[0..2] = [almost_destroyed, damaged, undamaged] -- ported
        # directly from destructible.script's damage_level computation.
        level = min(3, max(1, math.ceil(3 * ratio))) if ratio > 0 else 1
        return self.sprites[level - 1]

    def render(self, surface: pygame.Surface, camera) -> None:
        image = settings.TEXTURES[self.current_sprite_name()]
        size = (
            max(1, round(self.width * camera.zoom)),
            max(1, round(self.height * camera.zoom)),
        )
        scaled = pygame.transform.smoothscale(image, size)
        rotated = pygame.transform.rotate(scaled, -math.degrees(self.body.angle))
        rect = rotated.get_rect(center=camera.world_to_screen(self.body.position))
        surface.blit(rotated, rect)
