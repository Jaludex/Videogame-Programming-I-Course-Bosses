"""
ISPPV1 2023
Study Case: Match-3

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the game settings that include the association of the
inputs with an their ids, constants of values to set up the game, sounds,
textures, frames, and fonts.
"""

from pathlib import Path

import pygame

from gale import input_handler

from src.frames_utility import generate_tile_frames

input_handler.InputHandler.set_keyboard_action(input_handler.KEY_ESCAPE, "quit")
input_handler.InputHandler.set_keyboard_action(input_handler.KEY_KP_ENTER, "enter")
input_handler.InputHandler.set_keyboard_action(input_handler.KEY_RETURN, "enter")
input_handler.InputHandler.set_keyboard_action(input_handler.KEY_UP, "up")
input_handler.InputHandler.set_keyboard_action(input_handler.KEY_DOWN, "down")
input_handler.InputHandler.set_mouse_click_action(input_handler.MOUSE_BUTTON_1, "click")

TITLE = "Match 3"

WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720

VIRTUAL_WIDTH = 512
VIRTUAL_HEIGHT = 288

BOARD_WIDTH = 8
BOARD_HEIGHT = 8

TILE_SIZE = 32

NUM_VARIETIES = 6
NUM_COLORS = 18

VALID_COLORS = [0, 5, 6, 10, 11, 13]
NUM_VALID_COLORS = len(VALID_COLORS)

BACKGROUND_SCROLL_SPEED = 40
BACKGROUND_LOOPING_POINT = -1024 + VIRTUAL_WIDTH - 4 + 51

BEFORE_HINT_TIME = 4

LEVEL_TIME = 60

BASE_DIR = Path(__file__).parent

TEXTURES = {
    "background": pygame.image.load(
        BASE_DIR / "assets" / "graphics" / "background.png"
    ),
    "tiles": pygame.image.load(BASE_DIR / "assets" / "graphics" / "match3.png"),
}

FRAMES = {"tiles": generate_tile_frames(TEXTURES["tiles"])}

SOUNDS = {
    "clock": pygame.mixer.Sound(BASE_DIR / "assets" / "sounds" / "clock.wav"),
    "error": pygame.mixer.Sound(BASE_DIR / "assets" / "sounds" / "error.wav"),
    "game-over": pygame.mixer.Sound(BASE_DIR / "assets" / "sounds" / "game-over.wav"),
    "match": pygame.mixer.Sound(BASE_DIR / "assets" / "sounds" / "match.wav"),
    "next-level": pygame.mixer.Sound(BASE_DIR / "assets" / "sounds" / "next-level.wav"),
    "select": pygame.mixer.Sound(BASE_DIR / "assets" / "sounds" / "select.wav"),
    "board_reset": pygame.mixer.Sound(BASE_DIR / "assets" / "sounds" / "board_reset.wav"),
    "wrong_move": pygame.mixer.Sound(BASE_DIR / "assets" / "sounds" / "wrong_move.wav"),
    "bomb_generated": pygame.mixer.Sound(BASE_DIR / "assets" / "sounds" / "bomb_generated.wav"),
    "play_bomb": pygame.mixer.Sound(BASE_DIR / "assets" / "sounds" / "play_bomb.wav"),
    "play_minibomb": pygame.mixer.Sound(BASE_DIR / "assets" / "sounds" / "play_minibomb.wav"),
}

pygame.mixer.music.load(BASE_DIR / "assets" / "sounds" / "music.mp3")
pygame.mixer.music.set_volume(0.5)

FONTS = {
    "small": pygame.font.Font(BASE_DIR / "assets" / "fonts" / "font.ttf", 12),
    "medium": pygame.font.Font(BASE_DIR / "assets" / "fonts" / "font.ttf", 24),
    "large": pygame.font.Font(BASE_DIR / "assets" / "fonts" / "font.ttf", 48),
    "huge": pygame.font.Font(BASE_DIR / "assets" / "fonts" / "font.ttf", 64),
}

COLOR_BLUE = (99, 155, 255)
COLOR_WARNING = (224, 171, 11)
COLOR_RED = (255, 115, 99)
