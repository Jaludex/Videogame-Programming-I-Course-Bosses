"""
ISPPV1 2023
Study Case: Super Martian (Platformer)

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the class FallState for player.
"""

import settings
from gale.timer import Timer
from src.states.entities.BaseEntityState import BaseEntityState


class FallState(BaseEntityState):
    def enter(self, coyote: bool = False) -> None:
        self.entity.change_animation("jump")
        self.coyote = coyote

        if self.coyote:
            def kill_coyote_time():
                self.coyote = False
            self.coyote_timer = Timer.after(settings.COYOTE_TIME, kill_coyote_time)

    def update(self, dt: float) -> None:
        if self.coyote and self.entity.jump_requested:
            self.entity.jump_requested = False
            self.coyote_timer.remove()
            self.entity.change_state("jump")
        else:
            self.entity.jump_requested = False

        if self.entity.move_direction != 0:
            self.entity.flipped = self.entity.move_direction < 0
        self.entity.vx = settings.PLAYER_SPEED * self.entity.move_direction

        if self.entity.on_ground:
            if self.entity.move_direction != 0:
                self.entity.change_state("walk")
            else:
                self.entity.change_state("idle")
