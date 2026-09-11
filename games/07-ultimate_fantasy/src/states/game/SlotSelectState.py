"""
ISPPV1 2023
Study Case: Ultimate Fantasy (RPG)

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the class SlotSelectState: a picker over the 3 cards
in settings.SAVE_SLOTS, shared by "Save game" and "Load game"
(PauseMenuState, StartState). mode="save" lets the player pick (and, if
occupied, overwrite after confirming) any slot; mode="load" only lets
them pick a slot that already has a save in it. Each card shows the
slot's stats (party names, average level, region, last-saved date) read
from SaveMetadata.extra (see PlayState.save_game) -- without loading (or
migrating) the full save, which is the whole reason PlayState tags that
metadata onto the save in the first place.
"""

import time
from typing import Any, Callable, List, Optional

import pygame

from gale.save import SaveError, SaveManager
from gale.state import BaseState
from gale.ui.cursor import Cursor

import settings
from src.gui.Panel import Panel
from src.text_utils import wrap_text

# Wide enough that even a full 4-name party ("Squall, Cloud, Kimahri,
# Sephiroth", the game's longest combination) fits on one line -- a card
# is only ever the width of one stacked column here, not squeezed between
# siblings, so there's no reason to cut it closer than that. The names
# line is still wrap_text'd (not just centered as one line and left to
# overflow) as a defensive fallback in case that ever stops being true.
CARD_WIDTH = 176
CARD_HEIGHT = 44
CARD_GAP = 6
CARD_PADDING = 6


class SlotSelectState(BaseState):
    def enter(
        self,
        mode: str,
        on_select: Callable[[str], None],
        on_close: Optional[Callable[[], None]] = None,
    ) -> None:
        self.mode = mode  # "save" or "load"
        self.on_select = on_select
        self.on_close = on_close or (lambda: None)
        self.selected_index = 0
        self._refresh_metadata()

        total_height = CARD_HEIGHT * len(settings.SAVE_SLOTS) + CARD_GAP * (
            len(settings.SAVE_SLOTS) - 1
        )
        self.x = (settings.VIRTUAL_WIDTH - CARD_WIDTH) / 2
        self.top = (settings.VIRTUAL_HEIGHT - total_height) / 2

        self.panels = [
            Panel(self.x, self.top + i * (CARD_HEIGHT + CARD_GAP), CARD_WIDTH, CARD_HEIGHT)
            for i in range(len(settings.SAVE_SLOTS))
        ]
        self.cursor = Cursor(settings.TEXTURES["cursor-right"])

    def _refresh_metadata(self) -> None:
        manager = SaveManager()
        self.metadata = []

        for slot in settings.SAVE_SLOTS:
            try:
                self.metadata.append(manager.read_metadata(slot))
            except SaveError:
                self.metadata.append(None)

    def _selected_slot(self) -> str:
        return settings.SAVE_SLOTS[self.selected_index]

    def _confirm(self) -> None:
        meta = self.metadata[self.selected_index]

        if self.mode == "load" and meta is None:
            # Nothing to load from an empty slot -- a plain "denied" blip,
            # same sound ListView/Menu already use for every other click.
            settings.SOUNDS["blip"].stop()
            settings.SOUNDS["blip"].play()
            return

        settings.SOUNDS["blip"].stop()
        settings.SOUNDS["blip"].play()

        if self.mode == "save" and meta is not None:
            from src.states.game.ConfirmState import ConfirmState

            slot = self._selected_slot()
            self.state_machine.push(
                ConfirmState(self.state_machine),
                message=f"Overwrite the save in slot {self.selected_index + 1}?",
                on_yes=lambda: self.on_select(slot),
                on_no=lambda: None,
            )
            return

        self.on_select(self._selected_slot())

    def on_input(self, input_id: str, input_data: Any) -> None:
        if not input_data.pressed:
            return

        if input_id == "move_up":
            self.selected_index = (self.selected_index - 1) % len(settings.SAVE_SLOTS)
        elif input_id == "move_down":
            self.selected_index = (self.selected_index + 1) % len(settings.SAVE_SLOTS)
        elif input_id == "enter":
            self._confirm()
        elif input_id == "pause":
            self.on_close()

    def render(self, surface: pygame.Surface) -> None:
        overlay = pygame.Surface((settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill((0, 0, 0))
        surface.blit(overlay, (0, 0))

        title_font = settings.FONTS["medium"]
        title_text = "Save game" if self.mode == "save" else "Load game"
        title = title_font.render(title_text, True, (255, 255, 255))
        title_rect = title.get_rect(center=(settings.VIRTUAL_WIDTH / 2, self.top - 14))
        surface.blit(title, title_rect)

        small = settings.FONTS["small"]

        for i, panel in enumerate(self.panels):
            panel.render(surface)
            self._render_card_text(surface, small, panel, self.metadata[i], i)

            if i == self.selected_index:
                self.cursor.render(surface, (panel.x - 8, panel.y + panel.height / 2))

        hint = small.render("Pause: cancel", True, (200, 200, 200))
        last_panel = self.panels[-1]
        hint_rect = hint.get_rect(
            center=(settings.VIRTUAL_WIDTH / 2, last_panel.y + last_panel.height + 14)
        )
        surface.blit(hint, hint_rect)

    def _render_card_text(
        self,
        surface: pygame.Surface,
        font: pygame.font.Font,
        panel: Panel,
        meta: Any,
        index: int,
    ) -> None:
        x = panel.x + CARD_PADDING
        y = panel.y + 4
        max_width = panel.width - CARD_PADDING * 2

        def draw_line(text: str, color=(255, 255, 255)) -> None:
            nonlocal y
            line = font.render(text, True, color)
            surface.blit(line, (x, y))
            y += line.get_height() + 1

        draw_line(f"Slot {index + 1}")

        if meta is None:
            draw_line("Empty", (150, 150, 150))
            return

        extra = meta.extra
        names: List[str] = extra.get("party_names", [])
        names_text = ", ".join(names) if names else "?"
        # Wrapped (not truncated): a card is meant to show who's in the
        # party, and cutting names off would defeat that -- see CARD_WIDTH
        # for why one line is still the common case regardless.
        for line in wrap_text(font, names_text, max_width):
            draw_line(line)

        draw_line(f"Level {extra.get('party_level', '?')} - {extra.get('region_label', '?')}")
        date_str = time.strftime("%d/%m/%Y %H:%M", time.localtime(meta.updated_at))
        draw_line(date_str, (200, 200, 200))
