from typing import Dict, Any

import pygame

from gale.camera import Camera
from gale.input_handler import InputData
from gale.state import BaseState
from gale.text import render_text
from gale.timer import Timer

from src.Clock import Clock
from src.GameLevel import GameLevel
from src.Player import Player

import settings

class VictoryState(BaseState):
    def enter(self, **enter_params: Dict[str, Any]):
        self.level = enter_params.get("level")
        self.player = enter_params.get("player")
        self.game_level = enter_params.get("game_level")
        self.tilemap = self.game_level.tilemap
        self.camera = enter_params.get("camera")
        self.clock = enter_params.get("clock")
        self.opacity = 255

        pygame.mixer.music.stop()

        settings.SOUNDS["victory"].play()
        
        def start_fade():
            Timer.tween(3, [
                        (self, {"opacity": 0})
                        ],
                        on_finish=self._on_finish_fade)
            
        Timer.after(2, start_fade)

    def update(self, dt):
        pass

    def render(self, surface: pygame.Surface) -> None:
        temp_surface = pygame.Surface(surface.get_size(), pygame.SRCALPHA).convert_alpha()

        self.game_level.render(temp_surface, self.camera)
        self.player.render(temp_surface, self.camera)

        render_text(
            temp_surface,
            f"Score: {self.player.score}",
            settings.FONTS["small"],
            5,
            5,
            (255, 255, 255),
            shadowed=True,
        )

        render_text(
            temp_surface,
            f"Time: {self.clock.time}",
            settings.FONTS["small"],
            settings.VIRTUAL_WIDTH - 60,
            5,
            (255, 255, 255),
            shadowed=True,
        )

        temp_surface.set_alpha(self.opacity)

        surface.blit(temp_surface, (0, 0))

    def _on_finish_fade(self):
        Timer.clear()
        settings.SOUNDS["victory"].stop()

        if self.level + 1 > settings.NUM_LEVELS:
            self.state_machine.change("start")
        else:
            self.state_machine.change("next_level", level=self.level + 1)

    def on_input(self, input_id, input_data):
        if input_id == "enter" and input_data.pressed:
            self._on_finish_fade()