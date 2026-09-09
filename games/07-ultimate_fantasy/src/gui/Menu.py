"""
ISPPV1 2023
Study Case: Ultimate Fantasy (RPG)

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the class Menu: a Panel background plus a
gale.ui.ListView of (text, on_select) items, navigated with up/down and
confirmed with enter -- the composition gale.ui.ListView's own docstring
recommends ("build a menu as Container([Panel(...), ListView(...)])").
Adds the blip sound on navigate/confirm the original always played,
which ListView itself intentionally leaves up to the caller.
"""

from typing import List, Optional, Sequence, Tuple

import pygame

from gale.ui.cursor import Cursor
from gale.ui.list_view import ListView
from gale.ui.theme import Theme

import settings
from src.gui.Panel import Panel

Item = Tuple[str, "callable"]

# A theme whose hover/focus colors match the panel's own background, so the
# only visible "selected row" indicator is the cursor sprite -- exactly like
# the original, which never highlighted the row itself.
_MENU_THEME = Theme(
    background_color=pygame.Color(56, 56, 56),
    hover_color=pygame.Color(56, 56, 56),
    focus_color=pygame.Color(56, 56, 56),
    text_color=pygame.Color(255, 255, 255),
    border_width=0,
)


class Menu:
    def __init__(
        self,
        x: float,
        y: float,
        width: float,
        height: float,
        items: Sequence[Item],
        show_cursor: bool = True,
        font: Optional[pygame.font.Font] = None,
    ) -> None:
        self.panel = Panel(x, y, width, height)

        # A small, symmetric inset (leaves the visual center exactly where
        # it was) so ListView's selected-row highlight fill -- which spans
        # its full width/row-height -- never paints over (and erases) the
        # panel's own 2px border.
        self.list_view = ListView(
            x + 4,
            y + 3,
            width - 8,
            height - 6,
            items=items,
            font=font or settings.FONTS["medium"],
            cursor=None,
            theme=_MENU_THEME,
        )
        self.list_view.focused = True

        # The original positions its cursor at a fixed x (not relative to
        # the row/text, which is centered independently and can be far from
        # the panel's edge for a wide menu like SelectActionState's) --
        # ListView's own built-in cursor always draws 4px left of the row,
        # which is only reasonable for narrow menus, so it's drawn here
        # instead, matching Selection.lua's own
        # `max(width / 3, x - 8)` formula.
        self.cursor = Cursor(settings.TEXTURES["cursor-right"]) if show_cursor else None

    def update(self, dt: float) -> None:
        self.list_view.update(dt)

    def render(self, surface: pygame.Surface) -> None:
        self.panel.render(surface)
        self.list_view.render(surface)

        if self.cursor is not None and self.list_view.items:
            row_rect = self.list_view.row_rect(self.list_view.selected_index)
            cursor_x = max(self.panel.width / 3, self.panel.x - 8)
            self.cursor.render(surface, (cursor_x, row_rect.centery))

    def navigate(self, direction: Tuple[int, int]) -> None:
        if self.list_view.on_navigate(direction):
            settings.SOUNDS["blip"].stop()
            settings.SOUNDS["blip"].play()

    def confirm(self) -> None:
        if self.list_view.on_confirm():
            settings.SOUNDS["blip"].stop()
            settings.SOUNDS["blip"].play()
