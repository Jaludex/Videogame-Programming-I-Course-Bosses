"""
ISPPV1 2023
Study Case: Throw a Bird

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the class VictoryState: a simple "you win" screen
PlayState switches to once every alien has been destroyed (see
Level.all_enemies_defeated). Not a port of anything in the original --
the Defold project has no win/lose condition at all -- added on request.
Clicking restarts a fresh PlayState.
"""

import pygame

from gale.state import BaseState
from gale.text import render_text

import settings

OVERLAY_COLOR = (0, 0, 0, 140)
TITLE_COLOR = (255, 255, 255)
SUBTITLE_COLOR = (230, 230, 230)


class VictoryState(BaseState):
    def enter(self) -> None:
        self.overlay = pygame.Surface(
            (settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT), pygame.SRCALPHA
        )
        self.overlay.fill(OVERLAY_COLOR)

    def on_input(self, input_id: str, input_data) -> None:
        if input_id == "touch" and input_data.pressed:
            self.state_machine.change("play")

    def render(self, surface: pygame.Surface) -> None:
        surface.fill(settings.BG_COLOR)
        surface.blit(self.overlay, (0, 0))

        center_x = settings.VIRTUAL_WIDTH / 2
        center_y = settings.VIRTUAL_HEIGHT / 2

        render_text(
            surface,
            "¡Victoria!",
            settings.FONTS["large"],
            center_x,
            center_y - 20,
            TITLE_COLOR,
            center=True,
        )
        render_text(
            surface,
            "Todos los enemigos han sido derrotados.",
            settings.FONTS["medium"],
            center_x,
            center_y + 30,
            SUBTITLE_COLOR,
            center=True,
        )
        render_text(
            surface,
            "Haz click para jugar de nuevo.",
            settings.FONTS["small"],
            center_x,
            center_y + 60,
            SUBTITLE_COLOR,
            center=True,
        )
