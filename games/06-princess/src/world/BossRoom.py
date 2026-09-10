"""
ISPPV1 2023
Study Case: The Legend of the Princess (ARPG)

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the class Room.
"""

import random
from typing import Any, Callable, List, Optional, TypeVar

import pygame

from gale.tilemap import TileMap

import settings
from src.world.Room import Room
from src.definitions.entity import ENTITY_DEFS
from src.definitions.game_objects import GAME_OBJECT_DEFS
from src.Entity import Entity
from src.GameObject import GameObject
from src.world.Doorway import Doorway
from src.DragonBoss import DragonBoss
from src.states.entity.boss.BossIdleState import BossIdleState
from src.states.entity.boss.BossWeakState import BossWeakState

_DOORWAY_ZONES = {
    "left": pygame.Rect(
        -settings.TILE_SIZE - 6,
        settings.MAP_RENDER_OFFSET_Y + settings.MAP_HEIGHT // 2 * settings.TILE_SIZE - settings.TILE_SIZE * 2,
        settings.TILE_SIZE * 2 + 6,
        settings.TILE_SIZE * 3,
    ),
    "right": pygame.Rect(
        settings.MAP_RENDER_OFFSET_X + settings.MAP_WIDTH * settings.TILE_SIZE - 6,
        settings.MAP_RENDER_OFFSET_Y + settings.MAP_HEIGHT // 2 * settings.TILE_SIZE - settings.TILE_SIZE * 2,
        settings.TILE_SIZE * 2 + 6,
        settings.TILE_SIZE * 3,
    ),
    "top": pygame.Rect(
        settings.MAP_RENDER_OFFSET_X + settings.MAP_WIDTH // 2 * settings.TILE_SIZE - settings.TILE_SIZE,
        -settings.TILE_SIZE - 6,
        settings.TILE_SIZE * 2,
        settings.TILE_SIZE * 2 + 12,
    ),
    "bottom": pygame.Rect(
        settings.MAP_RENDER_OFFSET_X + settings.MAP_WIDTH // 2 * settings.TILE_SIZE - settings.TILE_SIZE,
        settings.VIRTUAL_HEIGHT - settings.TILE_SIZE - 6,
        settings.TILE_SIZE * 2,
        settings.TILE_SIZE * 2 + 12,
    ),
}


def _doorway_opening_for(
    rect: pygame.Rect, doorways_by_direction: dict
) -> Optional[pygame.Rect]:
    """
    :returns: The precise opening rect of whichever doorway rect is
        close to (i.e. overlapping the wider detection zone of), or
        None if rect isn't near any doorway right now.
    """
    for direction, zone in _DOORWAY_ZONES.items():
        if zone.colliderect(rect):
            return doorways_by_direction[direction].get_collision_rect()

    return None


