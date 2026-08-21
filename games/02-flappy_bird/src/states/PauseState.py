import pygame

from typing import Optional

from gale.input_handler import InputData
from gale.state import BaseState
from gale.text import render_text

import settings
from src.World import World
from src.Bird import Bird


class PauseState(BaseState):
    def enter(self, world: Optional[World] = None, score: Optional[int] = 0, bird: Optional[Bird] = None) -> None:
        self.world = world if world is not None else World()
        self.score = score
        self.bird = bird
        pygame.mixer.music.pause()
        settings.SOUNDS["pause"].stop()
        settings.SOUNDS["pause"].play()

    def update(self, dt: float) -> None:
        pass

    def render(self, surface: pygame.Surface) -> None:
        self.world.render(surface)
        if self.bird is not None:
            self.bird.render(surface)

        render_text(
            surface,
            "PAUSE",
            settings.FONTS["flappy"],
            settings.VIRTUAL_WIDTH / 2,
            settings.VIRTUAL_HEIGHT / 2,
            settings.COLOR_WHITE,
            center=True,
            shadowed=True,
        )

        render_text(
            surface,
            f"Score: {self.score}",
            settings.FONTS["flappy"],
            20,
            10,
            settings.COLOR_WHITE,
            shadowed=True,
        )

    def exit(self):
        settings.SOUNDS["pause"].stop()
        settings.SOUNDS["pause"].play()
        pygame.mixer.music.unpause()

    def on_input(self, input_id: str, input_data: InputData) -> None:
        if input_id == "pause" and input_data.pressed:
            self.state_machine.change("playing", world=self.world, score=self.score, bird=self.bird)
