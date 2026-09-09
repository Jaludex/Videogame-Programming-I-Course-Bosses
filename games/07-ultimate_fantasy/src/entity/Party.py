"""
ISPPV1 2023
Study Case: Ultimate Fantasy (RPG)

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the class Party: the group of playable Characters
moving together on the overworld map (a leader plus followers trailing
behind it), and its own idle/walk state machine.
"""

from typing import Any, Dict, Optional, TypeVar

import pygame

from gale.state import StateMachine

import settings
from src.definitions.entity import ENTITY_DEFS, ENTITY_HEIGHT, ENTITY_WIDTH, PARTY_BATTLE_POSITIONS
from src.entity.Character import Character
from src.states.entity.CharacterIdleState import CharacterIdleState
from src.states.entity.CharacterWalkState import CharacterWalkState
from src.states.entity.PartyIdleState import PartyIdleState
from src.states.entity.PartyWalkState import PartyWalkState


class Party:
    def __init__(self, party_genders: Dict[int, str], world: TypeVar("World")) -> None:
        self.world = world
        # Kept around (not just consumed) so a save can be reconstructed:
        # rebuilding a Character needs the same gender-driven texture/
        # name/animations that were used to create it the first time.
        self.party_genders = dict(party_genders)

        # Tracks which movement keys are currently held down, polled once per
        # frame (in left/right/up/down priority order) by PartyIdleState,
        # the same way every prior port tracks continuous movement input.
        self.held = {
            "move_left": False,
            "move_right": False,
            "move_up": False,
            "move_down": False,
        }

        x = settings.TILE_WIDTH // 2 + 2
        y = settings.TILE_HEIGHT // 2

        self.characters: Dict[int, Character] = {}

        for k in sorted(party_genders.keys()):
            gender = party_genders[k]
            char_def = ENTITY_DEFS["characters"][k]
            gender_def = char_def[gender]

            character = Character(
                {
                    "name": gender_def["name"],
                    "texture": gender_def["texture"],
                    "class": char_def["type"],
                    "level": char_def["level"],
                    "baseHP": char_def["baseHP"],
                    "baseAttack": char_def["baseAttack"],
                    "baseDefense": char_def["baseDefense"],
                    "baseMagic": char_def["baseMagic"],
                    "HPIV": char_def["HPIV"],
                    "attackIV": char_def["attackIV"],
                    "defenseIV": char_def["defenseIV"],
                    "magicIV": char_def["magicIV"],
                    "actions": char_def["actions"],
                    "direction": "down",
                    "map_x": x,
                    "map_y": y,
                    "width": ENTITY_WIDTH,
                    "height": ENTITY_HEIGHT,
                    "animations": ENTITY_DEFS["animations"],
                }
            )
            # Rolls the IV-based stat growth up to the character's starting
            # level (here just level 1, i.e. a single pass).
            character.calculate_stats()

            character.state_machine = StateMachine(
                {
                    "idle": lambda sm, c=character: CharacterIdleState(c, sm),
                    "walk": lambda sm, c=character: CharacterWalkState(c, sm),
                }
            )
            character.change_state("idle")

            self.characters[k] = character
            # Each subsequent party member starts one tile behind (to the
            # left of) the previous one, in a straight line.
            x -= 1

        self.state_machine = StateMachine(
            {
                "idle": lambda sm: PartyIdleState(self, sm),
                "walk": lambda sm: PartyWalkState(self, sm),
            }
        )
        self.state_machine.change("idle")

    def change_state(self, name: str, *args: Any, **kwargs: Any) -> None:
        self.state_machine.change(name, *args, **kwargs)

    def on_input(self, input_id: str, input_data: Any) -> None:
        if input_id in self.held:
            if input_data.pressed:
                self.held[input_id] = True
            elif input_data.released:
                self.held[input_id] = False

    def set_battle_positions(self) -> None:
        for k, character in self.characters.items():
            if character.dead:
                continue

            position = PARTY_BATTLE_POSITIONS[k]
            character.map_x = position["x"]
            character.map_y = position["y"]
            character.x = (character.map_x - 1) * settings.TILE_SIZE
            character.y = (character.map_y - 1) * settings.TILE_SIZE - character.height / 2
            character.direction = "right"

        self.change_state("idle")

    def set_position(self, x: int, y: int, direction: str) -> None:
        dx, dy = 0, 0

        if direction == "up":
            dy = 1
        elif direction == "down":
            dy = -1
        elif direction == "right":
            dx = -1
        elif direction == "left":
            dx = 1

        for k in sorted(self.characters.keys()):
            character = self.characters[k]

            if character.dead:
                continue

            character.map_x = x
            character.map_y = y
            character.x = (x - 1) * settings.TILE_SIZE
            character.y = (y - 1) * settings.TILE_SIZE - character.height / 2
            character.direction = direction

            x += dx
            y += dy

        self.change_state("idle")

    def first_alive_position(self) -> Optional[int]:
        for k in sorted(self.characters.keys()):
            if not self.characters[k].dead:
                return k

        return None

    def first_alive(self) -> Optional[Character]:
        position = self.first_alive_position()
        return self.characters[position] if position is not None else None

    def update(self, dt: float) -> None:
        self.state_machine.update(dt)

        for character in self.characters.values():
            if not character.dead:
                character.update(dt)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "genders": self.party_genders,
            "characters": {
                str(k): character.to_dict() for k, character in self.characters.items()
            },
        }

    def load_dict(self, data: Dict[str, Any]) -> None:
        for k, character_data in data["characters"].items():
            self.characters[int(k)].load_dict(character_data)

        leader = self.first_alive()

        if leader is not None:
            self.set_position(leader.map_x, leader.map_y, leader.direction)

    def render(self, surface: pygame.Surface) -> None:
        self.state_machine.render(surface)