class BossRoom(Room):
    def __init__(
        self,
        player: TypeVar("Player"),
        on_game_over: Callable[[], None],
        level: int,
    ) -> None:
        self.level = 1
        super().__init__(player, on_game_over)

        self.doorway_pos = "top"
        if player.direction == "up":
            self.doorway_pos = "bottom"
        elif player.direction == "left":
            self.doorway_pos = "right"
        elif player.direction == "right":
            self.doorway_pos = "left"

        self.key = "boss"
        self.finished = False

    def finish_shift(self):
        self.entities[0].active = True
        

    def update(self, dt: float) -> None:
        if self.adjacent_offset_x != 0 or self.adjacent_offset_y != 0:
            return

        self.player.update(dt)

        if self.player.health <= 0:
            self.on_game_over()

        for entity in self.entities:
            if entity.health <= 0:
                entity.dead = True

            elif not entity.dead:
                entity.process_ai(self, dt)
                entity.update(dt)

            # Collision between the player and entities in the room.
            if (not entity.dead
                and self.player.collides(entity)):
                self._push_player_out_of(entity)
                if not self.player.invulnerable:
                    settings.SOUNDS["hit-player"].play()
                    self.player.damage(2)
                    self.player.go_invulnerable(1.5)
                    

                    if self.player.dead:
                        self.on_game_over()

        for projectile in list(self.projectiles):
            projectile.update(dt)
            if projectile.dead:
                self.projectiles.remove(projectile)
                continue

            if projectile.sender == "player":
                for entity in self.entities:
                    if not entity.dead and entity.collides_with_head(projectile.obj):
                        entity.make_weak()
                        entity.damage(1)
                        settings.SOUNDS["hit-enemy"].play()
                        projectile.dead = True

            elif projectile.sender == "enemy":
                if not self.player.dead and projectile.collides(self.player):
                    self.player.damage(1)
                    settings.SOUNDS["hit-player"].play()
                    projectile.dead = True

            elif projectile.sender == "boss":
                if not self.player.dead and projectile.collides(self.player):
                    self.player.dead = True
                    settings.SOUNDS["hit-player"].play()
                    projectile.dead = True
                
            if projectile.dead:
                self.projectiles.remove(projectile)

        if self.player.dead:
            self.on_game_over()

        self.entities = [entity for entity in self.entities if not entity.dead]

        if len(self.entities) == 0 and not self.finished:
            for doorway in self.doorways:
                doorway.open = True

            self.finished = True
            settings.SOUNDS["door"].play()

    def _generate_entities(self) -> None:
        definition = ENTITY_DEFS["dragon_boss"]

        for _ in range(0, self.level):
            while True:
                # 1. Generar candidato a Boss en una posición aleatoria
                boss = DragonBoss(
                    x=random.randint(
                        settings.MAP_RENDER_OFFSET_X + settings.TILE_SIZE * 3,
                        settings.VIRTUAL_WIDTH - (settings.TILE_SIZE * 3) - 40,
                    ),
                    y=random.randint(
                        settings.MAP_RENDER_OFFSET_Y + settings.TILE_SIZE * 3,
                        (settings.MAP_HEIGHT * settings.TILE_SIZE)
                        + settings.MAP_RENDER_OFFSET_Y
                        - (settings.TILE_SIZE * 3)
                        - 32,
                    ),
                    width=40,
                    height=32,
                    walk_speed=80,
                    health=30,
                    animation_defs=definition["animations"],
                    states={},
                    player=self.player
                )
                
                has_collision = any(boss.collides(entity) for entity in self.entities)
                
                if not has_collision:
                    break

            # Configuración de estados y agregado a la lista fuera del bucle de validación
            boss.state_machine.states = {
                "idle": lambda sm, e=boss: BossIdleState(e, sm),
                "weak": lambda sm, e=boss: BossWeakState(e, sm)
            }
            boss.change_state("idle")

            self.entities.append(boss)

    def attackable_entities(self):
        return [entity for entity in self.entities if entity.weak and not entity.dead]

    def _generate_objects(self) -> None:
        pass

    def render(
        self,
        surface: pygame.Surface,
        camera_offset_x: float = 0,
        camera_offset_y: float = 0,
    ) -> None:
        offset_x = self.adjacent_offset_x + camera_offset_x
        offset_y = self.adjacent_offset_y + camera_offset_y

        for y in range(self.height):
            for x in range(self.width):
                gid = self.tilemap.get_gid("floor", y, x)
                tileset = self.tilemap.tileset_for_gid(gid)
                surface.blit(
                    tileset.image,
                    (
                        x * settings.TILE_SIZE + self.render_offset_x + offset_x,
                        y * settings.TILE_SIZE + self.render_offset_y + offset_y,
                    ),
                    tileset.rect_for(gid),
                )

        for doorway in self.doorways:
            if doorway.direction == self.doorway_pos:
                doorway.render(surface, offset_x, offset_y)

        for obj in self.objects:
            obj.render(surface, offset_x, offset_y)

        for entity in self.entities:
            if not entity.dead:
                entity.render(surface, offset_x, offset_y)

        if self.player:
            self.player.visibility_clip_rect = _doorway_opening_for(
                self.player.get_collision_rect(), self._doorways_by_direction
            )
            self.player.render(surface, camera_offset_x, camera_offset_y)
            self.player.visibility_clip_rect = None

        for projectile in self.projectiles:
            if not _doorway_opening_for(
                projectile.get_collision_rect(), self._doorways_by_direction
            ):
                projectile.render(surface, camera_offset_x, camera_offset_y)
