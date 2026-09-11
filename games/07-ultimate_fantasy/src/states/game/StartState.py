"""
ISPPV1 2023
Study Case: Ultimate Fantasy (RPG)

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the class StartState: the title screen. A "Nueva
partida"/"Cargar partida" Menu replaces the original's raw
Enter/"press C" key prompts -- "Cargar partida" opens the same
SlotSelectState/stat-card picker "Guardar partida" uses from the pause
menu (see PauseMenuState), instead of always resuming the single fixed
save slot the game used to have.
"""

from typing import Any

import pygame

from gale.state import BaseState

import settings
from src.gui.Menu import Menu


class StartState(BaseState):
    def enter(self) -> None:
        settings.play_music("intro")

        self.menu = Menu(
            settings.VIRTUAL_WIDTH / 2 - 70,
            settings.VIRTUAL_HEIGHT - 76,
            140,
            48,
            items=[
                ("New game", self._start_new_game),
                ("Load game", self._load_game),
            ],
            font=settings.FONTS["small"],
        )

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

    def _start_new_game(self) -> None:
        from src.states.game.FadeInState import FadeInState
        from src.states.game.FadeOutState import FadeOutState
        from src.states.game.SelectCharacterState import SelectCharacterState

        def on_complete() -> None:
            self.state_machine.pop()
            self.state_machine.push(
                SelectCharacterState(self.state_machine),
                character_index=0,
                selected="male",
                party={},
            )
            self.state_machine.push(
                FadeOutState(self.state_machine),
                color=(0, 0, 0),
                time=0.5,
                on_complete=lambda: None,
            )

        self.state_machine.push(
            FadeInState(self.state_machine),
            color=(0, 0, 0),
            time=1,
            on_complete=on_complete,
        )

    def _load_game(self) -> None:
        from src.states.game.SlotSelectState import SlotSelectState

        self.state_machine.push(
            SlotSelectState(self.state_machine),
            mode="load",
            on_select=self._do_load,
            on_close=self._close_slot_select,
        )

    def _close_slot_select(self) -> None:
        self.state_machine.pop()

    def _do_load(self, slot: str) -> None:
        from gale.save import SaveError, SaveManager
        from src.states.game.FadeInState import FadeInState
        from src.states.game.PlayState import PlayState

        try:
            save_data = SaveManager().load(slot)
        except SaveError:
            # Corrupted/unreadable: leave the slot picker open as-is.
            return

        party_genders = {int(k): v for k, v in save_data["party"]["genders"].items()}

        def on_complete() -> None:
            self.state_machine.pop()  # SlotSelectState
            self.state_machine.pop()  # this StartState
            self.state_machine.push(
                PlayState(self.state_machine),
                party_genders=party_genders,
                save_data=save_data,
            )

        self.state_machine.push(
            FadeInState(self.state_machine),
            color=(0, 0, 0),
            time=1,
            on_complete=on_complete,
        )

    def render(self, surface: pygame.Surface) -> None:
        surface.blit(
            pygame.transform.scale(
                settings.TEXTURES["background"],
                (settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT),
            ),
            (0, 0),
        )

        title_font = settings.FONTS["ff"]

        shadow = title_font.render("ULTIMATE FANTASY", True, (34, 34, 34))
        shadow_rect = shadow.get_rect(
            center=(settings.VIRTUAL_WIDTH / 2 + 2, settings.VIRTUAL_HEIGHT / 2 - 20 + 2)
        )
        surface.blit(shadow, shadow_rect)

        title = title_font.render("ULTIMATE FANTASY", True, (212, 175, 55))
        title_rect = title.get_rect(
            center=(settings.VIRTUAL_WIDTH / 2, settings.VIRTUAL_HEIGHT / 2 - 20)
        )
        surface.blit(title, title_rect)

        self.menu.render(surface)
