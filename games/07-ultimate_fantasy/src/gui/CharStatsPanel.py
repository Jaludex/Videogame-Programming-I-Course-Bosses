import math
import pygame

from gale.ui.panel import Panel as GalePanel
from gale.ui.progress_bar import ProgressBar

import settings
from src.entity.Character import Character
from src.gui.theme import BAR_THEME


class CharStatsPanel(GalePanel):
    def __init__(
        self, 
        x: float, 
        y: float, 
        width: float, 
        height: float, 
        character: Character
    ) -> None:
        super().__init__(x, y, width, height)
        self.character = character

    def set_character(self, character: Character) -> None:
        self.character = character

    def render(self, surface: pygame.Surface) -> None:
        if not self.visible or self.character is None:
            return
        
        pygame.draw.rect(surface, (255, 255, 255), self.rect, border_radius=3)
        inner = pygame.Rect(
            int(self.x) + 2, int(self.y) + 2, int(self.width) - 4, int(self.height) - 4
        )
        pygame.draw.rect(surface, (56, 56, 56), inner, border_radius=3)

        left_margin = int(self.x) + 12
        current_y = int(self.y) + 12

        if self.character.current_animation is not None:
            frame_rect = self.character.current_animation.get_current_frame()
            texture = settings.TEXTURES[self.character.texture]
            surface.blit(texture, (left_margin, current_y), frame_rect)
            
            bar_width = math.floor(frame_rect.width * 1.5)
            bar_x = left_margin - (bar_width - frame_rect.width) / 2
            bar_y = current_y + frame_rect.height + 6

            hp_bar = ProgressBar(
                bar_x,
                bar_y,
                bar_width,
                3,
                value=self.character.current_hp,
                max_value=self.character.hp,
                color=pygame.Color(189, 32, 32),
                theme=BAR_THEME,
            )
            hp_bar.render(surface)

            current_y = bar_y + 12

        font = settings.FONTS.get("small", settings.FONTS.get("medium"))
        text_color = (255, 255, 255)

        stats_lines = [
            f"{self.character.name}",
            f"LVL: {self.character.level}",
            f"HP: {self.character.current_hp} / {self.character.hp}",
            f"ATK: {self.character.attack}",
            f"DEF: {self.character.defense}",
            f"MAG: {self.character.magic}",
            f"EXP: {int(self.character.current_exp)} / {int(self.character.exp_to_level)}",
            f"TMR: {self.character.cooldown_time}",
        ]

        for line in stats_lines:
            text_surface = font.render(line, True, text_color)
            surface.blit(text_surface, (left_margin, current_y))
            current_y += text_surface.get_height() + 2

        current_y += 4  # Separación

        # 4. Renderizar lista de acciones del personaje
        has_character_action = False
        if hasattr(self.character, "actions") and self.character.actions:
            actions_header = font.render("Actions:", True, text_color)
            surface.blit(actions_header, (left_margin, current_y))
            current_y += actions_header.get_height() + 2

            for action in self.character.actions:
                action_name = action.get("name", "")
                target_type = action.get("target_type")

                if target_type == "character":
                    has_character_action = True

                text_surface = font.render(action_name, True, text_color)

                # Si la acción es para un enemigo, se renderiza con alfa reducida (semi-transparente)
                if target_type == "enemy":
                    text_surface.set_alpha(128)

                surface.blit(text_surface, (left_margin, current_y))
                current_y += text_surface.get_height() + 2

        # 5. Mostrar la indicación solo si el personaje tiene acciones ejecutables en un aliado
        if has_character_action:
            current_y += 4
            prompt_lines = [
                "PRESS ENTER TO",
                "SELECT ACTIONS"
            ]
            for line in prompt_lines:
                text_surface = font.render(line, True, text_color)
                surface.blit(text_surface, (left_margin, current_y))
                current_y += text_surface.get_height() + 2