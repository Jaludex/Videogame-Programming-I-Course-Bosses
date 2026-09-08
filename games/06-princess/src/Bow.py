from gale.factory import Factory

from src.definitions.game_objects import GAME_OBJECT_DEFS

from src.GameObject import GameObject
from src.Projectile import Projectile

class Bow():
    def __init__(self):
        self.ammo_factory = Factory(GameObject)

    def fire(self, player, room):
        player.direction
        arrow = self.ammo_factory.create(player.x + (player.width // 2), player.y + (player.height // 2), {"definition": GAME_OBJECT_DEFS["arrow"]})
        arrow.state = player.direction

        room.projectiles.append(Projectile(arrow, player.direction))