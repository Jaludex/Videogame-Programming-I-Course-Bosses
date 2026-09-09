"""
ISPPV1 2023
Study Case: Throw a Bird

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the game settings that include the association of the
inputs with their ids, constants of values to set up the game, sounds,
textures, and fonts. This game has no sound assets in the original Defold
project, so no gale.mixer/pygame.mixer setup is done here.

Unlike lessons 00-07 (all tile/sprite-sheet based), every graphic here is
its own loose PNG (no atlas), so there is no gale.frames slicing: TEXTURES
values are used directly as whole-image surfaces.
"""

import pathlib

import pygame

from gale import input_handler

input_handler.InputHandler.set_keyboard_action(input_handler.KEY_ESCAPE, "quit")

# The only input this game needs: the primary mouse button, used both to
# aim (drag starting near the bird) and to pan the camera (drag starting
# anywhere else), and continuous motion while it is held down. See
# src/states/game/PlayState.py.
input_handler.InputHandler.set_mouse_click_action(
    input_handler.MOUSE_BUTTON_1, "touch"
)
input_handler.InputHandler.set_mouse_motion_action(None, "touch_motion")

TITLE = "Throw a Bird"

BASE_DIR = pathlib.Path(__file__).parent

VIRTUAL_WIDTH = 800
VIRTUAL_HEIGHT = 450

WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720

# Physics tuning. gale.physics.World defaults to pixels_per_meter=30 and
# fixed_timestep=1/60, both left as-is; only gravity is set explicitly.
# The original Defold project used physics.scale=0.02 (50px/meter) with
# gravity_y=-1000 -- neither number carries over meaningfully to gale's
# own default scale, so this is retuned from scratch for a "normal
# feeling" downward pull at ppm=30, matching gale's own physics examples
# (examples/leap, examples/hillclimb both use the same (0, 900)).
GRAVITY = (0, 900)

BG_COLOR = (213, 237, 246)

# The original level (a Defold .collection) is authored in Defold's Y-up
# convention; gale/pygame is Y-down. FLOOR_Y is an arbitrary reference
# used to flip every Y coordinate lifted from the .collection (see the
# brief): screen_y = FLOOR_Y - defold_y. Its exact value is not load
# bearing, it only needs to keep everything at a sane, mostly-positive
# world y (Box2D doesn't care about negative coordinates either way).
FLOOR_Y = 1300


def flip_y(defold_y: float) -> float:
    return FLOOR_Y - defold_y


FONTS = {
    "small": pygame.font.Font(BASE_DIR / "assets" / "fonts" / "RifficFree-Bold.ttf", 16),
    "medium": pygame.font.Font(BASE_DIR / "assets" / "fonts" / "RifficFree-Bold.ttf", 24),
    "large": pygame.font.Font(BASE_DIR / "assets" / "fonts" / "RifficFree-Bold.ttf", 48),
}


def _load(*parts: str) -> pygame.Surface:
    return pygame.image.load(BASE_DIR.joinpath("assets", "graphics", *parts))


TEXTURES = {
    # Buildings: stone, wood, and the wood-chip debris spawned on a wood
    # block's death. undamaged/damaged/almost_destroyed are the 3 sprite
    # frames a destructible with damage tiers swaps between as its energy
    # drops (see src/entity/Destructible.py).
    "stone-undamaged": _load("buildings", "elementStone011.png"),
    "stone-damaged": _load("buildings", "elementStone014.png"),
    "stone-almost-destroyed": _load("buildings", "elementStone046.png"),
    "wood-undamaged": _load("buildings", "elementWood012.png"),
    "wood-damaged": _load("buildings", "elementWood015.png"),
    "wood-almost-destroyed": _load("buildings", "elementWood047.png"),
    "debris-wood": _load("buildings", "debrisWood_1.png"),
    # Characters: the bird (parrot) and the two alien archetypes, each
    # with a single sprite (no visible damage tiers, they just track
    # energy until death).
    "parrot": _load("characters", "parrot.png"),
    "alien-square": _load("characters", "alienBlue_square.png"),
    "alien-round": _load("characters", "alienGreen_round.png"),
    # Background/world decoration (parallax scenery + the ground's own
    # tiled visual strip).
    "hills-far": _load("world", "Mountain 2.png"),
    "hills-near": _load("world", "Mountain 1.png"),
    "clouds-far": _load("world", "Clouds 2.png"),
    "clouds-near": _load("world", "Clouds 7.png"),
    "tree-1": _load("world", "Forest Tree 6.png"),
    "tree-2": _load("world", "Forest Tree 7.png"),
    "tree-3": _load("world", "Forest Tree 13.png"),
    "ground-strip": _load("world", "Walking Platforms 8.png"),
}

# ground1px.png is a single solid-color pixel used by the original as a
# cheap infinite-looking fill below the ground's visual strip -- rather
# than tiling a 1x1 image thousands of times, its color is sampled once
# and used to fill a plain rect (see src/world/Level.py).
GROUND_FILL_COLOR = _load("world", "ground1px.png").get_at((0, 0))
