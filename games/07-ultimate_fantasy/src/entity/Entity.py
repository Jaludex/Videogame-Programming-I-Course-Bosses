"""
ISPPV1 2023
Study Case: Ultimate Fantasy (RPG)

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the class Entity, the base for anything that walks
around the overworld map (Character, NPC) sharing position/animation/
state-machine plumbing.
"""

import math
from typing import Any, Dict, Optional

import pygame

from gale.animation import Animation
from gale.state import StateMachine

import settings


class Entity:
    def __init__(self, definition: Dict[str, Any]) -> None:
        self.name: Optional[str] = definition.get("name")
        self.direction: str = definition.get("direction", "down")
        self.texture: str = definition["texture"]
        self.animations: Dict[str, Animation] = self._create_animations(
            definition["animations"]
        )
        self.current_animation: Optional[Animation] = None

        self.map_x: int = definition["map_x"]
        self.map_y: int = definition["map_y"]
        self.width: int = definition["width"]
        self.height: int = definition["height"]

        self.x: float = (self.map_x - 1) * settings.TILE_SIZE
        # Halfway raised on the tile just to simulate height/perspective.
        self.y: float = (self.map_y - 1) * settings.TILE_SIZE - self.height / 2

        # Assigned externally by whatever builds this entity (mirrors the
        # original, where Entity:init never sets stateMachine itself).
        self.state_machine: Optional[StateMachine] = None

    def _create_animations(
        self, animation_defs: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Animation]:
        animations = {}

        for name, adef in animation_defs.items():
            frames = [settings.frame(self.texture, i) for i in adef["frames"]]
            animations[name] = Animation(frames, adef.get("interval", 0))

        return animations

    def change_state(self, name: str, *args: Any, **kwargs: Any) -> None:
        self.state_machine.change(name, *args, **kwargs)

    def change_animation(self, name: str) -> None:
        self.current_animation = self.animations[name]

    def on_interact(self) -> None:
        pass

    def process_ai(self, params: Dict[str, Any], dt: float) -> None:
        current = self.state_machine.current

        if hasattr(current, "process_ai"):
            current.process_ai(params, dt)

    def update(self, dt: float) -> None:
        if self.current_animation is not None:
            self.current_animation.update(dt)

        self.state_machine.update(dt)

    def render(self, surface: pygame.Surface) -> None:
        self.state_machine.render(surface)

    def render_sprite(self, surface: pygame.Surface) -> None:
        if self.current_animation is None:
            return

        surface.blit(
            settings.TEXTURES[self.texture],
            (math.floor(self.x), math.floor(self.y)),
            self.current_animation.get_current_frame(),
        )
