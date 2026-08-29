import pygame

import settings
from src.tiles.Tile import Tile

class BombTile(Tile):
    def __init__(self, i: int, j: int, color: int) -> None:
        super().__init__(i, j, color, 5)
        settings.SOUNDS["bomb_generated"].stop()
        settings.SOUNDS["bomb_generated"].play()

    def play(self, tiles, match):
        for row in tiles:
            for tile in row:
                if tile.color == self.color and tile not in match:
                    match.append(tile)

        settings.SOUNDS["play_bomb"].stop()
        settings.SOUNDS["play_bomb"].play()
        