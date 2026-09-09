"""
ISPPV1 2023
Study Case: Ultimate Fantasy (RPG)

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the class TheEndState: shown after the final boss is
defeated. Same restart pattern as GameOverState.
"""

from typing import Any

import pygame

from gale.state import BaseState

import settings


class TheEndState(BaseState):
    def on_input(self, input_id: str, input_data: Any) -> None:
        if input_id == "enter" and input_data.pressed:
            for sound in settings.SOUNDS.values():
                sound.stop()

            self.state_machine.clear()

            from src.states.game.StartState import StartState

            self.state_machine.push(StartState(self.state_machine))

    def render(self, surface: pygame.Surface) -> None:
        surface.fill((0, 0, 0))

        medium = settings.FONTS["medium"]
        text = medium.render(
            "The man-eater flower has been defeated and the curse has been "
            "broken. Thanks!",
            True,
            (255, 255, 255),
        )
        surface.blit(text, (0, 10))

        large = settings.FONTS["large"]
        title = large.render("The end", True, (255, 255, 255))
        rect = title.get_rect(
            center=(settings.VIRTUAL_WIDTH / 2, settings.VIRTUAL_HEIGHT / 2 - 32)
        )
        surface.blit(title, rect)
