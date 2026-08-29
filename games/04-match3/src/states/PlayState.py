"""
ISPPV1 2023
Study Case: Match-3

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the class PlayState.
"""

from typing import Dict, Any, List

import pygame

from gale.input_handler import InputData
from gale.state import BaseState
from gale.text import render_text
from gale.timer import Timer

import settings


class PlayState(BaseState):
    def enter(self, **enter_params: Dict[str, Any]) -> None:
        self.level = enter_params["level"]
        self.board = enter_params["board"]
        self.score = enter_params["score"]

        # Position in the grid which we are highlighting
        self.board_highlight_i1 = -1
        self.board_highlight_j1 = -1
        self.board_highlight_i2 = -1
        self.board_highlight_j2 = -1

        self.highlighted_tile = False

        self.active = True

        self.hightlight_hint = False
        self.hint_timer = None

        self.timer_color = settings.COLOR_BLUE

        self.check_board()

        self.timer = settings.LEVEL_TIME

        self.goal_score = self.level * 2.5 * 1000

        # A surface that supports alpha to highlight a selected tile
        self.tile_alpha_surface = pygame.Surface(
            (settings.TILE_SIZE, settings.TILE_SIZE), pygame.SRCALPHA
        )
        pygame.draw.rect(
            self.tile_alpha_surface,
            (255, 255, 255, 96),
            pygame.Rect(0, 0, settings.TILE_SIZE, settings.TILE_SIZE),
            border_radius=7,
        )

        # A surface that supports alpha to draw behind the text.
        self.text_alpha_surface = pygame.Surface((212, 136), pygame.SRCALPHA)
        pygame.draw.rect(
            self.text_alpha_surface, (56, 56, 56, 234), pygame.Rect(0, 0, 212, 136)
        )

        def decrement_timer():
            self.timer -= 1

            # Play warning sound on timer if we get low
            if self.timer <= 10:
                settings.SOUNDS["clock"].play()

        Timer.every(1, decrement_timer)

    def update(self, _: float) -> None:
        if self.timer <= 0:
            Timer.clear()
            settings.SOUNDS["game-over"].play()
            self.state_machine.change("game-over", score=self.score)

        if self.score >= self.goal_score:
            Timer.clear()
            settings.SOUNDS["next-level"].play()
            self.state_machine.change("begin", level=self.level + 1, score=self.score)

        if self.highlighted_tile:
            mouse_pos_x, mouse_pos_y = pygame.mouse.get_pos()
            mouse_pos_x = mouse_pos_x * settings.VIRTUAL_WIDTH // settings.WINDOW_WIDTH
            mouse_pos_y = mouse_pos_y * settings.VIRTUAL_HEIGHT // settings.WINDOW_HEIGHT
            self.board.tiles[self.highlighted_i1][self.highlighted_j1].x = mouse_pos_x - self.board.x - (settings.TILE_SIZE // 2)
            self.board.tiles[self.highlighted_i1][self.highlighted_j1].y = mouse_pos_y - self.board.y - (settings.TILE_SIZE // 2)

        if self.timer < 10:
            self.timer_color = settings.COLOR_RED
        elif self.timer < 30:
            self.timer_color = settings.COLOR_WARNING

    def render(self, surface: pygame.Surface) -> None:
        self.board.render(surface)

        if self.highlighted_tile:
            # x = self.highlighted_j1 * settings.TILE_SIZE + self.board.x
            # y = self.highlighted_i1 * settings.TILE_SIZE + self.board.y
            # surface.blit(self.tile_alpha_surface, (x, y))
            self.board.tiles[self.highlighted_i1][self.highlighted_j1].render(surface, self.board.x, self.board.y)

        if self.hightlight_hint and self.possible_next_match is not None:
            hint_tile1, hint_tile2 = self.possible_next_match
            hint_x1 = hint_tile1.j * settings.TILE_SIZE + self.board.x
            hint_y1 = hint_tile1.i * settings.TILE_SIZE + self.board.y
            hint_x2 = hint_tile2.j * settings.TILE_SIZE + self.board.x
            hint_y2 = hint_tile2.i * settings.TILE_SIZE + self.board.y

            surface.blit(self.tile_alpha_surface, (hint_x1, hint_y1))
            surface.blit(self.tile_alpha_surface, (hint_x2, hint_y2))

        surface.blit(self.text_alpha_surface, (16, 16))
        render_text(
            surface,
            f"Level: {self.level}",
            settings.FONTS["medium"],
            30,
            24,
            (99, 155, 255),
            shadowed=True,
        )
        render_text(
            surface,
            f"Score: {self.score}",
            settings.FONTS["medium"],
            30,
            52,
            (99, 155, 255),
            shadowed=True,
        )
        render_text(
            surface,
            f"Goal: {self.goal_score}",
            settings.FONTS["medium"],
            30,
            80,
            (99, 155, 255),
            shadowed=True,
        )
        render_text(
            surface,
            f"Timer: {self.timer}",
            settings.FONTS["medium"],
            30,
            108,
            self.timer_color,
            shadowed=True,
        )

    def on_input(self, input_id: str, input_data: InputData) -> None:
        if not self.active:
            return

        if input_id == "click":
            pos_x, pos_y = input_data.position
            pos_x = pos_x * settings.VIRTUAL_WIDTH // settings.WINDOW_WIDTH
            pos_y = pos_y * settings.VIRTUAL_HEIGHT // settings.WINDOW_HEIGHT
            i = (pos_y - self.board.y) // settings.TILE_SIZE
            j = (pos_x - self.board.x) // settings.TILE_SIZE

            if 0 <= i < settings.BOARD_HEIGHT and 0 <= j <= settings.BOARD_WIDTH:
                if input_data.pressed and not self.highlighted_tile:
                    self.highlighted_tile = True
                    self.highlighted_i1 = i
                    self.highlighted_j1 = j
                elif input_data.released and self.highlighted_tile:
                    self.highlighted_tile = False
                    self.highlighted_i2 = i
                    self.highlighted_j2 = j
                    di = abs(self.highlighted_i2 - self.highlighted_i1)
                    dj = abs(self.highlighted_j2 - self.highlighted_j1)

                    self.active = False
                    if di <= 1 and dj <= 1 and di != dj:
                        tile1 = self.board.tiles[self.highlighted_i1][
                            self.highlighted_j1
                        ]
                        tile2 = self.board.tiles[self.highlighted_i2][
                            self.highlighted_j2
                        ]

                        def arrive():
                            tile1 = self.board.tiles[self.highlighted_i1][
                                self.highlighted_j1
                            ]
                            tile2 = self.board.tiles[self.highlighted_i2][
                                self.highlighted_j2
                            ]
                            self.board.swap_tiles(tile1, tile2)
                            valid_match: bool = self._calculate_matches([tile1, tile2])

                            if valid_match:
                                self.hightlight_hint = False
                            else:
                                settings.SOUNDS["wrong_move"].stop()
                                settings.SOUNDS["wrong_move"].play()
                                def set_back():
                                    self.board.swap_tiles(tile1, tile2)

                                    self.active = True

                                Timer.tween(
                                    0.25,
                                    [
                                        (tile1, {"x": tile2.x, "y": tile2.y}),
                                        (tile2, {"x": tile1.x, "y": tile1.y}),
                                    ],
                                    on_finish=set_back,
                                )
                            
                        destination_x1, destination_y1 = tile1.get_board_coords()
                        destination_x2, destination_y2 = tile2.get_board_coords()
                        # Swap tiles
                        Timer.tween(
                            0.25,
                            [
                                (tile1, {"x": destination_x2, "y": destination_y2}),
                                (tile2, {"x": destination_x1, "y": destination_y1}),
                            ],
                            on_finish=arrive,
                        )
                    else:
                        return_tile = self.board.tiles[self.highlighted_i1][self.highlighted_j1]
                        return_tile_x, return_tile_y = return_tile.get_board_coords()

                        Timer.tween(
                            0.25,
                            [(return_tile, {"x": return_tile_x, "y":return_tile_y})],
                            on_finish=lambda: setattr(self, "active", True)
                        )

            elif input_data.released and self.highlighted_tile:
                return_tile = self.board.tiles[self.highlighted_i1][self.highlighted_j1]
                return_tile.reset_board_coords()
                self.highlighted_tile = False

    def _calculate_matches(self, tiles: List) -> bool:
        matches = self.board.calculate_matches_for(tiles)

        if matches is None or len(matches) == 0:
            return False

        for match in matches:
            for tile in match:
                tile.play(self.board.tiles, match)

        settings.SOUNDS["match"].stop()
        settings.SOUNDS["match"].play()

        for match in matches:
            self.score += len(match) * 50

        self.board.remove_matches()

        falling_tiles = self.board.get_falling_tiles()

        def on_falling_complete():
            has_more_matches = self._calculate_matches([item[0] for item in falling_tiles])

            if not has_more_matches:
                self.check_board()
                self.active = True

        if falling_tiles:
            Timer.tween(
                0.25,
                falling_tiles,
                on_finish=on_falling_complete
            )
        else:
            self.check_board()
            self.active = True

        return True

    def check_board(self) -> None:
        if self.hint_timer is not None:
            self.hint_timer.remove()

        self.possible_next_match = self.board.search_match()

        while self.possible_next_match is None:
            self.board.reset()
            self.possible_next_match = self.board.search_match()

        def set_hightlight():
            self.hightlight_hint = True
        
        self.hint_timer = Timer.after(
            settings.BEFORE_HINT_TIME,
            set_hightlight
        )

        return

        