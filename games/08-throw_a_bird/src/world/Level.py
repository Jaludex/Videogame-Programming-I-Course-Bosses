"""
ISPPV1 2023
Study Case: Throw a Bird

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the class Level: the static ground, the tower of
stone/wood/alien blocks, the two wind boundary zones, and the parallax
background -- everything in the original Defold .collection except the
parrot itself and the camera/input logic (both PlayState's concerns).

Layout numbers (ground extents, block positions) are lifted straight
from the brief's read-out of the original .collection, in Defold's Y-up,
level-local pixels; settings.flip_y() converts every Y to gale/pygame's
Y-down convention. x is unaffected by the flip. None of this is meant to
be pixel-perfect -- per the brief, it is a recreation, not a port of
exact numbers.
"""

import math
import random
from typing import List, Tuple

import pygame

from gale.physics.shapes import BoxShape
from gale.physics.world import World

import settings
from src.entity.Debris import DebrisChip
from src.entity.Destructible import Destructible
from src.world.Background import Background

# name, x, y (Defold Y-up, level-local), archetype, rotated 90 degrees
BLOCKS: List[Tuple[str, float, float, str, bool]] = [
    ("stone0", 2062, 145, "stone", False),
    ("stone1", 2247, 145, "stone", False),
    ("stone2", 2467, 145, "stone", False),
    ("stone3", 2652, 145, "stone", False),
    ("wood0", 2137, 215, "wood", False),
    ("wood1", 2357, 215, "wood", False),
    ("wood2", 2577, 215, "wood", False),
    ("stone4", 2062, 285, "stone", False),
    ("stone5", 2247, 285, "stone", False),
    ("stone6", 2467, 285, "stone", False),
    ("stone7", 2652, 285, "stone", False),
    ("wood3", 2062, 430, "wood", True),
    ("wood4", 2247, 430, "wood", True),
    ("wood6", 2467, 430, "wood", True),
    ("wood5", 2652, 430, "wood", True),
    ("stone8", 2062, 575, "stone", False),
    ("stone9", 2247, 575, "stone", False),
    ("stone10", 2467, 575, "stone", False),
    ("stone11", 2652, 575, "stone", False),
    ("wood7", 2137, 645, "wood", False),
    ("wood8", 2357, 645, "wood", False),
    ("wood9", 2577, 645, "wood", False),
    ("wood10", 2282, 790, "wood", True),
    ("wood11", 2432, 790, "wood", True),
    ("wood12", 2357, 935, "wood", False),
    ("alien_round0", 2357, 715, "alien_round", False),
    ("alien_round1", 2357, 1005, "alien_round", False),
    ("stone12", 2282, 1005, "stone", False),
    ("stone13", 2432, 1005, "stone", False),
    ("alien_square0", 2154, 285, "alien_square", False),
    ("alien_square1", 2357, 145, "alien_square", False),
    ("alien_square2", 2559, 285, "alien_square", False),
]

# Ground world-space center and half-extents, taken directly from the
# brief (ground instance position (512, 295) + local collision-shape
# offset (1377, -223), half-extents 6448.155 x 36.718).
GROUND_CENTER_X = 1889
GROUND_TOP_DEFOLD_Y = 72 + 36.718
GROUND_HALF_WIDTH = 6448.155
# Thickened well past the original's thin collision box, purely so the
# ground reads as a solid slab instead of a sliver (there is no floor
# graphic below the visible strip otherwise).
GROUND_VISUAL_HEIGHT = 600.0

BIRD_START_DEFOLD = (300, 300)

# The wind zones bound the *playable* area (slingshot to tower, plus a
# margin to throw past it), not the ground strip's full extent -- the
# strip is ~13000px wide purely for the parallax background to have
# something to sit on, so anchoring the zones to ground_x_range (as a
# first version of this file did) put them ~5000-6000px past the tower,
# effectively unreachable: the bird could fly clean off into empty space
# forever without ever being turned back. 900 (a second version) then
# read as too close, sitting barely past the slingshot/tower; widened.
WIND_ZONE_MARGIN = 2200.0
_BLOCK_XS = [dx for _name, dx, _dy, _archetype, _rot90 in BLOCKS]
PLAY_AREA_LEFT = min(BIRD_START_DEFOLD[0], min(_BLOCK_XS)) - WIND_ZONE_MARGIN
PLAY_AREA_RIGHT = max(_BLOCK_XS) + WIND_ZONE_MARGIN

