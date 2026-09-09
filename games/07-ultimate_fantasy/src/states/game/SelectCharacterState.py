"""
ISPPV1 2023
Study Case: Ultimate Fantasy (RPG)

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the class SelectCharacterState: lets the player pick a
gender (male/female) for each of the NUM_CHARACTERS party slots in turn,
then hands the finished party off to PlayState.
"""

from typing import Any, Dict, Optional

import pygame

from gale.state import BaseState

import settings
from src.definitions.entity import DEFAULT_CHARACTER_FRAME, ENTITY_DEFS, ENTITY_HEIGHT, ENTITY_WIDTH, NUM_CHARACTERS

_WELCOME_TEXT = (
    "Welcome to the world of Ultimate Fantasy! There is a curse that has to "
    "be broken. To break the curse you have to defeat the Man-eater flower "
    "at the west from this town. Go north to gain experience with weak "
    "slimes, go south to face second level worms, go east for third level "
    "snakes, and finally, go west to deal with strong pumpkins and find the "
    "final boss. Good luck!"
)


class SelectCharacterState(BaseState):
    def enter(
        self,
        character_index: int = 0,
        selected: str = "male",
        party: Optional[Dict[int, str]] = None,
    ) -> None:
        self.character_index = character_index
        self.selected = selected
        self.character_type = ENTITY_DEFS["characters"][character_index]
        self.party = party if party is not None else {}

    def on_input(self, input_id: str, input_data: Any) -> None:
        if not input_data.pressed:
            return

        if input_id in ("move_left", "move_right"):
            self.selected = "female" if self.selected == "male" else "male"
        elif input_id == "enter":
            self._confirm()

    def _confirm(self) -> None:
        self.party[self.character_index] = self.selected

        if self.character_index < NUM_CHARACTERS - 1:
            self.state_machine.pop()
            self.state_machine.push(
                SelectCharacterState(self.state_machine),
                character_index=self.character_index + 1,
                selected=self.selected,
                party=self.party,
            )
            return

        settings.stop_music("intro")

        from src.states.game.DialogueState import DialogueState
        from src.states.game.FadeInState import FadeInState
        from src.states.game.FadeOutState import FadeOutState
        from src.states.game.PlayState import PlayState

        def on_complete() -> None:
            self.state_machine.pop()
            self.state_machine.push(
                PlayState(self.state_machine), party_genders=self.party
            )
            self.state_machine.push(
                DialogueState(self.state_machine), text=_WELCOME_TEXT
            )
            self.state_machine.push(
                FadeOutState(self.state_machine),
                color=(255, 255, 255),
                time=1,
                on_complete=lambda: None,
            )

        self.state_machine.push(
            FadeInState(self.state_machine),
            color=(255, 255, 255),
            time=1,
            on_complete=on_complete,
        )

    def render(self, surface: pygame.Surface) -> None:
        medium = settings.FONTS["medium"]
        type_text = medium.render(self.character_type["type"], True, (255, 255, 255))
        type_rect = type_text.get_rect(centerx=settings.VIRTUAL_WIDTH / 2, y=20)
        surface.blit(type_text, type_rect)

        small = settings.FONTS["small"]
        y = settings.VIRTUAL_HEIGHT / 2 - ENTITY_HEIGHT

        x_male = settings.VIRTUAL_WIDTH / 2 - ENTITY_WIDTH / 2 - 30
        self._render_option(surface, small, "male", x_male, y)

        x_female = settings.VIRTUAL_WIDTH / 2 - ENTITY_WIDTH / 2 + 30
        self._render_option(surface, small, "female", x_female, y)

    def _render_option(
        self, surface: pygame.Surface, font: pygame.font.Font, gender: str, x: float, y: float
    ) -> None:
        gender_def = self.character_type[gender]
        texture = gender_def["texture"]

        surface.blit(
            settings.TEXTURES[texture],
            (x, y),
            settings.frame(texture, DEFAULT_CHARACTER_FRAME),
        )

        name_text = font.render(gender_def["name"], True, (255, 255, 255))
        name_rect = name_text.get_rect(
            centerx=x + ENTITY_WIDTH / 2, y=y - 10
        )
        surface.blit(name_text, name_rect)

        if self.selected == gender:
            surface.blit(settings.TEXTURES["cursor-up"], (x, y + ENTITY_HEIGHT + 10))
