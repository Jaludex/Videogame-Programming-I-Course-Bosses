"""
ISPPV1 2023
Study Case: Breakout

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the class to define the Play state.
"""

import random
from typing import List

import pygame

from gale.factory import Factory
from gale.factory import AbstractFactory
from gale.state import BaseState
from gale.input_handler import InputData
from gale.text import render_text

import settings
import src.powerups
from src.Rocket import Rocket


class PlayState(BaseState):
    def enter(self, **params: dict):
        self.level = params["level"]
        self.score = params["score"]
        self.lives = params["lives"]
        self.paddle = params["paddle"]
        self.balls = params["balls"]
        self.brickset = params["brickset"]
        self.live_factor = params["live_factor"]
        self.points_to_next_live = params["points_to_next_live"]
        self.points_to_next_grow_up = (
            self.score
            + settings.PADDLE_GROW_UP_POINTS * (self.paddle.size + 1) * self.level
        )
        self.powerups = params.get("powerups", [])

        if not params.get("resume", False):
            self.balls[0].vx = random.randint(-80, 80)
            self.balls[0].vy = random.randint(-170, -100)
            settings.SOUNDS["paddle_hit"].play()

        self.powerups_abstract_factory = AbstractFactory("src.powerups")

        self.sticky_paddle_timer: float = params.get("sticky_paddle_timer", 0)
        self.bazooka_timer: float  = params.get("bazooka_timer", 0)
        self.rockets: List[Rocket] = params.get("rockets", [])
        self.rocket_factory = Factory(Rocket)

    def update(self, dt: float) -> None:
        self.paddle.update(dt)

        if self.bazooka_timer > 0:
            self.bazooka_timer -= dt
        
        if self.sticky_paddle_timer > 0:
            self.sticky_paddle_timer -= dt

        for ball in self.balls:
            if self.sticky_paddle_timer <= 0 and ball.sticked:
                self.push_sticked_ball(ball)

            if ball.sticked == True:
                ball.vx = self.paddle.vx
            
            ball.update(dt)
            ball.solve_world_boundaries()

            # Check collision with the paddle
            if ball.collides(self.paddle):
                settings.SOUNDS["paddle_hit"].stop()
                settings.SOUNDS["paddle_hit"].play()
                if self.sticky_paddle_timer > 0:
                    ball.sticked = True
                    ball.y = self.paddle.y - ball.height
                    ball.vy = 0
                else:
                    ball.rebound(self.paddle)
                    ball.push(self.paddle)
                continue

            # Check collision with brickset
            if not ball.collides(self.brickset):
                continue

            brick = self.brickset.get_colliding_brick(ball.get_collision_rect())

            if brick is None:
                continue

            ball.rebound(brick)
            self.break_brick(brick)

        # Removing all balls that are not in play
        self.balls = [ball for ball in self.balls if ball.active]

        for rocket in self.rockets:
            rocket.update(dt)

            if not rocket.collides(self.brickset):
                continue

            brick = self.brickset.get_colliding_brick(rocket.get_collision_rect())

            if brick is None:
                continue

            explosion_rect = rocket.get_explosion_rect()

            for b in self.brickset.get_colliding_bricks_in_rect(explosion_rect):
                self.break_brick(b)

            rocket.explodes()

        self.rockets = [r for r in self.rockets if r.active]

        self.brickset.update(dt)

        if not self.balls:
            self.lives -= 1
            if self.lives == 0:
                self.state_machine.change("game_over", score=self.score)
            else:
                self.paddle.dec_size()
                self.state_machine.change(
                    "serve",
                    level=self.level,
                    score=self.score,
                    lives=self.lives,
                    paddle=self.paddle,
                    brickset=self.brickset,
                    points_to_next_live=self.points_to_next_live,
                    live_factor=self.live_factor,
                )

        # Update powerups
        for powerup in self.powerups:
            powerup.update(dt)

            if powerup.collides(self.paddle):
                powerup.take(self)

        # Remove powerups that are not in play
        self.powerups = [p for p in self.powerups if p.active]

        # Check victory
        if self.brickset.size == 1 and next(
            (True for _, b in self.brickset.bricks.items() if b.broken), False) or self.brickset.size == 0:
            self.state_machine.change(
                "victory",
                lives=self.lives,
                level=self.level,
                score=self.score,
                paddle=self.paddle,
                balls=self.balls,
                points_to_next_live=self.points_to_next_live,
                live_factor=self.live_factor,
            )

    def render(self, surface: pygame.Surface) -> None:
        heart_x = settings.VIRTUAL_WIDTH - 120

        i = 0
        # Draw filled hearts
        while i < self.lives:
            surface.blit(
                settings.TEXTURES["hearts"], (heart_x, 5), settings.FRAMES["hearts"][0]
            )
            heart_x += 11
            i += 1

        # Draw empty hearts
        while i < 3:
            surface.blit(
                settings.TEXTURES["hearts"], (heart_x, 5), settings.FRAMES["hearts"][1]
            )
            heart_x += 11
            i += 1

        render_text(
            surface,
            f"Score: {self.score}",
            settings.FONTS["tiny"],
            settings.VIRTUAL_WIDTH - 80,
            5,
            (255, 255, 255),
        )

        self.brickset.render(surface)

        self.paddle.render(surface)

        for rocket in self.rockets:
            rocket.render(surface)

        if self.bazooka_timer > 0:
            surface.blit(settings.TEXTURES["spritesheet"], (5, 2), settings.FRAMES["powerups"][4])
            surface.blit(settings.TEXTURES["spritesheet"], (self.paddle.x - 15, self.paddle.y - 8), settings.FRAMES["bazooka"])
            surface.blit(settings.TEXTURES["spritesheet"], (self.paddle.x - 1 + self.paddle.width, self.paddle.y - 8), settings.FRAMES["bazooka"])

            bar_width: int = settings.POWERUP_BAR_WIDTH * (1 - ((settings.BAZOOKA_TIME - self.bazooka_timer) / settings.BAZOOKA_TIME))
            bar_rect = pygame.Surface((bar_width, int(settings.POWERUP_BAR_HEIGHT)))
            bar_rect.fill(settings.COLOR_BLUE)
            surface.blit(bar_rect, (26, 5))

        if self.sticky_paddle_timer > 0:
            sticky_icon_x = 31 + settings.POWERUP_BAR_WIDTH
            surface.blit(settings.TEXTURES["spritesheet"], (sticky_icon_x, 2), settings.FRAMES["powerups"][5])

            sticky_bar_x = 52 + settings.POWERUP_BAR_WIDTH
            bar_width: int = settings.POWERUP_BAR_WIDTH * (1 - ((settings.STICLY_PADDLE_TIME - self.sticky_paddle_timer) / settings.STICLY_PADDLE_TIME))
            bar_rect = pygame.Surface((bar_width, int(settings.POWERUP_BAR_HEIGHT)))
            bar_rect.fill(settings.COLOR_GREEN)
            surface.blit(bar_rect, (sticky_bar_x, 5))

        for ball in self.balls:
            ball.render(surface)

        for powerup in self.powerups:
            powerup.render(surface)

    def on_input(self, input_id: str, input_data: InputData) -> None:
        if input_id == "move_left":
            if input_data.pressed:
                self.paddle.vx = -settings.PADDLE_SPEED
            elif input_data.released and self.paddle.vx < 0:
                self.paddle.vx = 0
        elif input_id == "move_right":
            if input_data.pressed:
                self.paddle.vx = settings.PADDLE_SPEED
            elif input_data.released and self.paddle.vx > 0:
                self.paddle.vx = 0
        elif input_id == "pause" and input_data.pressed:
            self.state_machine.change(
                "pause",
                level=self.level,
                score=self.score,
                lives=self.lives,
                paddle=self.paddle,
                balls=self.balls,
                brickset=self.brickset,
                points_to_next_live=self.points_to_next_live,
                live_factor=self.live_factor,
                powerups=self.powerups,
                bazooka_timer = self.bazooka_timer,
                sticky_paddle_timer = self.sticky_paddle_timer,
                rockets = self.rockets
            )
        elif input_id == "enter" and input_data.pressed:
            if self.sticky_paddle_timer > 0:
                for ball in self.balls:
                    if ball.sticked:
                        self.push_sticked_ball(ball)
        elif input_id == "fire_bazooka" and input_data.pressed:
            if self.bazooka_timer > 0 and len(self.rockets) == 0:
                self.rockets.append(self.rocket_factory.create(self.paddle.x - 12, self.paddle.y - 8))
                self.rockets.append(self.rocket_factory.create(self.paddle.x + 5 + self.paddle.width, self.paddle.y - 8))
                settings.SOUNDS["fire_bazooka"].play()


    def roll_for_powerup(self, brick):
        rolled_number = random.random()
        key_to_append: str = "none"
        if rolled_number <= 0.15:
            rolled_number = random.randint(0, 3)
            if rolled_number <= 1:
                key_to_append = "TwoMoreBall"
            elif rolled_number == 2:
                key_to_append = "StickyPaddle"
            else:
                key_to_append = "Bazooka"
        if key_to_append != "none":
            r = brick.get_collision_rect()
            self.powerups.append(
                self.powerups_abstract_factory.get_factory(key_to_append).create(
                    r.centerx, r.centery
                )
            )

    def push_sticked_ball(self, ball):
        ball.y -= 1
        ball.vy = random.randint(-170, -100)
        if ball.vx == 0:
            ball.vx = random.randint(-80, 80)
        ball.sticked = False

    def break_brick(self, brick):
        brick.hit()
        self.score += brick.score()
        # Check earn life
        if self.score >= self.points_to_next_live:
            settings.SOUNDS["life"].play()
            self.lives = min(3, self.lives + 1)
            self.live_factor += 0.5
            self.points_to_next_live += settings.LIVE_POINTS_BASE * self.live_factor
        # Check growing up of the paddle
        if self.score >= self.points_to_next_grow_up:
            settings.SOUNDS["grow_up"].play()
            self.points_to_next_grow_up += (
                settings.PADDLE_GROW_UP_POINTS * (self.paddle.size + 1) * self.level
            )
            self.paddle.inc_size()

        self.roll_for_powerup(brick)