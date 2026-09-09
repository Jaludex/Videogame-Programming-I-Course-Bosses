"""
ISPPV1 2023
Study Case: Throw a Bird

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the class Background: the parallax mountains/clouds/
trees decorating the level. Purely cosmetic and low priority per the
brief, so exact original positions are not reproduced -- instead, each
layer is procedurally tiled/scattered across the level's width at the
approximate height and parallax factor (how much slower than the camera
it scrolls) the brief describes.
"""

from typing import List, Tuple

import pygame

import settings


class Background:
    def __init__(self) -> None:
        # (texture_key, world_x, world_y, parallax_factor, scale)
        self.layers: List[Tuple[str, float, float, float, float]] = []

        self._add_tiled("hills-far", y_defold=453, spacing=1310, x_from=-1900, x_to=8600, parallax=0.25)
        self._add_tiled("hills-near", y_defold=291, spacing=777, x_from=-2400, x_to=8600, parallax=0.45)

        for i, x in enumerate(range(-3200, 9200, 900)):
            y_defold = 500 + (i % 3) * 300
            key = "clouds-far" if i % 2 == 0 else "clouds-near"
            parallax = 0.15 if key == "clouds-far" else 0.3
            self.layers.append((key, x, settings.flip_y(y_defold), parallax, 0.6))

        tree_keys = ["tree-1", "tree-2", "tree-3"]
        for i, x in enumerate(range(-3600, 8900, 550)):
            y_defold = 197 + (i % 3) * 40
            self.layers.append(
                (tree_keys[i % 3], x, settings.flip_y(y_defold), 0.7, 0.45)
            )

    def _add_tiled(
        self,
        key: str,
        y_defold: float,
        spacing: float,
        x_from: float,
        x_to: float,
        parallax: float,
    ) -> None:
        y = settings.flip_y(y_defold)
        x = x_from
        while x <= x_to:
            self.layers.append((key, x, y, parallax, 1.0))
            x += spacing

    def render(self, surface: pygame.Surface, camera) -> None:
        offset_x, offset_y = camera.offset
        surface_width = surface.get_width()

        for key, x, y, parallax, scale in self.layers:
            screen_x = (x - offset_x * parallax) * camera.zoom
            screen_y = (y - offset_y * parallax) * camera.zoom

            image = settings.TEXTURES[key]
            width, height = image.get_size()
            size = (
                max(1, round(width * scale * camera.zoom)),
                max(1, round(height * scale * camera.zoom)),
            )

            if screen_x + size[0] / 2 < 0 or screen_x - size[0] / 2 > surface_width:
                continue

            scaled = pygame.transform.smoothscale(image, size)
            rect = scaled.get_rect(center=(screen_x, screen_y))
            surface.blit(scaled, rect)
