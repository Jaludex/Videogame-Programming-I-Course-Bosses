from typing import Any

import pygame

from gale.state import BaseState

import settings
from src.gui.Menu import Menu
from src.gui.CharStatsPanel import CharStatsPanel
from src.entity.Character import Character


class CheckMenuState(BaseState):
    def enter(self, play_state: Any) -> None:
        self.play_state = play_state

        items = [(char.name, self.select_actions) for char in self.play_state.world.party.characters.values()]
        items.append(("Exit", self.close))

        self.menu = Menu(
            5,
            5,
            110,
            72,
            items=items,
            font=settings.FONTS["small"],
        )

        self.selected_idx = 0

        self.stats_panel = CharStatsPanel(
            self.menu.panel.x + self.menu.panel.width + 5,
            5,
            100,
            190,
            None,  
        )

        self.update_character_info()

    def close(self) -> None:
        self.state_machine.pop()

    def select_actions(self):
        from src.states.game.WorldSelectActionState import WorldSelectActionState
        if self.selected_idx in range(0, 4):
            char = self.play_state.world.party.characters[self.selected_idx]
            has_character_action = any(action.get("target_type") == "character" for action in char.actions)

            if has_character_action:
                self.state_machine.push(WorldSelectActionState(self.state_machine), play_state=self.play_state, entity=char, on_action_selected=self.update_character_info)
        
    def update_character_info(self):
        if self.selected_idx in range(0, 4):
            new_char = self.play_state.world.party.characters[self.selected_idx]
        else:
            new_char = None
        
        self.stats_panel.set_character(new_char)

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

        if input_id in ["move_up", "move_down"]:
            self.selected_idx = self.menu.list_view.selected_index

            self.update_character_info()

    def render(self, surface: pygame.Surface) -> None:
        self.menu.render(surface)
        self.stats_panel.render(surface)
