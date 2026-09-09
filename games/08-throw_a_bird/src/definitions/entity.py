"""
ISPPV1 2023
Study Case: Throw a Bird

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains ARCHETYPES: the per-archetype physics/HP/sprite data
ported from the original Defold .go files' destructible.script properties
(stone/wood/alien_square/alien_round), plus BIRD (the parrot), and the two
helper functions used to turn a *desired* mass (the numbers in the brief,
carried over from the Lua source for their relative proportions) into the
density gale.physics.shapes actually takes.

gale.physics.Body has no direct "set this body's mass" call, only a
density per fixture, and density is a mass-per-unit-*area* figure in
Box2D's own meters, not gale's public pixel units. Box2D's fixture area
(in meters^2) for a WxH box built from pixel width/height W, H at a given
pixels_per_meter is (W/ppm) * (H/ppm), so solving density * area = mass
for density gives mass * ppm^2 / (W * H) (and the circle equivalent below).
This keeps every archetype's mass matching the brief's numbers exactly
(up to Box2D's own polygon-mass approximation), without ever touching
Box2D directly.
"""

import math
from typing import Any, Dict

PIXELS_PER_METER = 30.0


def density_for_box(mass: float, width: float, height: float) -> float:
    area_m2 = (width / PIXELS_PER_METER) * (height / PIXELS_PER_METER)
    return mass / area_m2


def density_for_circle(mass: float, radius: float) -> float:
    area_m2 = math.pi * (radius / PIXELS_PER_METER) ** 2
    return mass / area_m2


# Every archetype that can take damage and be destroyed. "sprites" holds
# the 3 damage-tier frame names (low energy first, matching the Lua
# damage_levels table) for stone/wood; alien_square/alien_round have a
# single sprite reused at every tier (no visible damage in the original).
ARCHETYPES: Dict[str, Dict[str, Any]] = {
    "stone": {
        "shape": "box",
        "width": 70,
        "height": 70,
        "mass": 500,
        "friction": 1.0,
        "restitution": 0.0,
        "angular_damping": 0.0,
        "linear_damping": 0.0,
        "energy": 2000,
        "debris": False,
        "sprites": ["stone-almost-destroyed", "stone-damaged", "stone-undamaged"],
    },
    "wood": {
        "shape": "box",
        # Matches the source sprite (elementWood0*.png) size, 220x70.
        # A previous half-scale (110x35) attempt at a "shelf" look left
        # every row of the tower a visible gap above the row below it
        # (the layout's y-spacing assumes full-size blocks), so the whole
        # structure collapsed under gravity before the bird was ever
        # thrown.
        "width": 220,
        "height": 70,
        "mass": 200,
        "friction": 1.0,
        "restitution": 0.0,
        "angular_damping": 0.0,
        "linear_damping": 0.0,
        "energy": 1000,
        "debris": True,
        "sprites": ["wood-almost-destroyed", "wood-damaged", "wood-undamaged"],
    },
    "alien_square": {
        "shape": "box",
        "width": 70,
        "height": 70,
        "mass": 500,
        "friction": 0.9,
        "restitution": 0.1,
        "angular_damping": 0.0,
        "linear_damping": 0.0,
        "energy": 500,
        "debris": False,
        "sprites": ["alien-square", "alien-square", "alien-square"],
    },
    "alien_round": {
        "shape": "circle",
        "radius": 35,
        "mass": 400,
        "friction": 0.9,
        "restitution": 0.1,
        "angular_damping": 0.7,
        "linear_damping": 0.1,
        "energy": 400,
        "debris": False,
        "sprites": ["alien-round", "alien-round", "alien-round"],
    },
}

# The parrot: a heavy, invulnerable circle -- no destructible.script
# equivalent, it never takes damage.
BIRD = {
    "radius": 35,
    "mass": 2500,
    "friction": 1.0,
    "restitution": 0.1,
    "angular_damping": 0.7,
    "linear_damping": 0.1,
    "sprite": "parrot",
}
