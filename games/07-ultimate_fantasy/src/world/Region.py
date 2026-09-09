"""
ISPPV1 2023
Study Case: Ultimate Fantasy (RPG)

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the class Region: procedurally generates a single
screen's worth of overworld tiles (base grass, fence border with optional
gates, and a decoration layer of flowers/tall-grass/NPCs). There is no
Tiled/TMX map here -- everything is generated directly in code, exactly
like the original. The three layers live in a single gale.tilemap.TileMap
instead of a bespoke class, but the generation algorithm itself --
order, randomness, gate carving -- is untouched.
"""

import random
from typing import Any, Dict, Optional

import pygame

from gale.state import StateMachine
from gale.tilemap import TileMap

import settings
from src.definitions.entity import ENTITY_DEFS, ENTITY_HEIGHT, ENTITY_WIDTH
from src.entity.NPC import NPC
from src.states.entity.NPCIdleState import NPCIdleState

TILE_IDS = settings.TILE_IDS


class Region:
    def __init__(self, definition: Optional[Dict[str, Any]] = None) -> None:
        definition = definition or {}

        self.tile_width: int = definition.get("tile_width", settings.TILE_WIDTH)
        self.tile_height: int = definition.get("tile_height", settings.TILE_HEIGHT)

        self.is_town: bool = definition.get("is_town", False)
        self.num_npcs: int = random.randint(2, 4) if self.is_town else 0
        self.npcs = []

        self.tilemap = TileMap(
            settings.TILE_SIZE, settings.TILE_SIZE, self.tile_width, self.tile_height
        )
        self.tilemap.add_tileset(settings.TILESET)

        self.gates = {
            "north": definition.get("north_gate", False),
            "south": definition.get("south_gate", False),
            "east": definition.get("east_gate", False),
            "west": definition.get("west_gate", False),
        }

        self._create_maps()

    def _create_maps(self) -> None:
        width, height = self.tile_width, self.tile_height

        # Step A: base layer (ground) -- every cell a random grass variant.
        base = self.tilemap.add_layer("base")
        for y in range(1, height + 1):
            for x in range(1, width + 1):
                base[y - 1][x - 1] = random.choice(TILE_IDS["grass"])

        # Step B: fence layer (border wall).
        fence = self.tilemap.add_layer("fence")
        for y in range(1, height + 1):
            for x in range(1, width + 1):
                if y == 1:
                    if x == 1:
                        tile_id = TILE_IDS["top-left-fence"]
                    elif x == width:
                        tile_id = TILE_IDS["top-right-fence"]
                    else:
                        tile_id = TILE_IDS["top-fence"]
                elif y == height:
                    if x == 1:
                        tile_id = TILE_IDS["bottom-left-fence"]
                    elif x == width:
                        tile_id = TILE_IDS["bottom-right-fence"]
                    else:
                        tile_id = TILE_IDS["bottom-fence"]
                elif x == 1:
                    tile_id = TILE_IDS["left-fence"]
                elif x == width:
                    tile_id = TILE_IDS["right-fence"]
                else:
                    tile_id = TILE_IDS["empty"]

                fence[y - 1][x - 1] = tile_id

        # Step C: gate carving (up to 4 gates, 2-tile-wide openings flanked
        # by "border" fence-cap tiles). `_set_fence` takes 1-based tile
        # (x, y) grid coordinates, same convention every other step here
        # uses, and overwrites that cell's gid in the fence layer.
        def _set_fence(tx: int, ty: int, tile_id: int) -> None:
            fence[ty - 1][tx - 1] = tile_id

        if self.gates["north"]:
            x = width // 2
            _set_fence(x - 1, 1, TILE_IDS["border-left-fence"])
            _set_fence(x, 1, TILE_IDS["empty"])
            _set_fence(x + 1, 1, TILE_IDS["empty"])
            _set_fence(x + 2, 1, TILE_IDS["border-right-fence"])

        if self.gates["south"]:
            x = width // 2
            _set_fence(x - 1, height, TILE_IDS["border-left-fence"])
            _set_fence(x, height, TILE_IDS["empty"])
            _set_fence(x + 1, height, TILE_IDS["empty"])
            _set_fence(x + 2, height, TILE_IDS["border-right-fence"])

        if self.gates["west"]:
            y = height // 2
            _set_fence(1, y - 1, TILE_IDS["border-bottom-left-fence"])
            _set_fence(1, y, TILE_IDS["empty"])
            _set_fence(1, y + 1, TILE_IDS["empty"])
            _set_fence(1, y + 2, TILE_IDS["border-top-left-fence"])

        if self.gates["east"]:
            y = height // 2
            _set_fence(width, y - 1, TILE_IDS["border-bottom-right-fence"])
            _set_fence(width, y, TILE_IDS["empty"])
            _set_fence(width, y + 1, TILE_IDS["empty"])
            _set_fence(width, y + 2, TILE_IDS["border-top-right-fence"])

        # Step D: grass/flowers/NPC decoration layer.
        grass = self.tilemap.add_layer("grass")
        for y in range(1, height + 1):
            for x in range(1, width + 1):
                if y == 1 or y == height or x == 1 or x == width:
                    tile_id = TILE_IDS["empty"]
                elif self.is_town:
                    if random.random() < 0.2:
                        tile_id = random.choice(TILE_IDS["flowers"])
                    else:
                        tile_id = TILE_IDS["empty"]
                        if (
                            len(self.npcs) < self.num_npcs
                            and random.random() < 0.05
                            and y != height // 2
                        ):
                            self._create_npc(x, y)
                else:
                    if random.random() < 0.3:
                        tile_id = TILE_IDS["tall-grass"]
                    else:
                        tile_id = TILE_IDS["empty"]

                grass[y - 1][x - 1] = tile_id

    def _create_npc(self, x: int, y: int) -> None:
        width, height = self.tile_width, self.tile_height

        if x <= width / 2 and y <= height / 2:
            direction = "down" if random.random() < 0.6 else "right"
        elif x <= width / 2:
            direction = "up" if random.random() < 0.4 else "right"
        elif y <= height / 2:
            direction = "down" if random.random() < 0.6 else "left"
        else:
            direction = "up" if random.random() < 0.4 else "left"

        gender = "male" if random.random() < 0.5 else "female"

        names = ENTITY_DEFS["npcs"][gender]["names"]
        name = names.pop(random.randrange(len(names)))

        npc = NPC(
            {
                "name": name,
                "map_x": x,
                "map_y": y,
                "width": ENTITY_WIDTH,
                "height": ENTITY_HEIGHT,
                "direction": direction,
                "animations": ENTITY_DEFS["animations"],
                "texture": ENTITY_DEFS["npcs"][gender]["texture"],
            }
        )

        npc.state_machine = StateMachine({"idle": lambda sm: NPCIdleState(npc, sm)})
        npc.state_machine.change("idle")

        self.npcs.append(npc)

    def update(self, dt: float) -> None:
        pass

    def render(self, surface: pygame.Surface) -> None:
        self.tilemap.render(surface)

        for npc in self.npcs:
            npc.render(surface)
