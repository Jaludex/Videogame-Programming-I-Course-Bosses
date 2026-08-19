"""
ISPPV1 2023
Study Case: Hello World

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the class that runs the whole game, showing the
most basic use of Gale: opening a window and drawing text on it.
"""

import pygame

from gale.game import Game
from gale.input_handler import InputData
from gale.text import render_text

import settings


class HelloWorld(Game):
    def init(self) -> None:
        pass

    def update(self, dt: float) -> None:
        pass

    def render(self, surface: pygame.Surface) -> None:
        surface.fill((0, 0, 0))
        render_text(
            surface,
            "Hello world!",
            settings.FONTS["default"],
            settings.VIRTUAL_WIDTH / 2,
            settings.VIRTUAL_HEIGHT / 2,
            (255, 255, 255),
            center=True,
        )

    def on_input(self, input_id: str, input_data: InputData) -> None:
        if input_id == "quit" and input_data.pressed:
            self.quit()
