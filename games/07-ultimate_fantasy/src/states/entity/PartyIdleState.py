"""
ISPPV1 2023
Study Case: Ultimate Fantasy (RPG)

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the class PartyIdleState.
"""

from src.states.entity.PartyBaseState import PartyBaseState


class PartyIdleState(PartyBaseState):
    def enter(self) -> None:
        for character in self.party.characters.values():
            character.change_animation(f"idle-{character.direction}")

        # A region transition or battle encounter forces the party idle and
        # then covers PlayState with fade/cutscene states for a while, which
        # don't handle movement input — so if a direction key was already
        # held when the transition started and gets released mid-fade, that
        # release event is lost and self.party.held would otherwise stay
        # stuck true, making the party walk on its own once control returns.
        for key in self.party.held:
            self.party.held[key] = False

    def update(self, dt: float) -> None:
        held = self.party.held

        if held["move_left"]:
            self.party.change_state("walk", direction="left")
        elif held["move_right"]:
            self.party.change_state("walk", direction="right")
        elif held["move_up"]:
            self.party.change_state("walk", direction="up")
        elif held["move_down"]:
            self.party.change_state("walk", direction="down")
