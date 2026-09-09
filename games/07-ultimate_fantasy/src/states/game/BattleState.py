"""
ISPPV1 2023
Study Case: Ultimate Fantasy (RPG)

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the class BattleState: builds the battle background
(procedurally, same as an overworld Region but sized BATTLE_WIDTH x
BATTLE_HEIGHT), spawns 3-5 random enemies for the current region (or,
10% of the time in the west region, a final-boss fight against the
Man-Eater Flower plus two regular west enemies), and kicks off the
opening dialogue -> BattleMenuState turn loop.
"""

import math
import random
from typing import Any, Callable, Optional

import pygame

from gale.state import BaseState, StateMachine
from gale.tilemap import TileMap

import settings
from src.definitions.entity import (
    BATTLE_HEIGHT,
    BATTLE_PADDLE,
    BATTLE_WIDTH,
    ENEMIES_POSITIONS,
    ENTITY_DEFS,
)
from src.entity.Enemy import Enemy
from src.gui.Panel import Panel
from src.states.entity.EnemyBattleState import EnemyBattleState

TILE_IDS = settings.TILE_IDS


class BattleState(BaseState):
    def enter(self, party: Any, region: str, on_exit: Callable[[], None]) -> None:
        self.party = party
        self.region = region
        self.on_exit = on_exit
        self.final_boss = False
        self.battle_started = False

        self.tilemap = TileMap(
            settings.TILE_SIZE, settings.TILE_SIZE, BATTLE_WIDTH, BATTLE_HEIGHT
        )
        self.tilemap.add_tileset(settings.TILESET)
        self._create_map()

        self.party.set_battle_positions()

        self.enemies = []
        self._create_enemies()

        self.bottom_panel = Panel(0, settings.VIRTUAL_HEIGHT - 64, settings.VIRTUAL_WIDTH, 64)

        self._create_bars()

    def exit(self) -> None:
        settings.stop_music("battle")
        self.on_exit()

    def _create_map(self) -> None:
        base = self.tilemap.add_layer("base")
        for y in range(1, BATTLE_HEIGHT + 1):
            for x in range(1, BATTLE_WIDTH + 1):
                base[y - 1][x - 1] = random.choice(TILE_IDS["grass"])

        grass = self.tilemap.add_layer("grass")
        for y in range(1, BATTLE_HEIGHT + 1):
            for x in range(1, BATTLE_WIDTH + 1):
                tile_id = TILE_IDS["tall-grass"] if random.random() < 0.3 else TILE_IDS["empty"]
                grass[y - 1][x - 1] = tile_id

    def _create_enemies(self) -> None:
        region_enemies = ENTITY_DEFS["enemies"][self.region]

        if self.region == "west" and random.randint(1, 10) == 1:
            self.final_boss = True
            defs = [ENTITY_DEFS["enemies"]["boss"]] + [
                random.choice(region_enemies) for _ in range(2)
            ]
            positions = ENEMIES_POSITIONS[3]
        else:
            num_enemies = random.randint(3, 5)
            defs = [random.choice(region_enemies) for _ in range(num_enemies)]
            positions = ENEMIES_POSITIONS[num_enemies]

        for enemy_def, position in zip(defs, positions):
            enemy = Enemy(
                {
                    "name": enemy_def.get("name", enemy_def["type"].capitalize()),
                    "texture": enemy_def["texture"],
                    "class": enemy_def["type"],
                    "level": enemy_def["level"],
                    "baseHP": enemy_def["baseHP"],
                    "baseAttack": enemy_def["baseAttack"],
                    "baseDefense": enemy_def["baseDefense"],
                    "baseMagic": enemy_def["baseMagic"],
                    "actions": enemy_def["actions"],
                    "direction": "left",
                    "map_x": position["x"],
                    "map_y": position["y"],
                    "width": enemy_def["width"],
                    "height": enemy_def["height"],
                    "animations": enemy_def["animations"],
                }
            )
            enemy.state_machine = StateMachine(
                {"battle": lambda sm, e=enemy: EnemyBattleState(e, sm)}
            )
            enemy.change_state("battle")
            self.enemies.append(enemy)

    def _create_bars(self) -> None:
        from gale.ui.progress_bar import ProgressBar

        from src.gui.theme import BAR_THEME

        for character in self.party.characters.values():
            if character.dead:
                continue

            width = math.floor(character.width * 1.5)
            character.energy_bar = ProgressBar(
                character.x - (width - character.width) / 2,
                character.y - 10,
                width,
                3,
                value=character.current_hp,
                max_value=character.hp,
                color=pygame.Color(189, 32, 32),
                theme=BAR_THEME,
            )
            character.exp_bar = ProgressBar(
                character.x - (width - character.width) / 2,
                character.y - 6,
                width,
                3,
                value=character.current_exp,
                max_value=character.exp_to_level,
                color=pygame.Color(32, 32, 189),
                theme=BAR_THEME,
            )

        for enemy in self.enemies:
            width = math.floor(enemy.width * 1.5)
            enemy.energy_bar = ProgressBar(
                enemy.x - (width - enemy.width) / 2,
                enemy.y - 10,
                width,
                3,
                value=enemy.current_hp,
                max_value=enemy.hp,
                color=pygame.Color(189, 32, 32),
                theme=BAR_THEME,
            )

    def update(self, dt: float) -> None:
        if not self.battle_started:
            self.battle_started = True
            self._trigger_starting_dialogue()

        for enemy in self.enemies:
            if not enemy.dead:
                enemy.update(dt)

    def _trigger_starting_dialogue(self) -> None:
        from src.states.game.BattleMenuState import BattleMenuState
        from src.states.game.BattleMessageState import BattleMessageState

        def show_go_message() -> None:
            names = ", ".join(
                c.name for c in self.party.characters.values() if not c.dead
            )
            boss_warning = (
                "The final boss is here, this is your opportunity to save the "
                "world! "
                if self.final_boss
                else ""
            )
            message = f"{boss_warning}Go, {names}!"
            self.state_machine.push(
                BattleMessageState(self.state_machine),
                battle_state=self,
                message=message,
                on_close=open_menu,
            )

        def open_menu() -> None:
            self.state_machine.push(BattleMenuState(self.state_machine), battle_state=self)

        self.state_machine.push(
            BattleMessageState(self.state_machine),
            battle_state=self,
            message="A wild creatures horde appeared!",
            on_close=show_go_message,
        )

    def render(self, surface: pygame.Surface) -> None:
        # gale.tilemap.TileMap has no built-in pixel offset (unlike this
        # game's old bespoke TileMap), so the same BATTLE_PADDLE shift is
        # reproduced with a subsurface instead -- pixel-for-pixel identical
        # to the previous (x - 1 + offset_x) * TILE_SIZE math.
        battle_area = surface.subsurface(
            pygame.Rect(
                BATTLE_PADDLE["x"] * settings.TILE_SIZE,
                BATTLE_PADDLE["y"] * settings.TILE_SIZE,
                BATTLE_WIDTH * settings.TILE_SIZE,
                BATTLE_HEIGHT * settings.TILE_SIZE,
            )
        )
        self.tilemap.render(battle_area)

        for enemy in self.enemies:
            if not enemy.dead:
                enemy.render(surface)
                enemy.energy_bar.render(surface)

        for character in self.party.characters.values():
            if not character.dead:
                character.render(surface)
                character.energy_bar.render(surface)
                character.exp_bar.render(surface)

        self.bottom_panel.render(surface)
