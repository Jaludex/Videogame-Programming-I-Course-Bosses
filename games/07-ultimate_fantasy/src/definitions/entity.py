"""
ISPPV1 2023
Study Case: Ultimate Fantasy (RPG)

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the entity definitions: constants for sizing/battle
layout and ENTITY_DEFS, the data (stats, animations, actions) for every
playable class, NPC, and enemy in the game.
"""

import math

DEFAULT_CHARACTER_FRAME = 8

ENTITY_WIDTH = 16
ENTITY_HEIGHT = 18
NUM_CHARACTERS = 4

BATTLE_WIDTH = 16
BATTLE_HEIGHT = 8
BATTLE_PADDLE = {"x": 4, "y": 1}

# Party member index (0-based here, vs. Lua's 1-based) -> battle grid coords.
PARTY_BATTLE_POSITIONS = [
    {"x": BATTLE_PADDLE["x"] + 6, "y": BATTLE_PADDLE["y"] + 3},
    {"x": BATTLE_PADDLE["x"] + 6, "y": BATTLE_PADDLE["y"] + BATTLE_HEIGHT - 1},
    {"x": BATTLE_PADDLE["x"] + 3, "y": BATTLE_PADDLE["y"] + 3},
    {"x": BATTLE_PADDLE["x"] + 3, "y": BATTLE_PADDLE["y"] + BATTLE_HEIGHT - 1},
]

# Enemy count -> list of battle grid coords (relative to BATTLE_PADDLE / BATTLE_WIDTH / BATTLE_HEIGHT).
ENEMIES_POSITIONS = {
    3: [
        {"x": BATTLE_PADDLE["x"] + BATTLE_WIDTH - 6, "y": BATTLE_PADDLE["y"] + 5},
        {"x": BATTLE_PADDLE["x"] + BATTLE_WIDTH - 3, "y": BATTLE_PADDLE["y"] + 3},
        {
            "x": BATTLE_PADDLE["x"] + BATTLE_WIDTH - 3,
            "y": BATTLE_PADDLE["y"] + BATTLE_HEIGHT - 1,
        },
    ],
    4: [
        {"x": BATTLE_PADDLE["x"] + BATTLE_WIDTH - 6, "y": BATTLE_PADDLE["y"] + 3},
        {"x": BATTLE_PADDLE["x"] + BATTLE_WIDTH - 2, "y": BATTLE_PADDLE["y"] + 3},
        {
            "x": BATTLE_PADDLE["x"] + BATTLE_WIDTH - 6,
            "y": BATTLE_PADDLE["y"] + BATTLE_HEIGHT - 1,
        },
        {
            "x": BATTLE_PADDLE["x"] + BATTLE_WIDTH - 2,
            "y": BATTLE_PADDLE["y"] + BATTLE_HEIGHT - 1,
        },
    ],
    5: [
        {"x": BATTLE_PADDLE["x"] + BATTLE_WIDTH - 6, "y": BATTLE_PADDLE["y"] + 3},
        {"x": BATTLE_PADDLE["x"] + BATTLE_WIDTH - 2, "y": BATTLE_PADDLE["y"] + 3},
        {"x": BATTLE_PADDLE["x"] + BATTLE_WIDTH - 4, "y": BATTLE_PADDLE["y"] + 5},
        {
            "x": BATTLE_PADDLE["x"] + BATTLE_WIDTH - 6,
            "y": BATTLE_PADDLE["y"] + BATTLE_HEIGHT - 1,
        },
        {
            "x": BATTLE_PADDLE["x"] + BATTLE_WIDTH - 2,
            "y": BATTLE_PADDLE["y"] + BATTLE_HEIGHT - 1,
        },
    ],
}


def _character_attack(entity, target, strength):
    amount = max(
        0, math.floor(entity.compute_attack() * strength) - target.compute_defense()
    )
    target.damage(amount)
    return amount


def _character_attack_aoe(entity, targets, strength):
    amount = math.floor(entity.compute_attack() * strength)
    actual_amount = math.floor(amount / len(targets))

    for target in targets:
        target.damage(actual_amount)

    return actual_amount


def _character_heal(entity, target, strength):
    amount = math.floor(entity.compute_healing() * strength)
    target.heal(amount)
    return amount


