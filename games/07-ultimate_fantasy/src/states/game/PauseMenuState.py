"""
ISPPV1 2023
Study Case: Ultimate Fantasy (RPG)

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the class PauseMenuState: pushed on top of PlayState
(which keeps rendering, frozen, underneath it) when the player presses
the pause key. Offers Continue/Save/Load another/Quit -- the canonical
"menu over a paused game" use case StateStack was introduced for back in
Chapter 8. Loading another save or quitting first warns (via
ConfirmState) if the current game has progress since its last save (see
World.dirty), and proceeds however the player answers.
"""

from typing import Any

import pygame

from gale.save import SaveError, SaveManager
from gale.state import BaseState

import settings
from src.gui.Menu import Menu

UNSAVED_LOAD_WARNING = (
    "You have unsaved progress. Do you want to save the current game before loading another?"
)
UNSAVED_QUIT_WARNING = (
    "You have unsaved progress. Do you want to save the current game before quitting?"
)


class PauseMenuState(BaseState):
    def enter(self, play_state: Any) -> None:
        self.play_state = play_state

        self.menu = Menu(
            settings.VIRTUAL_WIDTH / 2 - 70,
            settings.VIRTUAL_HEIGHT / 2 - 48,
            140,
            96,
            items=[
                ("Continue", self.close),
                ("Save game", self._save),
                ("Load another game", self._load_another),
                ("Quit", self._quit),
            ],
            font=settings.FONTS["small"],
        )

    def close(self) -> None:
        self.state_machine.pop()


    def _save(self) -> None:
        from src.states.game.SlotSelectState import SlotSelectState

        self.state_machine.push(
            SlotSelectState(self.state_machine),
            mode="save",
            on_select=self._do_save,
            on_close=self._cancel_slot_select,
        )

    def _cancel_slot_select(self) -> None:
        self.state_machine.pop()

    def _do_save(self, slot: str) -> None:
        from src.states.game.ShowTextState import ShowTextState

        self.play_state.save_game(slot)
        self.state_machine.pop()  # SlotSelectState
        self.state_machine.pop()  # this PauseMenuState
        self.state_machine.push(
            ShowTextState(self.state_machine),
            color=(255, 255, 255),
            text="Game Saved",
            on_complete=lambda: None,
        )


    def _load_another(self) -> None:
        if self.play_state.world.dirty:
            from src.states.game.ConfirmState import ConfirmState

            self.state_machine.push(
                ConfirmState(self.state_machine),
                message=UNSAVED_LOAD_WARNING,
                on_yes=self._save_before_loading,
                on_no=self._show_load_slots,
            )
        else:
            self._show_load_slots()

    def _save_before_loading(self) -> None:
        from src.states.game.SlotSelectState import SlotSelectState

        self.state_machine.push(
            SlotSelectState(self.state_machine),
            mode="save",
            on_select=self._do_save_before_loading,
            on_close=self._cancel_slot_select,
        )

    def _do_save_before_loading(self, slot: str) -> None:
        self.play_state.save_game(slot)
        self.state_machine.pop()  # SlotSelectState
        self._show_load_slots()

    def _show_load_slots(self) -> None:
        from src.states.game.SlotSelectState import SlotSelectState

        self.state_machine.push(
            SlotSelectState(self.state_machine),
            mode="load",
            on_select=self._do_load,
            on_close=self._cancel_slot_select,
        )

    def _do_load(self, slot: str) -> None:
        from src.states.game.FadeInState import FadeInState
        from src.states.game.PlayState import PlayState

        try:
            save_data = SaveManager().load(slot)
        except SaveError:
            # Corrupted/unreadable: leave the paused game exactly as it was.
            return

        party_genders = {int(k): v for k, v in save_data["party"]["genders"].items()}

        def on_complete() -> None:
            # Whatever the discarded game's own region music was --
            # World.__init__ (for the fresh PlayState below) only ever
            # expects to be following StartState's "intro", not another
            # already-playing World, so it never stops these on its own.
            settings.stop_music("town")
            settings.stop_music("world")

            self.state_machine.pop()  # SlotSelectState
            self.state_machine.pop()  # this PauseMenuState
            self.state_machine.pop()  # the old, now-discarded PlayState
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

    def _quit(self) -> None:
        if self.play_state.world.dirty:
            from src.states.game.ConfirmState import ConfirmState

            self.state_machine.push(
                ConfirmState(self.state_machine),
                message=UNSAVED_QUIT_WARNING,
                on_yes=self._save_before_quitting,
                on_no=self._do_quit,
            )
        else:
            self._do_quit()

    def _save_before_quitting(self) -> None:
        from src.states.game.SlotSelectState import SlotSelectState

        self.state_machine.push(
            SlotSelectState(self.state_machine),
            mode="save",
            on_select=self._do_save_before_quitting,
            on_close=self._cancel_slot_select,
        )

    def _do_save_before_quitting(self, slot: str) -> None:
        self.play_state.save_game(slot)
        self._do_quit()

    def _do_quit(self) -> None:
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
