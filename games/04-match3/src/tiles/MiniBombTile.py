import pygame

import settings
from src.tiles.Tile import Tile

class MiniBombTile(Tile):
    def __init__(self, i: int, j: int, color: int) -> None:
        super().__init__(i, j, color, 1)
        settings.SOUNDS["bomb_generated"].stop()
        settings.SOUNDS["bomb_generated"].play()

    def play(self, tiles, match):
        obj_j = self.j
        for i in range(0, 8):
            obj_i = i
            if (0 <= obj_i < settings.BOARD_WIDTH and 
                0 <= obj_j < settings.BOARD_HEIGHT and
                tiles[obj_i][obj_j] not in match
                ):
                match.append(tiles[obj_i][obj_j])

        obj_i = self.i
        for j in range(0, 8):
            obj_j = j
            if (0 <= obj_i < settings.BOARD_WIDTH and 
                0 <= obj_j < settings.BOARD_HEIGHT and
                tiles[obj_i][obj_j] not in match
                ):
                match.append(tiles[obj_i][obj_j])


        settings.SOUNDS["play_minibomb"].stop()
        settings.SOUNDS["play_minibomb"].play()