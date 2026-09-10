"""
ISPPV1 2023
Study Case: The Legend of the Princess (ARPG)

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the class PlayState for the game.
"""

import pygame

from typing import Any, Dict

from gale.input_handler import InputData
from gale.state import BaseState, StateMachine
from gale.text import render_text

import settings
from src.commands import PAUSE
from gale.command import CommandBindings
from gale.timer import Timer


class PauseState(BaseState):
    def enter(self, **enter_params: Dict[str, Any]) -> None:
        #Bring Att
        self.player = enter_params["player"]
        self.dungeon = enter_params["dungeon"]
        self.pause_requested = False

        Timer.pause()

        self.command_bindings = CommandBindings()
        self.command_bindings.bind("pause", press=PAUSE)
        pygame.mixer.music.pause()
        #Pause Sound

    def exit(self):
        Timer.resume()

    def update(self, dt: float) -> None:
        if self.pause_requested:
            self.pause_requested = False
            self.unpause()
        return

    def render(self, surface: pygame.Surface) -> None:
        self.dungeon.render(surface)

        # Draw player hearts, top of screen.
        health_left = self.player.health
        heart_frame = 1

        for i in range(3):
            if health_left > 1:
                heart_frame = 5
            elif health_left == 1:
                heart_frame = 3
            else:
                heart_frame = 1

            surface.blit(
                settings.TEXTURES["hearts"],
                (i * (settings.TILE_SIZE + 1), 2),
                settings.frame("hearts", heart_frame),
            )

            health_left -= 2

        transparent = pygame.Surface((settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT), pygame.SRCALPHA)

        pygame.draw.rect(
            transparent,
            settings.COLOR_BLACK_TRANSPARENT,
            transparent.get_rect(),
        )
        surface.blit(transparent, (0, 0))

        render_text(
            surface,
            "PAUSE",
            settings.FONTS["princess-small"],
            settings.VIRTUAL_WIDTH / 2,
            settings.VIRTUAL_HEIGHT / 2,
            settings.COLOR_WHITE,
            center=True
        )

    def on_input(self, input_id: str, input_data: InputData) -> None:
        self.command_bindings.dispatch(self, input_id, input_data)

    def unpause(self):
        pygame.mixer.music.unpause()
        self.state_machine.change("play", unpause=True, player=self.player, dungeon=self.dungeon)
        
