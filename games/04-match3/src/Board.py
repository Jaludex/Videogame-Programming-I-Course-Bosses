"""
ISPPV1 2023
Study Case: Match-3

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the class Board.
"""

from typing import List, Optional, Tuple, Any, Dict, Set

import pygame
import copy
import random

import settings
from src.tiles.Tile import Tile
from src.tiles.MiniBombTile import MiniBombTile
from src.tiles.BombTile import BombTile

class Board:
    def __init__(self, x: int, y: int) -> None:
        self.x = x
        self.y = y
        self.matches: List[List[Tile]] = []
        self.tiles: List[List[Tile]] = []
        self._initialize_tiles()

    def render(self, surface: pygame.Surface) -> None:
        for row in self.tiles:
            for tile in row:
                tile.render(surface, self.x, self.y)

    def _is_match_generated(self, i: int, j: int, color: int) -> bool:
        if (
            i >= 2
            and self.tiles[i - 1][j].color == color
            and self.tiles[i - 2][j].color == color
        ):
            return True

        return (
            j >= 2
            and self.tiles[i][j - 1].color == color
            and self.tiles[i][j - 2].color == color
        )

    def _initialize_tiles(self) -> None:
        self.tiles = [
            [None for _ in range(settings.BOARD_WIDTH)]
            for _ in range(settings.BOARD_HEIGHT)
        ]
        for i in range(settings.BOARD_HEIGHT):
            for j in range(settings.BOARD_WIDTH):
                color = settings.VALID_COLORS[random.randint(0, settings.NUM_VALID_COLORS - 1)]
                while self._is_match_generated(i, j, color):
                    color = settings.VALID_COLORS[random.randint(0, settings.NUM_VALID_COLORS - 1)]

                self.tiles[i][j] = Tile(
                    i, j, color, 0
                )

    def _calculate_match_rec(self, tile: Tile) -> Set[Tile]:
        if tile in self.in_stack:
            return []

        self.in_stack.add(tile)

        color_to_match = tile.color

        ## Check horizontal match
        h_match: List[Tile] = []

        # Check left
        if tile.j > 0:
            left = max(0, tile.j - 2)
            for j in range(tile.j - 1, left - 1, -1):
                if self.tiles[tile.i][j].color != color_to_match:
                    break
                h_match.append(self.tiles[tile.i][j])

        # Check right
        if tile.j < settings.BOARD_WIDTH - 1:
            right = min(settings.BOARD_WIDTH - 1, tile.j + 2)
            for j in range(tile.j + 1, right + 1):
                if self.tiles[tile.i][j].color != color_to_match:
                    break
                h_match.append(self.tiles[tile.i][j])

        ## Check vertical match
        v_match: List[Tile] = []

        # Check top
        if tile.i > 0:
            top = max(0, tile.i - 2)
            for i in range(tile.i - 1, top - 1, -1):
                if self.tiles[i][tile.j].color != color_to_match:
                    break
                v_match.append(self.tiles[i][tile.j])

        # Check bottom
        if tile.i < settings.BOARD_HEIGHT - 1:
            bottom = min(settings.BOARD_HEIGHT - 1, tile.i + 2)
            for i in range(tile.i + 1, bottom + 1):
                if self.tiles[i][tile.j].color != color_to_match:
                    break
                v_match.append(self.tiles[i][tile.j])

        match: List[Tile] = []

        if len(h_match) >= 2:
            for t in h_match:
                if t not in self.in_match:
                    self.in_match.add(t)
                    match.append(t)

        if len(v_match) >= 2:
            for t in v_match:
                if t not in self.in_match:
                    self.in_match.add(t)
                    match.append(t)

        if len(match) > 0:
            if tile not in self.in_match:
                self.in_match.add(tile)
                match.append(tile)

        for t in match:
            match += self._calculate_match_rec(t)

        self.in_stack.remove(tile)
        return match

    def calculate_matches_for(
        self, new_tiles: List[Tile]
    ) -> Optional[List[List[Tile]]]:
        self.in_match: Set[Tile] = set()
        self.in_stack: Set[Tile] = set()

        for tile in new_tiles:
            if tile in self.in_match:
                continue
            match = self._calculate_match_rec(tile)
            if len(match) > 0:
                self.matches.append(match)

        delattr(self, "in_match")
        delattr(self, "in_stack")

        return self.matches if len(self.matches) > 0 else None

    def remove_matches(self) -> None:
        for match in self.matches:
            match_len = len(match)

            can_spawn_bombs = True

            for tile in match:
                if tile.variety != 0:
                    can_spawn_bombs = False
                    break
            
            if can_spawn_bombs and match_len >= 4:
                obj_tile = match[-1]
                
                if match_len == 4:
                    new_tile = MiniBombTile(obj_tile.i, obj_tile.j, obj_tile.color)
                else:
                    new_tile = BombTile(obj_tile.i, obj_tile.j, obj_tile.color)

                for tile in match:
                    self.tiles[tile.i][tile.j] = None

                self.tiles[obj_tile.i][obj_tile.j] = new_tile

            else:
                for tile in match:
                    self.tiles[tile.i][tile.j] = None

        self.matches = []

    def get_falling_tiles(self) -> Tuple[Any, Dict[str, Any]]:
        # List of tweens to create
        tweens: Tuple[Tile, Dict[str, Any]] = []

        # for each column, go up tile by tile until we hit a space
        for j in range(settings.BOARD_WIDTH):
            space = False
            space_i = -1
            i = settings.BOARD_HEIGHT - 1

            while i >= 0:
                tile = self.tiles[i][j]

                # if our previous tile was a space
                if space:
                    # if the current tile is not a space
                    if tile is not None:
                        self.tiles[space_i][j] = tile
                        tile.i = space_i

                        # set its prior position to None
                        self.tiles[i][j] = None

                        tweens.append((tile, {"y": tile.i * settings.TILE_SIZE}))
                        space = False
                        i = space_i
                        space_i = -1
                elif tile is None:
                    space = True

                    if space_i == -1:
                        space_i = i

                i -= 1

        # create a replacement tiles at the top of the screen
        for j in range(settings.BOARD_WIDTH):
            for i in range(settings.BOARD_HEIGHT):
                tile = self.tiles[i][j]

                if tile is None:
                    tile = Tile(
                        i,
                        j,
                        settings.VALID_COLORS[random.randint(0, settings.NUM_VALID_COLORS - 1)],
                        0,
                    )
                    tile.y -= settings.TILE_SIZE
                    self.tiles[i][j] = tile
                    tweens.append((tile, {"y": tile.i * settings.TILE_SIZE}))

        return tweens

    def swap_tiles(self, tile1: Tile, tile2: Tile) -> None:
        (
            self.tiles[tile1.i][tile1.j],
            self.tiles[tile2.i][tile2.j],
        ) = (
            self.tiles[tile2.i][tile2.j],
            self.tiles[tile1.i][tile1.j],
        )
        tile1.i, tile1.j, tile2.i, tile2.j = (
            tile2.i,
            tile2.j,
            tile1.i,
            tile1.j,
        )

    def search_match(self):
        for i in range(0, settings.BOARD_HEIGHT):
            for j in range(0, settings.BOARD_WIDTH):
                tile1 = self.tiles[i][j]

                if i < settings.BOARD_HEIGHT - 1:
                    tile2 = self.tiles[i + 1][j]

                    self.swap_tiles(tile1, tile2)

                    has_match = self.calculate_matches_for([tile1, tile2]) is not None
                    self.matches = []

                    self.swap_tiles(tile1, tile2)

                    if has_match:
                        return (tile1, tile2)

                if j < settings.BOARD_WIDTH - 1:
                    tile2 = self.tiles[i][j + 1]

                    self.swap_tiles(tile1, tile2)

                    has_match = self.calculate_matches_for([tile1, tile2]) is not None
                    self.matches = []

                    self.swap_tiles(tile1, tile2)

                    if has_match:
                        return (tile1, tile2)

        return None

    def reset(self) -> None:
        self.matches = []
        self._initialize_tiles()
        settings.SOUNDS["board_reset"].play()