def _character_heal_aoe(entity, targets, strength):
    amount = math.floor(entity.compute_healing() * strength)
    actual_amount = math.floor(amount / len(targets))

    for target in targets:
        target.heal(actual_amount)

    return actual_amount


def _enemy_attack(entity, target, strength=None):
    amount = max(0, entity.compute_attack() - target.compute_defense())
    target.damage(amount)
    return amount


def _boss_attack_aoe(entity, targets, strength=None):
    amount = entity.compute_attack()
    actual_amount = math.floor(amount / len(targets))

    for target in targets:
        target.damage(actual_amount)

    return actual_amount


def _boss_heal_aoe(entity, targets, strength=None):
    amount = entity.compute_healing()
    actual_amount = math.floor(amount / len(targets))

    for target in targets:
        target.heal(actual_amount)

    return actual_amount


# Shared overworld walk/idle animations for every Character/NPC (frame indices
# are 1-based sprite-sheet quads -- see settings.frame()).
_ENTITY_ANIMATIONS = {
    "walk-up": {"frames": [1, 2, 3], "interval": 0.1},
    "walk-right": {"frames": [4, 5, 6], "interval": 0.1},
    "walk-down": {"frames": [7, 8, 9], "interval": 0.1},
    "walk-left": {"frames": [10, 11, 12], "interval": 0.1},
    "idle-up": {"frames": [2], "interval": 0},
    "idle-right": {"frames": [5], "interval": 0},
    "idle-down": {"frames": [8], "interval": 0},
    "idle-left": {"frames": [11], "interval": 0},
}

