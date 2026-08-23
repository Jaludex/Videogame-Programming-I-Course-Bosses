import pygame

from src import World
from src import Bird
from gale.input_handler import InputData

class GameModeStrat():
    def __init__():
        pass

    def update(self, dt: float) -> None:
        raise NotImplementedError

    def render(self, surface: pygame.Surface) -> None:
        raise NotImplementedError

    def on_input(self, input_id: str, input_data: InputData) -> None:
        raise NotImplementedError

    def should_generate_log(self) -> bool:
        raise NotImplementedError

    def new_log(self):
        raise NotImplementedError

    def can_collide(self, bird: Bird) -> bool:
        raise NotImplementedError

    