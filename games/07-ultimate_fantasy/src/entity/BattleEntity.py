"""
ISPPV1 2023
Study Case: Ultimate Fantasy (RPG)

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the class BattleEntity: adds battle stats (HP/attack/
defense/magic) and the damage/heal/compute-* formulas shared by both
Character (playable) and Enemy.
"""

import math
import random
from typing import Any, Dict, List

from src.entity.Entity import Entity


class BattleEntity(Entity):
    def __init__(self, definition: Dict[str, Any]) -> None:
        super().__init__(definition)

        self.klass: str = definition["class"]
        self.actions: List[Dict[str, Any]] = definition["actions"]
        self.level: int = definition.get("level", 1)
        self.dead: bool = definition.get("dead", False)

        self.base_hp: float = definition["baseHP"]
        self.base_attack: float = definition["baseAttack"]
        self.base_defense: float = definition["baseDefense"]
        self.base_magic: float = definition["baseMagic"]

        self.hp: float = self.base_hp
        self.attack: float = self.base_attack
        self.defense: float = self.base_defense
        self.magic: float = self.base_magic

        self.current_hp: float = self.hp

    def damage(self, amount: float) -> None:
        self.current_hp -= amount

        if self.current_hp <= 0:
            self.dead = True

    def heal(self, amount: float) -> None:
        if not self.dead:
            self.current_hp = min(self.hp, self.current_hp + amount)

    def compute_attack(self) -> int:
        return math.floor(random.random() / 2 * self.attack + random.random() / 4 * self.magic)

    def compute_defense(self) -> int:
        return math.floor(
            random.random() / 4 * self.defense + random.random() / 8 * self.magic
        )

    def compute_healing(self) -> int:
        return math.floor(random.random() * 2 * self.magic)
