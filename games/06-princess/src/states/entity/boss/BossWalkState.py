import random
from typing import TypeVar

import pygame
from gale.timer import Timer

import settings
from src import commands
from src.states.entity.BaseEntityState import BaseEntityState
from src.states.entity.movement import move_and_bump

_DIRECTIONS = ["left", "right", "up", "down"]

_MOVE_COMMANDS = {
    "left": commands.MOVE_LEFT,
    "right": commands.MOVE_RIGHT,
    "up": commands.MOVE_UP,
    "down": commands.MOVE_DOWN,
}
_STOP_COMMANDS = (
    commands.STOP_MOVE_LEFT,
    commands.STOP_MOVE_RIGHT,
    commands.STOP_MOVE_UP,
    commands.STOP_MOVE_DOWN,
)

_HEAD_OFFSETS = {
    "left": (-8, 0),
    "right": (8, 0),
    "up": (0, -8),
    "down": (0, 8),
}


class BossWalkState(BaseEntityState):
    def enter(self) -> None:
        self.entity.change_animation("walking")

        self.is_moving = False
        self.bumped = False
        self.movement_timer = 0.0
        self.move_duration = 0.0

        self.head_rel_x = self.entity.head_x - self.entity.x
        self.head_rel_y = self.entity.head_y - self.entity.y

        self._pick_direction_and_prepare()

    def update(self, dt: float) -> None:
        entity = self.entity

        if self.is_moving:
            held = entity.held

            if held["move_left"]:
                entity.direction = "left"
            elif held["move_right"]:
                entity.direction = "right"
            elif held["move_up"]:
                entity.direction = "up"
            elif held["move_down"]:
                entity.direction = "down"

            self.bumped = move_and_bump(entity, dt)

            min_x = settings.MAP_RENDER_OFFSET_X + settings.TILE_SIZE * 2
            max_x = (
                settings.MAP_RENDER_OFFSET_X
                + settings.MAP_WIDTH * settings.TILE_SIZE
                - settings.TILE_SIZE * 2
                - entity.width
            )
            min_y = settings.MAP_RENDER_OFFSET_Y + settings.TILE_SIZE * 2
            max_y = (
                settings.MAP_RENDER_OFFSET_Y
                + settings.MAP_HEIGHT * settings.TILE_SIZE
                - settings.TILE_SIZE * 2
                - entity.height
            )

            if entity.x < min_x:
                entity.x = min_x
                self.bumped = True
            elif entity.x > max_x:
                entity.x = max_x
                self.bumped = True

            if entity.y < min_y:
                entity.y = min_y
                self.bumped = True
            elif entity.y > max_y:
                entity.y = max_y
                self.bumped = True

        entity.head_x = entity.x + self.head_rel_x
        entity.head_y = entity.y + self.head_rel_y

    def _pick_direction_and_prepare(self) -> None:
        for stop in _STOP_COMMANDS:
            stop.execute(self.entity)

        min_x = settings.MAP_RENDER_OFFSET_X + settings.TILE_SIZE * 2
        max_x = (
            settings.MAP_RENDER_OFFSET_X
            + settings.MAP_WIDTH * settings.TILE_SIZE
            - settings.TILE_SIZE * 2
            - self.entity.width
        )
        min_y = settings.MAP_RENDER_OFFSET_Y + settings.TILE_SIZE * 2
        max_y = (
            settings.MAP_RENDER_OFFSET_Y
            + settings.MAP_HEIGHT * settings.TILE_SIZE
            - settings.TILE_SIZE * 2
            - self.entity.height
        )

        valid_directions = []
        if self.entity.x > min_x:
            valid_directions.append("left")
        if self.entity.x < max_x:
            valid_directions.append("right")
        if self.entity.y > min_y:
            valid_directions.append("up")
        if self.entity.y < max_y:
            valid_directions.append("down")

        if not valid_directions:
            valid_directions = _DIRECTIONS

        direction = random.choice(valid_directions)
        self.entity.direction = direction

        distance = random.randint(3, 5) * settings.TILE_SIZE
        self.move_duration = distance / self.entity.walk_speed

        base_rel_x = (self.entity.width - self.entity.head_width) / 2
        base_rel_y = (self.entity.height - self.entity.head_height) / 2

        offset_x, offset_y = _HEAD_OFFSETS[direction]
        target_rel_x = base_rel_x + offset_x
        target_rel_y = base_rel_y + offset_y

        Timer.tween(
            1.0,
            [
                (
                    self,
                    {
                        "head_rel_x": target_rel_x,
                        "head_rel_y": target_rel_y,
                    },
                )
            ],
        )

        def start_moving() -> None:
            if self.state_machine.current is self:
                self.bumped = False 
                self.movement_timer = 0.0
                _MOVE_COMMANDS[direction].execute(self.entity)
                self.is_moving = True

        Timer.after(1.0, start_moving)

    def process_ai(self, room: TypeVar("Room"), dt: float) -> None:
        self.entity.process_fire(dt)

        if self.entity.fire_requested:
            self.entity.fire_requested = False
            self.entity.firing = True

            def stop_firing_head():
                self.entity.firing = False

            Timer.after(1, stop_firing_head)
            self.entity.fire(room)

        if self.is_moving:
            self.movement_timer += dt

            if self.bumped or self.movement_timer >= self.move_duration:
                self.entity.change_state("idle")

    def exit(self) -> None:
        for stop in _STOP_COMMANDS:
            stop.execute(self.entity)

    def render(self, surface: pygame.Surface) -> None:
        anim = self.entity.current_animation
        if anim:
            self.entity.render_sprite(
                surface, anim.texture_id, anim.get_current_frame()
            )