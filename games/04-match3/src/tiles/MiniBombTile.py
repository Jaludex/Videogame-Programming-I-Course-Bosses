import pygame

import settings
from src.tiles.Tile import Tile

_OBJECTIVE_TILES = ((1, 0), (0, 1), (0, -1), (-1, 0))

class MiniBombTile(Tile):
    def __init__(self, i: int, j: int, color: int) -> None:
        super().__init__(i, j, color, 1)
        settings.SOUNDS["bomb_generated"].stop()
        settings.SOUNDS["bomb_generated"].play()

    def play(self, tiles, match):
        for pair in _OBJECTIVE_TILES:
            off_i, off_j = pair
            obj_i = self.i + off_i
            obj_j = self.j + off_j

            if (0 <= obj_i < settings.BOARD_WIDTH and 
                0 <= obj_j < settings.BOARD_HEIGHT and
                tiles[obj_i][obj_j] not in match
                ):
                match.append(tiles[obj_i][obj_j])

        settings.SOUNDS["play_minibomb"].stop()
        settings.SOUNDS["play_minibomb"].play()