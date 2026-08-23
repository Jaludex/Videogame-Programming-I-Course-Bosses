import pygame
import settings
import random

from typing import List

from src import Bird
from src.modes import GameModeStrat
from src import World
from src.logpairs import LogPair

from src.powerups import PowerUp

from gale.factory import AbstractFactory
from gale.input_handler import InputData

class HardMode(GameModeStrat):
    def __init__(self):
        self.log_factory = AbstractFactory("src.logpairs")
        self.powerup_factory = AbstractFactory("src.powerups")
        self.logs_spawn_timer: float = 0.0
        self.time_for_next_log: float = settings.TIME_TO_SPAWN_LOGS
        self.spawn_log = False
        self.last_log_y: float = -settings.LOG_HEIGHT + random.randint(0, 80) + 20
        self.invincible_timer = 0
        self.powerups: List[PowerUp] = []
        self.time_for_next_powerup = settings.TIME_TO_SPAWN_POWERUP

    def update(self, dt: float, bird: Bird, world: World) -> None:
        self.logs_spawn_timer -= dt
        if self.logs_spawn_timer <= 0:
            self.spawn_log = True
            self.logs_spawn_timer = settings.TIME_TO_SPAWN_LOGS * random.uniform(0.9, 1.4)

        self.time_for_next_powerup -= dt
        if self.time_for_next_powerup <= 0:
            self.time_for_next_powerup = settings.TIME_TO_SPAWN_POWERUP + random.randint(-2, 10)
            if random.random() <= 0.9:
                pw_y = random.randint(20, settings.VIRTUAL_HEIGHT - 20)

                new_pw = self.powerup_factory.get_factory("GhostPill").create(settings.VIRTUAL_WIDTH, pw_y)
                if not world.collides_with_log(new_pw.get_collision_rect()):
                    self.powerups.append(new_pw)


        for pu in self.powerups:
            pu.update(dt)
            if pu.collides(bird):
                pu.take(self)

        self.powerups = [p for p in self.powerups if p.active]

        if self.invincible_timer > 0:
            bird.invincible = True
            self.invincible_timer -= dt

            if self.invincible_timer <= 0:
                self.invincible_timer = 0
                bird.invincible = False
                pygame.mixer.music.stop()
                pygame.mixer.music.load(settings.MUSICS["main"])
                pygame.mixer.music.play()
        

    def render(self, surface: pygame.Surface) -> None:
        for pu in self.powerups:
            pu.render(surface)

        if self.invincible_timer > 0:
            bar_width: int = settings.POWERUP_BAR_WIDTH * (1 - ((settings.POWERUP_DURATION - self.invincible_timer) / settings.POWERUP_DURATION))
            bar_rect = pygame.Surface((bar_width, int(settings.POWERUP_BAR_HEIGHT)))
            bar_rect.fill(settings.COLOR_GREEN)
            surface.blit(bar_rect, (20, 40))

    def on_input(self, input_id: str, input_data: InputData, bird: Bird) -> None:
        if input_id == "jump" and input_data.pressed:
            bird.jump()
        elif input_id == "move_left":
            if input_data.pressed:
                bird.vx = -settings.BIRD_X_MOVEMENT_SPEED
            elif input_data.released and bird.vx < 0:
                bird.vx = 0
        elif input_id == "move_right":
            if input_data.pressed:
                bird.vx = settings.BIRD_X_MOVEMENT_SPEED
            elif input_data.released and bird.vx > 0:
                bird.vx = 0
            
    def should_generate_log(self) -> bool:
        return self.spawn_log

    def new_log(self) -> LogPair:
        y = max(
            -settings.LOG_HEIGHT + 10,
            min(
                self.last_log_y + random.randint(-100, 100),
                settings.VIRTUAL_HEIGHT - settings.LOGS_GAP - settings.LOG_HEIGHT,
            ),
        )
        self.last_log_y = y
        self.spawn_log = False

        next_log = "LogPair"
        if random.random() < 0.2:
            next_log = "MovingLogPair"
        return self.log_factory.get_factory(next_log).create(settings.VIRTUAL_WIDTH, y)

    def can_collide(self, bird: Bird) -> bool:
        return not bird.invincible