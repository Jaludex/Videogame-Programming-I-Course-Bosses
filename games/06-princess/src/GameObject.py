"""
ISPPV1 2023
Study Case: The Legend of the Princess (ARPG)

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the class GameObject.
"""

from typing import Any, Dict

import pygame

import settings


class GameObject:
    def __init__(self, definition: Dict[str, Any], x: float, y: float) -> None:
        self.type = definition["type"]
        self.texture_id = definition["texture"]
        self.frame_index = definition.get("frame", 1)

        # Whether it acts as an obstacle or not.
        self.solid = definition["solid"]

        self.default_state = definition["default_state"]
        self.state = self.default_state
        self.states = definition["states"]

        self.x = x
        self.y = y
        self.width = definition["width"]
        self.height = definition["height"]

        self.on_collide = definition.get("on_collide") or (lambda: None)

        # Whether this object is consumable or not.
        self.consumable = definition.get("consumable", False)
        self.on_consume = definition.get("on_consume") or (lambda player, obj: None)

        # An object could be taken or not.
        self.takeable = definition.get("takeable", False)
        self.taken = False

    def get_collision_rect(self) -> pygame.Rect:
        return pygame.Rect(round(self.x), round(self.y), self.width, self.height)

    def update(self, dt: float) -> None:
        pass

    def render(self, surface: pygame.Surface, offset_x: float = 0, offset_y: float = 0, angle: float = 0) -> None:
        frame_index = self.states[self.state].get("frame", self.frame_index)
    
        full_texture = settings.TEXTURES[self.texture_id]
        frame_rect = settings.frame(self.texture_id, frame_index)
        
        frame_surface = full_texture.subsurface(frame_rect)
        
        dest_x = self.x + offset_x
        dest_y = self.y + offset_y

        if angle != 0:
            rotated_surface = pygame.transform.rotate(frame_surface, angle)
            
            orig_rect = pygame.Rect(dest_x, dest_y, frame_rect.width, frame_rect.height)
            new_rect = rotated_surface.get_rect(center=orig_rect.center)
            
            surface.blit(rotated_surface, new_rect.topleft)
        else:
            surface.blit(frame_surface, (dest_x, dest_y))