ENTITY_DEFS = {
    "animations": _ENTITY_ANIMATIONS,
    "characters": [
        {
            "type": "warrior",
            "female": {"name": "Celes", "texture": "warrior-female"},
            "male": {"name": "Squall", "texture": "warrior-male"},
            "level": 1,
            "baseHP": 40,
            "baseAttack": 10,
            "baseDefense": 10,
            "baseMagic": 0,
            "HPIV": 4,
            "attackIV": 5,
            "defenseIV": 5,
            "magicIV": 0,
            "actions": [
                {
                    "name": "Attack",
                    "target_type": "enemy",
                    "sound_effect": "hit",
                    "strength": 1.5,
                    "require_target": True,
                    "func": _character_attack,
                },
            ],
        },
        {
            "type": "ranger",
            "female": {"name": "Terra", "texture": "ranger-female"},
            "male": {"name": "Cloud", "texture": "ranger-male"},
            "level": 1,
            "baseHP": 35,
            "baseAttack": 12,
            "baseDefense": 8,
            "baseMagic": 1,
            "HPIV": 2,
            "attackIV": 7,
            "defenseIV": 4,
            "magicIV": 1,
            "actions": [
                {
                    "name": "Attack",
                    "target_type": "enemy",
                    "sound_effect": "hit",
                    "strength": 1.3,
                    "require_target": True,
                    "func": _character_attack,
                },
                {
                    "name": "Arrows",
                    "target_type": "enemy",
                    "sound_effect": "arrows",
                    "strength": 10,
                    "require_target": False,
                    "func": _character_attack_aoe,
                },
            ],
        },
        {
            "type": "healer",
            "female": {"name": "Tifa", "texture": "healer-female"},
            "male": {"name": "Kimahri", "texture": "healer-male"},
            "level": 1,
            "baseHP": 25,
            "baseAttack": 2,
            "baseDefense": 5,
            "baseMagic": 10,
            "HPIV": 2,
            "attackIV": 2,
            "defenseIV": 2,
            "magicIV": 7,
            "actions": [
                {
                    "name": "Heal",
                    "target_type": "character",
                    "sound_effect": "powerup",
                    "strength": 5,
                    "require_target": True,
                    "func": _character_heal,
                },
                {
                    "name": "Global Heal",
                    "target_type": "character",
                    "sound_effect": "powerup",
                    "strength": 8,
                    "require_target": False,
                    "func": _character_heal_aoe,
                },
            ],
        },
        {
            "type": "mage",
            "female": {"name": "Rinoa", "texture": "mage-female"},
            "male": {"name": "Sephiroth", "texture": "mage-male"},
            "level": 1,
            "baseHP": 30,
            "baseAttack": 5,
            "baseDefense": 5,
            "baseMagic": 12,
            "HPIV": 2,
            "attackIV": 3,
            "defenseIV": 2,
            "magicIV": 8,
            "actions": [
                {
                    "name": "Flame",
                    "target_type": "enemy",
                    "sound_effect": "flame",
                    "strength": 10,
                    "require_target": False,
                    "func": _character_attack_aoe,
                },
            ],
        },
    ],
    "npcs": {
        "female": {
            "texture": "npc-female",
            "names": ["Alice", "Fiona", "Beth", "Cami", "Rose"],
        },
        "male": {
            "texture": "npc-male",
            "names": ["Albert", "Leon", "Nick", "Alex", "Sam"],
        },
        "texts": [
            "Good luck in your journey!",
            "You, little guys! Go to defeat the west monster and break the curse!",
            "All of you are so nice!",
            "Thank you for taking such a risk! I love you all!",
        ],
    },
    "enemies": {
        "north": [
            {
                "level": 1,
                "type": "slime",
                "texture": "slime",
                "width": 16,
                "height": 16,
                "baseHP": 15,
                "baseAttack": 20,
                "baseDefense": 5,
                "baseMagic": 0,
                "animations": {
                    "default": {"frames": [4, 5, 6], "interval": 0.3},
                },
                "actions": [
                    {
                        "name": "Attack",
                        "target_type": "enemy",
                        "sound_effect": "hit",
                        "require_target": True,
                        "func": _enemy_attack,
                    },
                ],
            },
        ],
        "south": [
            {
                "level": 2,
                "type": "worm",
                "texture": "small-worm",
                "width": 16,
                "height": 16,
                "baseHP": 30,
                "baseAttack": 30,
                "baseDefense": 7,
                "baseMagic": 0,
                "animations": {
                    "default": {"frames": [4, 5, 6], "interval": 0.15},
                },
                "actions": [
                    {
                        "name": "Attack",
                        "target_type": "enemy",
                        "sound_effect": "hit",
                        "require_target": True,
                        "func": _enemy_attack,
                    },
                ],
            },
        ],
        "east": [
            {
                "level": 3,
                "type": "snake",
                "texture": "snake",
                "width": 16,
                "height": 16,
                "baseHP": 40,
                "baseAttack": 40,
                "baseDefense": 15,
                "baseMagic": 2,
                "animations": {
                    "default": {"frames": [4, 5, 6], "interval": 0.15},
                },
                "actions": [
                    {
                        "name": "Attack",
                        "target_type": "enemy",
                        "sound_effect": "hit",
                        "require_target": True,
                        "func": _enemy_attack,
                    },
                ],
            },
        ],
        "west": [
            {
                "level": 4,
                "type": "pumpking",
                "texture": "pumpking",
                "width": 23,
                "height": 23,
                "baseHP": 55,
                "baseAttack": 60,
                "baseDefense": 18,
                "baseMagic": 5,
                "animations": {
                    "default": {"frames": [4, 5, 6], "interval": 0.15},
                },
                "actions": [
                    {
                        "name": "Attack",
                        "target_type": "enemy",
                        "sound_effect": "hit",
                        "require_target": True,
                        "func": _enemy_attack,
                    },
                ],
            },
        ],
        "boss": {
            "level": 10,
            "type": "boss",
            "name": "Man-Eater Flower",
            "texture": "man-eater-flower",
            "width": 30,
            "height": 38,
            "baseHP": 100,
            "baseAttack": 100,
            "baseDefense": 30,
            "baseMagic": 30,
            "animations": {
                "default": {"frames": [4, 5, 6], "interval": 0.15},
            },
            "actions": [
                {
                    "name": "Attack",
                    "target_type": "enemy",
                    "sound_effect": "hit",
                    "require_target": True,
                    "func": _enemy_attack,
                },
                {
                    "name": "Flame",
                    "target_type": "enemy",
                    "sound_effect": "flame",
                    "require_target": False,
                    "func": _boss_attack_aoe,
                },
                {
                    "name": "Global Heal",
                    "target_type": "character",
                    "sound_effect": "powerup",
                    "require_target": False,
                    "func": _boss_heal_aoe,
                },
            ],
        },
    },
}
