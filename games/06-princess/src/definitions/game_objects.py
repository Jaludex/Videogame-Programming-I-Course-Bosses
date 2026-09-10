"""
ISPPV1 2023
Study Case: The Legend of the Princess (ARPG)

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the definition for game objects.
"""

from typing import Any, Dict

import settings


def _pickup_heart(player, obj) -> None:
    player.heal(2)
    settings.SOUNDS["heart-taken"].play()

GAME_OBJECT_DEFS: Dict[str, Dict[str, Any]] = {
    "switch": {
        "type": "switch",
        "texture": "switches",
        "frame": 2,
        "width": 16,
        "height": 16,
        "solid": False,
        "default_state": "unpressed",
        "states": {
            "unpressed": {"frame": 2},
            "pressed": {"frame": 1},
        },
    },
    "pot": {
        "type": "pot",
        "texture": "tiles",
        "frame": 16,
        "width": 16,
        "height": 16,
        "solid": True,
        "consumable": False,
        "default_state": "default",
        "takeable": True,
        "states": {
            "default": {"frame": 16},
        },
    },
    # Definition of heart as a consumable object type.
    "heart": {
        "type": "heart",
        "texture": "hearts",
        "frame": 5,
        "width": 16,
        "height": 16,
        "solid": False,
        "consumable": True,
        "default_state": "default",
        "states": {
            "default": {"frame": 5},
        },
        "on_consume": _pickup_heart,
    },
    "chest": {
        "type": "chest",
        "texture": "chest",
        "frame": 1,
        "width": 16,
        "height": 19,
        "solid": True,
        "default_state": "closed",
        "states": {
            "closed": {"frame": 1},
            "open": {"frame": 2},
        }
    },
    "arrow": {
        "type": "arrow",
        "texture": "arrows",
        "frame": 1,
        "width": 16,
        "height": 5,
        "solid": True,
        "default_state": "right",
        "states": {
            "right": {
                "frame": 1,
                "witdh": 16,
                "height": 5,
                },
            "up": {
                "frame": 2,
                "witdh": 5,
                "height": 16,
                },
            "left": {
                "frame": 3,
                "witdh": 16,
                "height": 5,
                },
            "down": {
                "frame": 4,
                "witdh": 5,
                "height": 16,
                },
        }
    },
    "bow": {
        "type": "bow",
        "texture": "bow",
        "frame": 1,
        "width": 16,
        "height": 16,
        "solid": False,
        "default_state": "default",
        "states": {
            "default": {"frame": 1}
        }
    },
    "fireball": {
        "type": "fireball",
        "texture": "fireball",
        "frame": 1,
        "width": 16,
        "height": 16,
        "solid": True,
        "default_state": "default",
        "states": {
            "default": {"frame": 1}
        },
    }
}
