"""
ISPPV1 2023
Study Case: Ultimate Fantasy (RPG)

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the game settings that include the association of the
inputs with their ids, constants of values to set up the game, sounds,
textures, frames, and fonts.
"""

import pathlib

import pygame

from gale import frames
from gale import input_handler
from gale import tilemap

input_handler.InputHandler.set_keyboard_action(input_handler.KEY_ESCAPE, "quit")
input_handler.InputHandler.set_keyboard_action(input_handler.KEY_LEFT, "move_left")
input_handler.InputHandler.set_keyboard_action(input_handler.KEY_RIGHT, "move_right")
input_handler.InputHandler.set_keyboard_action(input_handler.KEY_UP, "move_up")
input_handler.InputHandler.set_keyboard_action(input_handler.KEY_DOWN, "move_down")
input_handler.InputHandler.set_keyboard_action(input_handler.KEY_SPACE, "space")
input_handler.InputHandler.set_keyboard_action(input_handler.KEY_RETURN, "enter")
input_handler.InputHandler.set_keyboard_action(input_handler.KEY_KP_ENTER, "enter")
input_handler.InputHandler.set_keyboard_action(input_handler.KEY_p, "pause")
input_handler.InputHandler.set_keyboard_action(input_handler.KEY_c, "continue")

TITLE = "Ultimate Fantasy"

# gale.save.SaveManager slot used for this game's single save file.
SAVE_SLOT = "slot1"

BASE_DIR = pathlib.Path(__file__).parent

VIRTUAL_WIDTH = 384
VIRTUAL_HEIGHT = 224

WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720

TILE_SIZE = 16

TILE_WIDTH = VIRTUAL_WIDTH // TILE_SIZE
TILE_HEIGHT = VIRTUAL_HEIGHT // TILE_SIZE

#
# tile ids (1-based, matching the tilesheet's slicing -- see settings.frame())
#
TILE_IDS = {
    "grass": [46, 47],
    "flowers": [16, 24, 32, 40, 48, 56, 64, 72],
    "empty": 101,
    "tall-grass": 42,
    "half-tall-grass": 50,
    "top-left-fence": 73,
    "top-fence": 74,
    "top-right-fence": 75,
    "left-fence": 81,
    "right-fence": 83,
    "bottom-left-fence": 89,
    "bottom-fence": 90,
    "bottom-right-fence": 91,
    "border-left-fence": 65,
    "border-right-fence": 66,
    "border-top-left-fence": 88,
    "border-bottom-left-fence": 87,
    "border-top-right-fence": 96,
    "border-bottom-right-fence": 95,
}

TEXTURES = {
    "tiles": pygame.image.load(BASE_DIR / "assets" / "graphics" / "sheet.png"),
    "background": pygame.image.load(BASE_DIR / "assets" / "graphics" / "background.png"),
    "cursor-right": pygame.image.load(
        BASE_DIR / "assets" / "graphics" / "cursor_right.png"
    ),
    "cursor-up": pygame.image.load(BASE_DIR / "assets" / "graphics" / "cursor_up.png"),
    "healer-female": pygame.image.load(
        BASE_DIR / "assets" / "graphics" / "characters" / "healer_f.png"
    ),
    "healer-male": pygame.image.load(
        BASE_DIR / "assets" / "graphics" / "characters" / "healer_m.png"
    ),
    "mage-female": pygame.image.load(
        BASE_DIR / "assets" / "graphics" / "characters" / "mage_f.png"
    ),
    "mage-male": pygame.image.load(
        BASE_DIR / "assets" / "graphics" / "characters" / "mage_m.png"
    ),
    "warrior-female": pygame.image.load(
        BASE_DIR / "assets" / "graphics" / "characters" / "warrior_f.png"
    ),
    "warrior-male": pygame.image.load(
        BASE_DIR / "assets" / "graphics" / "characters" / "warrior_m.png"
    ),
    "ranger-female": pygame.image.load(
        BASE_DIR / "assets" / "graphics" / "characters" / "ranger_f.png"
    ),
    "ranger-male": pygame.image.load(
        BASE_DIR / "assets" / "graphics" / "characters" / "ranger_m.png"
    ),
    "npc-female": pygame.image.load(
        BASE_DIR / "assets" / "graphics" / "characters" / "townfolk_f.png"
    ),
    "npc-male": pygame.image.load(
        BASE_DIR / "assets" / "graphics" / "characters" / "townfolk_m.png"
    ),
    "slime": pygame.image.load(BASE_DIR / "assets" / "graphics" / "enemies" / "slime.png"),
    "small-worm": pygame.image.load(
        BASE_DIR / "assets" / "graphics" / "enemies" / "small_worm.png"
    ),
    "snake": pygame.image.load(BASE_DIR / "assets" / "graphics" / "enemies" / "snake.png"),
    "pumpking": pygame.image.load(
        BASE_DIR / "assets" / "graphics" / "enemies" / "pumpking.png"
    ),
    "man-eater-flower": pygame.image.load(
        BASE_DIR / "assets" / "graphics" / "enemies" / "man_eater_flower.png"
    ),
}

