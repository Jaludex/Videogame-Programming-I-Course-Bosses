"""
ISPPV1 2023
Study Case: Ultimate Fantasy (RPG)

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the class Panel: a gale.ui.Panel subclass reproducing
the original's exact two-layer beveled look (a white outer rounded rect
with a dark grey inset), since gale.ui.Panel itself only draws a flat
single fill + border.
"""

import pygame

from gale.ui.panel import Panel as GalePanel


class Panel(GalePanel):
    def render(self, surface: pygame.Surface) -> None:
        if not self.visible:
            return

        pygame.draw.rect(surface, (255, 255, 255), self.rect, border_radius=3)
        inner = pygame.Rect(
            int(self.x) + 2, int(self.y) + 2, int(self.width) - 4, int(self.height) - 4
        )
        pygame.draw.rect(surface, (56, 56, 56), inner, border_radius=3)
