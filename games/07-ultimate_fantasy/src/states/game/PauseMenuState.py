"""
ISPPV1 2023
Study Case: Ultimate Fantasy (RPG)

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the class PauseMenuState: pushed on top of PlayState
(which keeps rendering, frozen, underneath it) when the player presses
the pause key. Offers Continue/Save/Quit, the canonical "menu over a
paused game" use case StateStack was introduced for back in Chapter 8.
"""

from typing import Any

import pygame

from gale.state import BaseState

import settings
from src.gui.Menu import Menu


class PauseMenuState(BaseState):
    def enter(self, play_state: Any) -> None:
        self.play_state = play_state

        self.menu = Menu(
            settings.VIRTUAL_WIDTH / 2 - 60,
            settings.VIRTUAL_HEIGHT / 2 - 36,
            120,
            72,
            items=[
                ("Continuar", self.close),
                ("Guardar partida", self._save),
                ("Salir", self._quit),
            ],
            font=settings.FONTS["small"],
        )

    def close(self) -> None:
        self.state_machine.pop()

    def _save(self) -> None:
        from src.states.game.ShowTextState import ShowTextState

        self.play_state.save_game()
        self.state_machine.pop()
        self.state_machine.push(
            ShowTextState(self.state_machine),
            color=(255, 255, 255),
            text="partida guardada",
            on_complete=lambda: None,
        )

    def _quit(self) -> None:
        pygame.event.post(pygame.event.Event(pygame.QUIT))

    def update(self, dt: float) -> None:
        self.menu.update(dt)

    def on_input(self, input_id: str, input_data: Any) -> None:
        if not input_data.pressed:
            return

        if input_id == "move_up":
            self.menu.navigate((0, -1))
        elif input_id == "move_down":
            self.menu.navigate((0, 1))
        elif input_id == "enter":
            self.menu.confirm()

    def render(self, surface: pygame.Surface) -> None:
        self.menu.render(surface)
