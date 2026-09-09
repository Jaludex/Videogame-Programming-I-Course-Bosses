"""
ISPPV1 2023
Study Case: Ultimate Fantasy (RPG)

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains DEFAULT_THEME, a gale.ui.Theme matching the original's
color palette (white border, dark grey fill, white text), applied once at
startup via gale.ui.theme.set_default_theme so every gale.ui widget used
throughout the project (TextBox, ProgressBar, ...) looks consistent with
it, without having to pass a theme explicitly at every call site.
"""

import pygame

from gale.ui.theme import Theme

import settings

DEFAULT_THEME = Theme(
    font=settings.FONTS["small"],
    text_color=pygame.Color(255, 255, 255),
    background_color=pygame.Color(56, 56, 56),
    border_color=pygame.Color(255, 255, 255),
    border_width=2,
    accent_color=pygame.Color(189, 32, 32),
    padding=3,
)

# HP/EXP bars are only 3px tall, so DEFAULT_THEME's 2px white border (sized
# for panels) covers nearly the whole bar regardless of fill color, making
# it look blank/white. The original drew these with a thin black outline
# and no separate background fill instead.
BAR_THEME = Theme(
    font=settings.FONTS["small"],
    text_color=pygame.Color(255, 255, 255),
    background_color=pygame.Color(0, 0, 0),
    border_color=pygame.Color(0, 0, 0),
    border_width=1,
    accent_color=pygame.Color(189, 32, 32),
    padding=0,
)
