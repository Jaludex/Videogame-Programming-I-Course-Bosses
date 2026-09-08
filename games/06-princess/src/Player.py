"""
ISPPV1 2023
Study Case: The Legend of the Princess (ARPG)

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the class Player.
"""

from typing import Any

from gale.command import CommandBindings
from gale.timer import Timer
from gale.input_handler import InputData

import settings

from src.commands import (
    INTERACT,
    MOVE_DOWN,
    MOVE_LEFT,
    MOVE_RIGHT,
    MOVE_UP,
    STOP_MOVE_DOWN,
    STOP_MOVE_LEFT,
    STOP_MOVE_RIGHT,
    STOP_MOVE_UP,
    SWORD,
    FIRE,
)
from src.Entity import Entity
from src.definitions.player_items import PLAYER_ITEM_DEFS
from src.GameObject import GameObject


class Player(Entity):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

        # Edge-triggered intent: sword/take are one-shot actions resolved
        # (and cleared) by whichever player state's update() consumes them,
        # the same way jump_requested works in 05-super_martian.
        self.sword_requested = False
        self.interact_requested = False
        self.fire_requested = False

        self.active = True

        self.bow = None

        self.command_bindings = CommandBindings()
        self.command_bindings.bind("move_left", press=MOVE_LEFT, release=STOP_MOVE_LEFT)
        self.command_bindings.bind(
            "move_right", press=MOVE_RIGHT, release=STOP_MOVE_RIGHT
        )
        self.command_bindings.bind("move_up", press=MOVE_UP, release=STOP_MOVE_UP)
        self.command_bindings.bind("move_down", press=MOVE_DOWN, release=STOP_MOVE_DOWN)
        self.command_bindings.bind("sword", press=SWORD)
        self.command_bindings.bind("enter", press=INTERACT)
        self.command_bindings.bind("fire", press=FIRE)

    def collides(self, target: Any) -> bool:
        """
        AABB with some slight shrinkage of the box on the top side, for
        perspective (so walking "into" the top edge of an obstacle from
        below doesn't collide until the player's feet actually reach it).
        """
        self_y = self.y + self.height / 2
        self_height = self.height - self.height / 2

        return not (
            self.x + self.width < target.x
            or self.x > target.x + target.width
            or self_y + self_height < target.y
            or self_y > target.y + target.height
        )

    def on_input(self, input_id: str, input_data: InputData) -> None:
        if self.active:
            self.command_bindings.dispatch(self, input_id, input_data)

    def get_item(self, item_key: str):
        item = PLAYER_ITEM_DEFS.get(item_key)
        if item is None:
            return

        self.active = False
        self.direction = "down"
        self.held["move_up"] = False

        object_display = GameObject(item.get("display_object_def"), self.x, self.y + self.height / 2)

        self.state_machine.change("pot-lift", pot=object_display)

        settings.SOUNDS["got-item"].play()

        def reactivate_player():
            action = item.get("action")
            action(self)
            self.active = True
            self.state_machine.change("idle")

        mode_duration = settings.SOUNDS["got-item"].get_length()
        self.go_invulnerable(mode_duration + 1)
        Timer.after(mode_duration, reactivate_player)