# Wide enough to give a fast-moving body several frames to be blended to
# a stop-and-turn (see _apply_wind) instead of crossing in a couple of
# frames, which is what a thinner zone (150, a second version) did.
WIND_ZONE_WIDTH = 700.0
WIND_ZONE_HEIGHT = 6000.0
# wind.script's own approach -- a flat force applied for as long as a
# body overlaps the trigger volume -- didn't translate directly (see the
# WIND_ZONE_WIDTH comment above for the too-thin-zone half of that), and
# a second version's fix, snapping the x-velocity straight to a target
# the instant contact starts, read as exaggeratedly strong/aggressive:
# a fast incoming body would have its velocity reversed in a single
# frame, a multi-thousand-px/s change with no transition at all.
#
# Every frame a body touches a wind zone, its x-velocity is now blended
# a fraction of the way toward this target speed (directed back toward
# the play area) instead of snapped to it outright -- see
# WIND_BLEND_RATE. Combined with the wider zone above, that spreads the
# turn-around over several frames, so it reads as a wind gust slowing
# and reversing you, not a wall slamming you back.
WIND_BOUNCE_SPEED = 650.0
# Exponential-smoothing rate (same style as PlayState's camera zoom
# lerp): higher = the velocity blend catches up to the target faster.
WIND_BLEND_RATE = 5.0

DEBRIS_PER_BLOCK = 5
DEBRIS_SCATTER = 30

# The "enemies" for a win condition -- the aliens, not the stone/wood
# structure itself (knocking the tower down is how you get at them, not
# the goal in its own right).
ENEMY_ARCHETYPES = {"alien_square", "alien_round"}


