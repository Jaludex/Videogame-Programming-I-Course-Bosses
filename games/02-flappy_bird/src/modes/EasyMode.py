import pygame
import settings
import random

from src import Bird
from src.modes import GameModeStrat
from src import World
from src.logpairs import LogPair
from gale.factory import Factory
from gale.input_handler import InputData

class EasyMode(GameModeStrat):
    def __init__(self):
        self.log_factory = Factory(LogPair)
        self.logs_spawn_timer: float = 0.0
        self.spawn_log = False
        self.last_log_y: float = -settings.LOG_HEIGHT + random.randint(0, 80) + 20

    def update(self, dt: float, bird: Bird, world: World) -> None:
        self.logs_spawn_timer += dt
        if self.logs_spawn_timer >= settings.TIME_TO_SPAWN_LOGS:
            self.spawn_log = True
            self.logs_spawn_timer = 0

    def render(self, surface: pygame.Surface) -> None:
        pass

    def on_input(self, input_id: str, input_data: InputData, bird: Bird) -> None:
        if input_id == "jump" and input_data.pressed:
            bird.jump()
            
    def should_generate_log(self) -> bool:
        return self.spawn_log

    def new_log(self) -> LogPair:
        y = max(
            -settings.LOG_HEIGHT + 10,
            min(
                self.last_log_y + random.randint(-20, 20),
                settings.VIRTUAL_HEIGHT + 90 - settings.LOG_HEIGHT,
            ),
        )
        self.last_log_y = y
        self.spawn_log = False
        return self.log_factory.create(settings.VIRTUAL_WIDTH, y)

    def can_collide(self, bird: Bird) -> bool:
        return True