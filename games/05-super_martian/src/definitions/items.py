"""
ISPPV1 2023
Study Case: Super Martian (Platformer)

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the definition for items.
"""

from typing import Dict, Any

import random

from gale.timer import Timer

import settings
from src.GameItem import GameItem
from src.Player import Player


def pickup_coin(
    coin: GameItem, player: Player, points: int, color: int, time: float
) -> None:
    settings.SOUNDS["pickup_coin"].stop()
    settings.SOUNDS["pickup_coin"].play()
    player.score += points
    player.coins_counter[color] += 1
    Timer.after(time, lambda: coin.respawn())


def pickup_green_coin(coin: GameItem, player: Player):
    pickup_coin(coin, player, 1, 62, random.uniform(2, 4))


def pickup_blue_coin(coin: GameItem, player: Player):
    pickup_coin(coin, player, 5, 61, random.uniform(5, 8))


def pickup_red_coin(coin: GameItem, player: Player):
    pickup_coin(coin, player, 20, 55, random.uniform(10, 18))


def pickup_yellow_coin(coin: GameItem, player: Player):
    pickup_coin(coin, player, 50, 54, random.uniform(20, 25))


def collide_key_block(block: GameItem, player: Player):
    player.spawn_key_at = (block.x, block.y)

    block.collidable = False
    original_y = block.y
    new_y = block.y - (block.height / 2)

    def get_the_block_back():
        Timer.tween(
            0.12,
            [
                (block, {"y": original_y})
            ],
        )

    Timer.tween(
        0.12,
        [
            (block, {"y": new_y})
        ],
        on_finish=get_the_block_back
    )

def pickup_key(key: GameItem, player: Player):
    player.grabbed_key = True
    key.collidable = False

    def swap_key():
        if key.frame_index == 69:
            key.frame_index = 70
        else:
            key.frame_index = 69

    Timer.every(
        0.5,
        swap_key
    )


ITEMS: Dict[str, Dict[int, Dict[str, Any]]] = {
    "coins": {
        62: {
            "texture_id": "tiles",
            "consumable": True,
            "collidable": True,
            "on_consume": pickup_green_coin,
        },
        61: {
            "texture_id": "tiles",
            "consumable": True,
            "collidable": True,
            "on_consume": pickup_blue_coin,
        },
        55: {
            "texture_id": "tiles",
            "consumable": True,
            "collidable": True,
            "on_consume": pickup_red_coin,
        },
        54: {
            "texture_id": "tiles",
            "consumable": True,
            "collidable": True,
            "on_consume": pickup_yellow_coin,
        },
    },
    "blocks": {
        34: {
            "texture_id": "tiles",
            "consumable": False,
            "collidable": True,
        },
        68: {
             "texture_id": "tiles",
             "consumable": False,
             "collidable": True,
             "on_collide": collide_key_block,
        }
    },
    "keys":
    {
        69: {
            "texture_id": "tiles",
            "consumable": False,
            "collidable": True,
            "on_collide": pickup_key,
        }
    }
}
