import pygame

from typing import Optional

from gale.input_handler import InputData
from gale.state import BaseState
from gale.text import render_text

import settings
from src.World import World
from src.Bird import Bird
from src.modes import GameModeStrat


class GameOverState(BaseState):
    def enter(self, world: Optional[World] = None, score: Optional[int] = 0, bird: Optional[Bird] = None, gamemode: GameModeStrat = None) -> None:
        self.world = world if world is not None else World()
        self.score = score
        self.bird = bird
        self.gamemode = gamemode

    def update(self, dt: float) -> None:
        # Bird falling effect
        if self.bird.get_rect().bottom <= settings.VIRTUAL_HEIGHT - 17:
            self.bird.update(dt)

    def render(self, surface: pygame.Surface) -> None:
        self.world.render(surface)
        self.gamemode.render(surface)

        if self.bird is not None:
            self.bird.render(surface)

        render_text(
            surface,
            "YOUR FINAL SCORE",
            settings.FONTS["flappy"],
            settings.VIRTUAL_WIDTH / 2,
            settings.VIRTUAL_HEIGHT / 4,
            settings.COLOR_WHITE,
            center=True,
            shadowed=True,
        )
        render_text(
            surface,
            str(self.score),
            settings.FONTS["huge"],
            settings.VIRTUAL_WIDTH / 2,
            2 * settings.VIRTUAL_HEIGHT / 4,
            settings.COLOR_WHITE,
            center=True,
            shadowed=True,
        )
        render_text(
            surface,
            "Press Enter to restart",
            settings.FONTS["medium"],
            settings.VIRTUAL_WIDTH / 2,
            3 * settings.VIRTUAL_HEIGHT / 4,
            settings.COLOR_WHITE,
            center=True,
            shadowed=True,
            )

    def on_input(self, input_id: str, input_data: InputData) -> None:
        if input_id == "confirm" and input_data.pressed:
            self.state_machine.change("title")
