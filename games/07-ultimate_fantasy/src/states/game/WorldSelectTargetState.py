from typing import Any, Callable, List

import pygame

from gale.state import BaseState

import settings
from src.gui.Panel import Panel


class WorldSelectTargetState(BaseState):
    def enter(
        self,
        play_state: Any,
        targets: List[Any],
        on_target_selected: Callable[[Any], None],
    ) -> None:
        self.play_state = play_state
        self.targets = list(targets)
        self.on_target_selected = on_target_selected

        panel_width = 190
        panel_height = 55
        panel_x = (settings.VIRTUAL_WIDTH - panel_width) / 2
        panel_y = settings.VIRTUAL_HEIGHT - panel_height - 10

        self.panel = Panel(panel_x, panel_y, panel_width, panel_height)

        self.current_selection = 0
        for i, target in enumerate(self.targets):
            if not target.dead:
                self.current_selection = i
                break

    def _next_alive(self) -> None:
        n = len(self.targets)
        for step in range(1, n + 1):
            i = (self.current_selection + step) % n
            if not self.targets[i].dead:
                self.current_selection = i
                return

    def _prev_alive(self) -> None:
        n = len(self.targets)
        for step in range(1, n + 1):
            i = (self.current_selection - step) % n
            if not self.targets[i].dead:
                self.current_selection = i
                return

    def update(self, dt: float) -> None:
        for target in self.targets:
            if target.current_animation is not None:
                target.current_animation.update(dt)

    def on_input(self, input_id: str, input_data: Any) -> None:
        if not input_data.pressed:
            return

        if input_id in ["move_left", "move_up"]:
            self._prev_alive()
        elif input_id in ["move_right", "move_down"]:
            self._next_alive()
        elif input_id == "enter":
            target = self.targets[self.current_selection]
            self.state_machine.pop()
            self.on_target_selected(target)

    def render(self, surface: pygame.Surface) -> None:
        self.panel.render(surface)

        num_targets = len(self.targets)
        if num_targets == 0:
            return

        slot_width = self.panel.width / num_targets
        font = settings.FONTS.get("small", settings.FONTS.get("medium"))

        for i, target in enumerate(self.targets):
            slot_center_x = self.panel.x + i * slot_width + slot_width / 2

            if target.current_animation is not None:
                frame_rect = target.current_animation.get_current_frame()
                
                name_surface = font.render(target.name or "", True, (255, 255, 255))

                total_height = frame_rect.height + 2 + name_surface.get_height()
                start_y = self.panel.y + (self.panel.height - total_height) / 2

                sprite_x = slot_center_x - frame_rect.width / 2
                sprite_y = start_y
                texture = settings.TEXTURES[target.texture]
                surface.blit(texture, (sprite_x, sprite_y), frame_rect)

                name_x = slot_center_x - name_surface.get_width() / 2
                name_y = sprite_y + frame_rect.height + 2
                surface.blit(name_surface, (name_x, name_y))

                if i == self.current_selection:
                    cursor_img = settings.TEXTURES["cursor-right"]
                    cursor_x = sprite_x - cursor_img.get_width() - 2
                    cursor_y = sprite_y + (frame_rect.height - cursor_img.get_height()) / 2
                    surface.blit(cursor_img, (cursor_x, cursor_y))