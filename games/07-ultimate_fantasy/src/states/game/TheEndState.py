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
from src.text_utils import wrap_text


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
        message = (
            "The man-eater flower has been defeated and the curse has been "
            "broken. Thanks!"
        )
        # 12px of margin on each side -- rendering right up to the two
        # screen edges reads as cramped once the text is wide enough to
        # need wrapping at all.
        max_width = settings.VIRTUAL_WIDTH - 24
        y = 10

        for line in wrap_text(medium, message, max_width):
            text = medium.render(line, True, (255, 255, 255))
            rect = text.get_rect(center=(settings.VIRTUAL_WIDTH / 2, y + text.get_height() / 2))
            surface.blit(text, rect)
            y += text.get_height()

        large = settings.FONTS["large"]
        title = large.render("The end", True, (255, 255, 255))
        rect = title.get_rect(
            center=(settings.VIRTUAL_WIDTH / 2, settings.VIRTUAL_HEIGHT / 2 - 32)
        )
        surface.blit(title, rect)
