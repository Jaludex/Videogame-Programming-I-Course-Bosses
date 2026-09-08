from typing import Any, Dict

import settings

from src.definitions.game_objects import GAME_OBJECT_DEFS
from src.Bow import Bow

def _get_basic_bow(player):
    player.bow = Bow()

PLAYER_ITEM_DEFS: Dict[str, Dict[str, Any]] = {
    "bow": {
        "action": _get_basic_bow,
        "display_object_def": GAME_OBJECT_DEFS["bow"]
    }
}
