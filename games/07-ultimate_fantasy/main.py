"""
ISPPV1 2023
Study Case: Ultimate Fantasy (RPG)

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the main program to run the game.
"""

from gale.ui.theme import set_default_theme

from src.gui.theme import DEFAULT_THEME
from src.UltimateFantasy import UltimateFantasy

if __name__ == "__main__":
    set_default_theme(DEFAULT_THEME)
    game = UltimateFantasy()
    game.exec()