# Shared by every gale.tilemap.TileMap in the game (world regions and
# battle backgrounds alike): tile ids in TILE_IDS above are 1-based,
# matching this tileset's default first_gid, so they double as gids
# with no remapping.
TILESET = tilemap.Tileset(TEXTURES["tiles"], TILE_SIZE, TILE_SIZE)

FRAMES = {
    "healer-female": frames.generate_frames(TEXTURES["healer-female"], 16, 18),
    "healer-male": frames.generate_frames(TEXTURES["healer-male"], 16, 18),
    "mage-female": frames.generate_frames(TEXTURES["mage-female"], 16, 18),
    "mage-male": frames.generate_frames(TEXTURES["mage-male"], 16, 18),
    "warrior-female": frames.generate_frames(TEXTURES["warrior-female"], 16, 18),
    "warrior-male": frames.generate_frames(TEXTURES["warrior-male"], 16, 18),
    "ranger-female": frames.generate_frames(TEXTURES["ranger-female"], 16, 18),
    "ranger-male": frames.generate_frames(TEXTURES["ranger-male"], 16, 18),
    "npc-female": frames.generate_frames(TEXTURES["npc-female"], 16, 18),
    "npc-male": frames.generate_frames(TEXTURES["npc-male"], 16, 18),
    "slime": frames.generate_frames(TEXTURES["slime"], 16, 16),
    "small-worm": frames.generate_frames(TEXTURES["small-worm"], 16, 16),
    "snake": frames.generate_frames(TEXTURES["snake"], 16, 16),
    "pumpking": frames.generate_frames(TEXTURES["pumpking"], 23, 23),
    "man-eater-flower": frames.generate_frames(TEXTURES["man-eater-flower"], 30, 38),
}


def frame(texture_id, one_based_index):
    """
    Every frame index in this project's own code (tile IDs, quad numbers,
    animation frame lists) is written 1-based, matching the original
    Lua/LOVE2D source it was ported from, since gale.frames.generate_frames
    (like Lua tables) still needs a 0-based lookup.
    """
    return FRAMES[texture_id][one_based_index - 1]


FONTS = {
    "small": pygame.font.Font(BASE_DIR / "assets" / "fonts" / "font.ttf", 8),
    "medium": pygame.font.Font(BASE_DIR / "assets" / "fonts" / "font.ttf", 16),
    "large": pygame.font.Font(BASE_DIR / "assets" / "fonts" / "font.ttf", 32),
    "ff": pygame.font.Font(BASE_DIR / "assets" / "fonts" / "finalf.ttf", 48),
    "ff-small": pygame.font.Font(BASE_DIR / "assets" / "fonts" / "finalf.ttf", 24),
}

SOUNDS = {
    "intro": pygame.mixer.Sound(BASE_DIR / "assets" / "sounds" / "intro.mp3"),
    "town": pygame.mixer.Sound(BASE_DIR / "assets" / "sounds" / "town.mp3"),
    "world": pygame.mixer.Sound(BASE_DIR / "assets" / "sounds" / "world.mp3"),
    "blip": pygame.mixer.Sound(BASE_DIR / "assets" / "sounds" / "blip.wav"),
    "battle": pygame.mixer.Sound(BASE_DIR / "assets" / "sounds" / "battle.mp3"),
    "run": pygame.mixer.Sound(BASE_DIR / "assets" / "sounds" / "run.wav"),
    "hit": pygame.mixer.Sound(BASE_DIR / "assets" / "sounds" / "hit.wav"),
    "powerup": pygame.mixer.Sound(BASE_DIR / "assets" / "sounds" / "powerup.wav"),
    "arrows": pygame.mixer.Sound(BASE_DIR / "assets" / "sounds" / "arrows.wav"),
    "flame": pygame.mixer.Sound(BASE_DIR / "assets" / "sounds" / "flame.ogg"),
    "game-over": pygame.mixer.Sound(BASE_DIR / "assets" / "sounds" / "game_over.mp3"),
    "victory": pygame.mixer.Sound(BASE_DIR / "assets" / "sounds" / "victory.wav"),
    "levelup": pygame.mixer.Sound(BASE_DIR / "assets" / "sounds" / "levelup.wav"),
    "exp": pygame.mixer.Sound(BASE_DIR / "assets" / "sounds" / "exp.wav"),
    "the-end": pygame.mixer.Sound(BASE_DIR / "assets" / "sounds" / "the_end.mp3"),
}

MUSIC_CHANNELS = {
    "intro": None,
    "town": None,
    "world": None,
    "battle": None,
    "game-over": None,
    "the-end": None,
}


def play_music(name: str) -> None:
    stop_music(name)
    MUSIC_CHANNELS[name] = SOUNDS[name].play(loops=-1)


def stop_music(name: str) -> None:
    channel = MUSIC_CHANNELS.get(name)

    if channel is not None:
        channel.stop()
        MUSIC_CHANNELS[name] = None


def pause_music(name: str) -> None:
    channel = MUSIC_CHANNELS.get(name)

    if channel is not None:
        channel.pause()


def resume_music(name: str) -> None:
    channel = MUSIC_CHANNELS.get(name)

    if channel is not None:
        channel.unpause()
