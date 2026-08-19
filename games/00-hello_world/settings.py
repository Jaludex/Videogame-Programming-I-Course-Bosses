"""
ISPPV1 2023
Study Case: Hello World

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the game settings that include the association of the
inputs with an their ids, constants of values to set up the game, and
fonts.

Original (C/Allegro5) note: the original quits on any key press. Gale's
input handler binds specific keys to actions rather than reacting to
"any key", so this port follows the same KEY_ESCAPE -> "quit" convention
every other Gale-based example in this course uses.
"""

import pygame

from gale import input_handler

input_handler.InputHandler.set_keyboard_action(input_handler.KEY_ESCAPE, "quit")
input_handler.InputHandler.set_keyboard_action(input_handler.KEY_b, "change_color")

TITLE = "Hello World"

# Size of our actual window. The original creates a plain 320x200
# window with no virtual-resolution scaling, so window and virtual
# sizes match here too.
WINDOW_WIDTH = 320
WINDOW_HEIGHT = 200

# Size we are trying to emulate
VIRTUAL_WIDTH = 320
VIRTUAL_HEIGHT = 200

# Allegro's al_create_builtin_font() is a small monospace pixel font
# built into the library; pygame.font.Font(None, ...) is the closest
# equivalent, a default font with no file dependency.
FONTS = {
    "default": pygame.font.Font(None, 16),
}
