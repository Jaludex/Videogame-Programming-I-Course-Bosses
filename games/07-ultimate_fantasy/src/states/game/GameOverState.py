"""
ISPPV1 2023
Study Case: Ultimate Fantasy (RPG)

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the class GameOverState: shown on a full party wipe.
Enter/Return stops every sound, clears the whole state stack, and
restarts at StartState.
"""

from typing import Any

import pygame

from gale.state import BaseState

import settings


class GameOverState(BaseState):
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
        text = medium.render("Your party was defeated!", True, (255, 255, 255))
        surface.blit(text, (0, 10))

        large = settings.FONTS["large"]
        title = large.render("Game Over", True, (255, 255, 255))
        rect = title.get_rect(
            center=(settings.VIRTUAL_WIDTH / 2, settings.VIRTUAL_HEIGHT / 2 - 32)
        )
        surface.blit(title, rect)