class Level:
    def __init__(self, world: World) -> None:
        self.world = world
        self.background = Background()
        self.blocks: List[Destructible] = []
        self.debris: List[DebrisChip] = []

        self._build_ground()
        self._build_blocks()
        self._build_wind_zones()

        self._enemy_count = sum(
            1 for block in self.blocks if block.archetype in ENEMY_ARCHETYPES
        )

    @property
    def all_enemies_defeated(self) -> bool:
        return self._enemy_count > 0 and not any(
            block.archetype in ENEMY_ARCHETYPES for block in self.blocks
        )

    @property
    def bird_start(self) -> pygame.Vector2:
        x, y = BIRD_START_DEFOLD
        return pygame.Vector2(x, settings.flip_y(y))

    @property
    def ground_x_range(self) -> Tuple[float, float]:
        return (
            GROUND_CENTER_X - GROUND_HALF_WIDTH,
            GROUND_CENTER_X + GROUND_HALF_WIDTH,
        )

    def _build_ground(self) -> None:
        self.ground_top_y = settings.flip_y(GROUND_TOP_DEFOLD_Y)
        center_y = self.ground_top_y + GROUND_VISUAL_HEIGHT / 2

        self.ground_body = self.world.create_static_body(
            GROUND_CENTER_X,
            center_y,
            BoxShape(GROUND_HALF_WIDTH * 2, GROUND_VISUAL_HEIGHT, friction=1.0),
        )
        self.ground_body.user_data = "ground"

    def _build_blocks(self) -> None:
        for _name, dx, dy, archetype, rot90 in BLOCKS:
            angle = math.pi / 2 if rot90 else 0.0
            self.blocks.append(
                Destructible(self.world, dx, settings.flip_y(dy), archetype, angle)
            )

    def _build_wind_zones(self) -> None:
        center_y = self.ground_top_y - WIND_ZONE_HEIGHT / 2 + 400

        self.wind_left = self.world.create_static_body(
            PLAY_AREA_LEFT,
            center_y,
            BoxShape(WIND_ZONE_WIDTH, WIND_ZONE_HEIGHT, is_sensor=True),
        )
        self.wind_left.user_data = "wind"

        self.wind_right = self.world.create_static_body(
            PLAY_AREA_RIGHT,
            center_y,
            BoxShape(WIND_ZONE_WIDTH, WIND_ZONE_HEIGHT, is_sensor=True),
        )
        self.wind_right.user_data = "wind"

    def update(self, dt: float) -> None:
        self._apply_wind(dt)
        self._collect_destroyed()
        self.debris = [chip for chip in self.debris if chip.alive]

    def fixed_update(self) -> None:
        self._apply_collision_damage()

    def _apply_collision_damage(self) -> None:
        # Blocks placed touching (or nearly touching) their neighbors in
        # BLOCKS settle into permanent contact within the first few physics
        # steps after the level loads -- gravity closes the small gaps at a
        # speed under DAMAGE_SPEED_THRESHOLD, so that one-time contact never
        # registers damage, and since the pair never separates again,
        # world.on_collision_begin never fires for it a second time either.
        # A block later punched into an already-touching neighbor (an alien
        # boxed in by its neighbors, most commonly) would then never deal
        # damage through that contact no matter how hard the impact, since
        # begin-contact only fires on a fresh touch. Checking every body
        # still in contact on every fixed step instead -- not just the
        # instant contact begins -- catches that case too; the existing
        # DAMAGE_SPEED_THRESHOLD in Destructible.on_collision already keeps
        # a resting contact from bleeding energy every step.
        for block in self.blocks:
            if block.destroyed:
                continue

            for other in block.body.touching_bodies:
                self._handle_pair(block.body, other)

    def _apply_wind(self, dt: float) -> None:
        # sign > 0 (left zone) pushes toward +x, sign < 0 (right zone)
        # pushes toward -x -- both back toward the play area's center.
        factor = 1.0 - math.exp(-WIND_BLEND_RATE * dt)

        for wind_body, sign in ((self.wind_left, 1), (self.wind_right, -1)):
            for body in wind_body.touching_bodies:
                target_vx = sign * WIND_BOUNCE_SPEED
                vx = body.velocity.x

                if (sign > 0 and vx < target_vx) or (sign < 0 and vx > target_vx):
                    body.set_velocity(vx + (target_vx - vx) * factor, body.velocity.y)

    def _collect_destroyed(self) -> None:
        survivors = []

        for block in self.blocks:
            if not block.destroyed:
                survivors.append(block)
                continue

            if block.spawns_debris:
                position = block.position
                for _ in range(DEBRIS_PER_BLOCK):
                    offset_x = random.uniform(-DEBRIS_SCATTER, DEBRIS_SCATTER)
                    offset_y = random.uniform(-DEBRIS_SCATTER, DEBRIS_SCATTER)
                    self.debris.append(
                        DebrisChip(position.x + offset_x, position.y + offset_y)
                    )

            self.world.destroy_body(block.body)

        self.blocks = survivors

    def _handle_pair(self, body, other) -> None:
        entity = body.user_data

        if not isinstance(entity, Destructible):
            return

        if other.user_data == "ground":
            entity.on_collision(other, is_ground=True)
        elif other.user_data == "wind":
            return
        elif hasattr(other.user_data, "mass"):
            entity.on_collision(other, is_ground=False)

    def render(self, surface: pygame.Surface, camera) -> None:
        self.background.render(surface, camera)
        self._render_ground(surface, camera)

        for block in self.blocks:
            block.render(surface, camera)

        for chip in self.debris:
            chip.render(surface, camera)

    def _render_ground(self, surface: pygame.Surface, camera) -> None:
        top_screen_y = round((self.ground_top_y - camera.offset[1]) * camera.zoom)
        fill_rect = pygame.Rect(
            0, max(0, top_screen_y), surface.get_width(), surface.get_height()
        )
        pygame.draw.rect(surface, settings.GROUND_FILL_COLOR, fill_rect)

        strip = settings.TEXTURES["ground-strip"]
        strip_width, strip_height = strip.get_size()
        size = (
            max(1, round(strip_width * camera.zoom)),
            max(1, round(strip_height * camera.zoom)),
        )
        scaled_strip = pygame.transform.scale(strip, size)

        left, right = self.ground_x_range
        x = left

        while x < right:
            center = (x + strip_width / 2, self.ground_top_y + strip_height / 2)
            rect = scaled_strip.get_rect(center=camera.world_to_screen(center))

            if rect.right >= 0 and rect.left <= surface.get_width():
                surface.blit(scaled_strip, rect)

            x += strip_width
