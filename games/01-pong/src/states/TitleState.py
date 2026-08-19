"""
ISPPV1 2023
Study Case: Pong

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the class TitleState.
"""

import random

import pygame

from gale.input_handler import InputData
from gale.state import BaseState
from gale.text import render_text

import settings
from src.rendering import render_table


class TitleState(BaseState):
    def enter(self, pong) -> None:
        self.pong = pong

    def render(self, surface: pygame.Surface) -> None:
        render_table(surface, self.pong)
        render_text(
            surface,
            "Select an option:",
            settings.FONTS["large"],
            settings.VIRTUAL_WIDTH / 2,
            settings.VIRTUAL_HEIGHT / 2,
            settings.COLOR_WHITE,
            center=True,
        )

        render_text(
            surface,
            "1- Play against a friend 2- Play against a bot.",
            settings.FONTS["large"],
            settings.VIRTUAL_WIDTH / 2,
            settings.VIRTUAL_HEIGHT / 2 + 30,
            settings.COLOR_WHITE,
            center=True,
                        )

    def on_input(self, input_id: str, input_data: InputData) -> None:
        if input_id in ("select_1", "select_2") and input_data.pressed:
            self.pong.serving_player = random.randint(1, 2)

            if input_id == "select_1":
                self.state_machine.change("serve", pong=self.pong, against_bot=False)
            else:
                self.state_machine.change("serve", pong=self.pong, against_bot=True)
