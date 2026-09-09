"""
ISPPV1 2023
Study Case: Ultimate Fantasy (RPG)

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the class World: holds the 5 procedurally generated
regions (center/town plus north/south/east/west), the party, and the
region-to-region gate-transition logic (fade out -> swap region -> fade
in -> announce region name).
"""

from typing import Any, Dict, Optional

import pygame

from gale.state import StateStack

import settings
from src.entity.Party import Party
from src.world.Region import Region


class World:
    def __init__(self, stack: StateStack, party_genders: Dict[int, str]) -> None:
        self.stack = stack

        self.regions = {
            "center": Region(
                {
                    "is_town": True,
                    "north_gate": True,
                    "south_gate": True,
                    "east_gate": True,
                    "west_gate": True,
                }
            ),
            "north": Region({"south_gate": True}),
            "south": Region({"north_gate": True}),
            "east": Region({"west_gate": True}),
            "west": Region({"east_gate": True}),
        }
        self.current_region_name = "center"

        self.party = Party(party_genders, self)

        # World is constructed both for a new game (SelectCharacterState
        # already stopped "intro") and for a loaded save (StartState's
        # "continue" path never does), so stop it here too -- redundant
        # in the first case, the actual fix in the second.
        settings.stop_music("intro")
        settings.play_music("town")

    def current_region(self) -> Region:
        return self.regions[self.current_region_name]

    def move(self, direction: str) -> None:
        from src.states.game.FadeInState import FadeInState
        from src.states.game.FadeOutState import FadeOutState
        from src.states.game.ShowTextState import ShowTextState

        leader = self.party.first_alive()

        if leader is None:
            return

        alive_count = sum(1 for c in self.party.characters.values() if not c.dead)
        x, y = leader.map_x, leader.map_y
        next_region: Optional[str] = None

        if direction == "right" and self.current_region_name == "center":
            next_region, x = "east", alive_count
        elif direction == "left" and self.current_region_name == "center":
            next_region, x = "west", settings.TILE_WIDTH - alive_count + 1
        elif direction == "up" and self.current_region_name == "center":
            next_region, y = "north", settings.TILE_HEIGHT - alive_count + 1
        elif direction == "down" and self.current_region_name == "center":
            next_region, y = "south", alive_count
        elif direction == "right" and self.current_region_name == "west":
            next_region, x = "center", alive_count
        elif direction == "left" and self.current_region_name == "east":
            next_region, x = "center", settings.TILE_WIDTH - alive_count + 1
        elif direction == "up" and self.current_region_name == "south":
            next_region, y = "center", settings.TILE_HEIGHT - alive_count + 1
        elif direction == "down" and self.current_region_name == "north":
            next_region, y = "center", alive_count

        if next_region is None:
            return

        def on_fade_in_complete() -> None:
            if self.current_region_name == "center":
                settings.stop_music("town")
            else:
                settings.stop_music("world")

            self.current_region_name = next_region

            if next_region == "center":
                settings.play_music("town")
            else:
                settings.play_music("world")

            self.party.set_position(x, y, direction)

            def on_fade_out_complete() -> None:
                self.stack.push(
                    ShowTextState(self.stack),
                    color=(0, 0, 0),
                    text=next_region,
                    on_complete=lambda: None,
                )

            self.stack.push(
                FadeOutState(self.stack),
                color=(255, 255, 255),
                time=0.5,
                on_complete=on_fade_out_complete,
            )

        self.stack.push(
            FadeInState(self.stack),
            color=(255, 255, 255),
            time=1,
            on_complete=on_fade_in_complete,
        )

    def update(self, dt: float) -> None:
        self.current_region().update(dt)
        self.party.update(dt)

    def on_input(self, input_id: str, input_data: Any) -> None:
        self.party.on_input(input_id, input_data)

        if input_id == "space" and input_data.pressed:
            self._try_interact()

    def _try_interact(self) -> None:
        from src.states.game.DialogueState import DialogueState

        player = self.party.first_alive()

        if player is None:
            return

        for npc in self.current_region().npcs:
            dx = abs(npc.map_x - player.map_x)
            dy = abs(npc.map_y - player.map_y)

            if dx <= 1 and dy <= 1:
                text = npc.on_interact()
                self.stack.push(DialogueState(self.stack), text=text)
                return

    def render(self, surface: pygame.Surface) -> None:
        self.current_region().render(surface)
        self.party.render(surface)

    def to_dict(self) -> Dict[str, Any]:
        """
        Regions themselves are left out on purpose: they are generated
        proceduralmente (Section on tile maps, Chapter 7) from nothing
        but their gate configuration, which is fixed in __init__ and
        never mutated, so there is nothing region-specific worth
        persisting -- only which one the party is currently in.
        """
        return {
            "current_region_name": self.current_region_name,
            "party": self.party.to_dict(),
        }

    def load_dict(self, data: Dict[str, Any]) -> None:
        self.current_region_name = data["current_region_name"]
        self.party.load_dict(data["party"])

        if self.current_region_name != "center":
            settings.stop_music("town")
            settings.play_music("world")
