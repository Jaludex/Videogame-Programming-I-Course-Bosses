from typing import Dict, Any

import pygame

from gale.input_handler import InputData
from gale.state import BaseState
from gale.text import render_text
from gale.timer import Timer

from src.GameLevel import GameLevel
from src.Player import Player

import settings

class NextLevelState(BaseState):
    def enter(self, **enter_params: Dict[str, Any]):
        self.level = max(1, min(enter_params.get("level"), settings.NUM_LEVELS))
        self.level_score = 100 + (self.level * 100)
        pygame.mixer.music.stop()

        Timer.clear()
        
        Timer.after(3, self._finish)

    def update(self, dt):
        pass

    def render(self, surface: pygame.Surface) -> None:
        render_text(
            surface,
            f"Level {str(self.level)}",
            settings.FONTS["small"],
            settings.VIRTUAL_WIDTH // 2,
            settings.VIRTUAL_HEIGHT // 2,
            (255, 255, 255),
            center=True,
            shadowed=True,
        )

        render_text(
            surface,
            f"Go for {str(self.level_score)} points!",
            settings.FONTS["small"],
            settings.VIRTUAL_WIDTH // 2,
            settings.VIRTUAL_HEIGHT - 32,
            (255, 255, 255),
            center=True,
            shadowed=True,
        )

    def _finish(self):
        Timer.clear()
        self.state_machine.change("play", level=self.level)

    def on_input(self, input_id, input_data):
        pass