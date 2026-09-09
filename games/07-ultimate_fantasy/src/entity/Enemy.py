"""
ISPPV1 2023
Study Case: Ultimate Fantasy (RPG)

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the class Enemy: a battle-only monster. Thin subclass
of BattleEntity -- enemies have fixed stats for the fight, no leveling.
"""

from typing import Any, Dict

from src.entity.BattleEntity import BattleEntity


class Enemy(BattleEntity):
    def __init__(self, definition: Dict[str, Any]) -> None:
        super().__init__(definition)
