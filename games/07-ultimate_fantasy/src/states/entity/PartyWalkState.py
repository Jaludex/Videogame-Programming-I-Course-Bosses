"""
ISPPV1 2023
Study Case: Ultimate Fantasy (RPG)

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the class PartyWalkState: tile-by-tile party movement
(leader + trailing followers, "snake" formation), fence collision, region
edge/gate transitions, and tall-grass random encounter triggering.
"""

import random
from typing import List, Optional, Tuple

from gale.timer import Timer

import settings
from src.states.entity.PartyBaseState import PartyBaseState


class PartyWalkState(PartyBaseState):
    def enter(self, direction: str) -> None:
        self.direction = direction

        if not self._check_for_encounter():
            self._attempt_move()

    @staticmethod
    def _delta(direction: str) -> Tuple[int, int]:
        if direction == "left":
            return -1, 0
        elif direction == "right":
            return 1, 0
        elif direction == "up":
            return 0, -1
        else:
            return 0, 1

    def _check_for_encounter(self) -> bool:
        party = self.party
        leader = party.first_alive()

        if leader is None:
            return False

        dx, dy = self._delta(self.direction)
        to_x, to_y = leader.map_x + dx, leader.map_y + dy

        region = party.world.current_region()

        if not (1 <= to_x <= region.tile_width and 1 <= to_y <= region.tile_height):
            return False

        gid = region.tilemap.get_gid("grass", to_y - 1, to_x - 1)

        if gid != settings.TILE_IDS["tall-grass"]:
            return False

        if random.randint(1, 10) != 1:
            return False

        self._trigger_encounter()
        return True

    def _trigger_encounter(self) -> None:
        from src.states.game.BattleState import BattleState
        from src.states.game.FadeInState import FadeInState
        from src.states.game.FadeOutState import FadeOutState

        party = self.party
        stack = party.world.stack

        leader = party.first_alive()
        restore_x, restore_y = leader.map_x, leader.map_y
        restore_direction = leader.direction

        party.change_state("idle")
        settings.pause_music("world")
        settings.play_music("battle")

        def on_exit() -> None:
            settings.stop_music("battle")
            settings.resume_music("world")
            party.set_position(restore_x, restore_y, restore_direction)

        def on_fade_in_complete() -> None:
            stack.push(
                BattleState(stack),
                party=party,
                region=party.world.current_region_name,
                on_exit=on_exit,
            )
            stack.push(
                FadeOutState(stack),
                color=(255, 255, 255),
                time=1,
                on_complete=lambda: None,
            )

        stack.push(
            FadeInState(stack),
            color=(255, 255, 255),
            time=1,
            on_complete=on_fade_in_complete,
        )

    def _next_alive_ahead(self, order: List[int], i: int) -> Optional[int]:
        for j in reversed(order):
            if j < i and not self.party.characters[j].dead:
                return j

        return None

    def _attempt_move(self) -> None:
        party = self.party
        characters = party.characters
        order = sorted(characters.keys())
        first = party.first_alive_position()

        if first is None:
            return

        # Followers face toward whichever character is immediately ahead of
        # them in the chain, before any position actually changes.
        for i in reversed(order):
            if i <= first or characters[i].dead:
                continue

            j = self._next_alive_ahead(order, i)

            if j is None:
                continue

            follower, ahead = characters[i], characters[j]

            if follower.map_x < ahead.map_x:
                follower.direction = "right"
            elif follower.map_x > ahead.map_x:
                follower.direction = "left"
            elif follower.map_y < ahead.map_y:
                follower.direction = "down"
            elif follower.map_y > ahead.map_y:
                follower.direction = "up"

            follower.change_state("walk")

        leader = characters[first]
        leader.direction = self.direction
        leader.change_state("walk")

        dx, dy = self._delta(self.direction)
        to_x, to_y = leader.map_x + dx, leader.map_y + dy

        if to_x < 1:
            party.world.move("left")
            return
        if to_x > settings.TILE_WIDTH:
            party.world.move("right")
            return
        if to_y < 1:
            party.world.move("up")
            return
        if to_y > settings.TILE_HEIGHT:
            party.world.move("down")
            return

        region = party.world.current_region()
        if region.tilemap.get_gid("fence", to_y - 1, to_x - 1) != settings.TILE_IDS["empty"]:
            party.change_state("idle")
            return

        # Cascade positions from front to back (snake trailing): each
        # follower snaps to wherever the character ahead of it currently is.
        for i in reversed(order):
            if i <= first or characters[i].dead:
                continue

            j = self._next_alive_ahead(order, i)

            if j is None:
                continue

            characters[i].map_x = characters[j].map_x
            characters[i].map_y = characters[j].map_y

        leader.map_x, leader.map_y = to_x, to_y

        last_tween = None

        for character in characters.values():
            if character.dead:
                continue

            target_x = (character.map_x - 1) * settings.TILE_SIZE
            target_y = (
                character.map_y - 1
            ) * settings.TILE_SIZE - character.height / 2
            last_tween = Timer.tween(
                0.5, [(character, {"x": target_x, "y": target_y})]
            )

        if last_tween is not None:
            last_tween.finish(self._on_step_finished)

    def _on_step_finished(self) -> None:
        held = self.party.held

        if held["move_left"]:
            self.party.change_state("walk", direction="left")
        elif held["move_right"]:
            self.party.change_state("walk", direction="right")
        elif held["move_up"]:
            self.party.change_state("walk", direction="up")
        elif held["move_down"]:
            self.party.change_state("walk", direction="down")
        else:
            self.party.change_state("idle")
