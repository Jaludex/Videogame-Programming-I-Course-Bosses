"""
ISPPV1 2023
Study Case: Ultimate Fantasy (RPG)

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the class NPC: a static townfolk entity the player can
talk to.
"""

import random
from typing import Any, Dict

from src.definitions.entity import ENTITY_DEFS
from src.entity.Entity import Entity


class NPC(Entity):
    def __init__(self, definition: Dict[str, Any]) -> None:
        super().__init__(definition)

    def on_interact(self) -> str:
        """
        :returns: The dialogue line this NPC says (its name plus a random
        line from ENTITY_DEFS["npcs"]["texts"]). Unlike the original,
        which pushed a DialogueState directly onto a Lua global
        `stateStack`, this just returns the text -- the caller (World)
        owns the state stack reference and pushes DialogueState itself.
        """
        text = random.choice(ENTITY_DEFS["npcs"]["texts"])
        return f"{self.name}: {text}"
