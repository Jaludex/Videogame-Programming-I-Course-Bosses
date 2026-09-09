"""
ISPPV1 2023
Study Case: Ultimate Fantasy (RPG)

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the class TakeTurnState: drives one full round of
battle -- every living party member acts (in slot order), then every
living enemy acts (in list order, AI picking a uniformly random action
among its own, guaranteed to hit a living target), repeating round after
round until one side is wiped. Also handles the victory (EXP/level-up)
and defeat (game over) end-of-battle flows.
"""

import math
import random
from typing import Any

import pygame

from gale.state import BaseState
from gale.timer import Timer

import settings


class TakeTurnState(BaseState):
    def enter(self, battle_state: Any) -> None:
        self.battle_state = battle_state
        self.enemy_attacks_in_a_row = 0
        self._take_party_turn(0)

    def _party_keys(self):
        return sorted(self.battle_state.party.characters.keys())

    # -- party turns ---------------------------------------------------

    def _take_party_turn(self, index: int) -> None:
        keys = self._party_keys()

        if index >= len(keys):
            self._take_enemy_turn(0)
            return

        character = self.battle_state.party.characters[keys[index]]

        if character.dead:
            self._take_party_turn(index + 1)
            return

        from src.states.game.BattleMessageState import BattleMessageState

        self.state_machine.push(
            BattleMessageState(self.state_machine),
            battle_state=self.battle_state,
            message=f"Turn for {character.name}! Select an action.",
            on_close=lambda: self._prompt_action(character, index),
        )

    def _prompt_action(self, character: Any, index: int) -> None:
        from src.states.game.SelectActionState import SelectActionState

        def on_action_selected() -> None:
            if all(enemy.dead for enemy in self.battle_state.enemies):
                self._victory()
            else:
                self._take_party_turn(index + 1)

        self.state_machine.push(
            SelectActionState(self.state_machine),
            battle_state=self.battle_state,
            entity=character,
            on_action_selected=on_action_selected,
        )

    # -- enemy turns ----------------------------------------------------

    def _take_enemy_turn(self, index: int) -> None:
        enemies = self.battle_state.enemies

        if index >= len(enemies):
            self._take_party_turn(0)
            return

        enemy = enemies[index]

        if enemy.dead:
            self._take_enemy_turn(index + 1)
            return

        self.enemy_attacks_in_a_row += 1
        action = random.choice(enemy.actions)

        if action["target_type"] == "enemy":
            targets = list(self.battle_state.party.characters.values())
            target_label = "you"
        else:
            targets = self.battle_state.enemies
            target_label = "them"

        if action["require_target"]:
            alive = [target for target in targets if not target.dead]
            target = random.choice(alive)
            amount = action["func"](enemy, target, action.get("strength"))
            settings.SOUNDS[action["sound_effect"]].play()
            Timer.tween(0.5, [(target.energy_bar, {"value": target.current_hp})])
            message = f"{enemy.name} used {action['name']} for {amount} HP on {target.name}."
        else:
            alive_targets = [target for target in targets if not target.dead]
            amount = action["func"](enemy, alive_targets, action.get("strength"))
            settings.SOUNDS[action["sound_effect"]].play()

            for target in alive_targets:
                Timer.tween(0.5, [(target.energy_bar, {"value": target.current_hp})])

            message = (
                f"{enemy.name} used {action['name']} for {amount} HP on all of "
                f"{target_label}."
            )

        if all(character.dead for character in self.battle_state.party.characters.values()):
            self._faint()
            return

        from src.states.game.BattleMessageState import BattleMessageState

        def on_message_close() -> None:
            if (
                self.enemy_attacks_in_a_row < 3
                and enemy.klass == "boss"
                and random.randint(1, 3) == 1
            ):
                self._take_enemy_turn(index)
            else:
                self.enemy_attacks_in_a_row = 0
                self._take_enemy_turn(index + 1)

        self.state_machine.push(
            BattleMessageState(self.state_machine),
            battle_state=self.battle_state,
            message=message,
            on_close=on_message_close,
        )

    # -- victory / experience --------------------------------------------

    def _victory(self) -> None:
        settings.stop_music("battle")
        self._victory_channel = settings.SOUNDS["victory"].play(loops=-1)

        from src.states.game.BattleMessageState import BattleMessageState

        self.state_machine.push(
            BattleMessageState(self.state_machine),
            battle_state=self.battle_state,
            message="Victory!",
            on_close=self._start_exp,
        )

    def _start_exp(self) -> None:
        total_level = sum(enemy.level for enemy in self.battle_state.enemies)
        num_characters = len(self.battle_state.party.characters)
        opponent_level = total_level / num_characters
        self._inc_exp(0, opponent_level)

    def _inc_exp(self, index: int, opponent_level: float) -> None:
        keys = self._party_keys()

        if index >= len(keys):
            self._fade_out()
            return

        character = self.battle_state.party.characters[keys[index]]

        if character.dead:
            self._inc_exp(index + 1, opponent_level)
            return

        exp = math.ceil(
            (character.hpiv + character.attackiv + character.defenseiv + character.magiciv)
            * opponent_level
        )

        from src.states.game.BattleMessageState import BattleMessageState

        self.state_machine.push(
            BattleMessageState(self.state_machine),
            battle_state=self.battle_state,
            message=f"{character.name} earned {exp} experience points!",
            on_close=None,
            can_input=False,
        )
        Timer.after(1.5, lambda: self._apply_exp(character, exp, index, opponent_level))

    def _apply_exp(
        self, character: Any, exp: int, index: int, opponent_level: float
    ) -> None:
        settings.SOUNDS["exp"].play()
        new_value = min(character.current_exp + exp, character.exp_to_level)
        Timer.tween(
            0.5,
            [(character.exp_bar, {"value": new_value})],
            on_finish=lambda: self._exp_applied(character, exp, index, opponent_level),
        )

    def _exp_applied(
        self, character: Any, exp: int, index: int, opponent_level: float
    ) -> None:
        # Pops the can_input=False experience-gain message, which never
        # auto-closes on its own.
        self.state_machine.pop()
        character.current_exp += exp

        if character.current_exp >= character.exp_to_level:
            settings.SOUNDS["levelup"].play()
            character.current_exp -= character.exp_to_level
            last_level = character.level
            increases = character.level_up()
            hp_increase = increases[0]
            Timer.tween(
                0.5, [(character.energy_bar, {"value": character.current_hp - hp_increase})]
            )

            from src.states.game.BattleMessageState import BattleMessageState

            message = (
                f"Congratulations! {character.name} advanced from level "
                f"{last_level} level {character.level}!"
            )
            self.state_machine.push(
                BattleMessageState(self.state_machine),
                battle_state=self.battle_state,
                message=message,
                on_close=lambda: self._show_stats(character, increases, index, opponent_level),
            )
        else:
            self._inc_exp(index + 1, opponent_level)

    def _show_stats(self, character: Any, increases: Any, index: int, opponent_level: float) -> None:
        from src.states.game.StatsMenuState import StatsMenuState

        self.state_machine.push(
            StatsMenuState(self.state_machine),
            character=character,
            stats=increases,
            on_close=lambda: self._inc_exp(index + 1, opponent_level),
        )

    def _fade_out(self) -> None:
        if self._victory_channel is not None:
            self._victory_channel.stop()

        from src.states.game.FadeInState import FadeInState
        from src.states.game.FadeOutState import FadeOutState

        if self.battle_state.final_boss:

            def on_complete() -> None:
                settings.SOUNDS["the-end"].play()
                # Pops this lingering TakeTurnState, then the BattleState
                # underneath it (matches the original's "pop twice").
                self.state_machine.pop()
                self.state_machine.pop()

                from src.states.game.TheEndState import TheEndState

                self.state_machine.push(TheEndState(self.state_machine))
                self.state_machine.push(
                    FadeOutState(self.state_machine),
                    color=(0, 0, 0),
                    time=1,
                    on_complete=lambda: None,
                )

            self.state_machine.push(
                FadeInState(self.state_machine),
                color=(0, 0, 0),
                time=3,
                on_complete=on_complete,
            )
        else:

            def on_complete() -> None:
                # Pops this lingering TakeTurnState, then the BattleState
                # underneath it (BattleState.exit() stops battle music and
                # restores the party's overworld position/music).
                self.state_machine.pop()
                self.state_machine.pop()
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

    def _faint(self) -> None:
        settings.stop_music("battle")
        settings.SOUNDS["game-over"].play()

        from src.states.game.FadeInState import FadeInState

        def on_complete() -> None:
            from src.states.game.GameOverState import GameOverState

            self.state_machine.push(GameOverState(self.state_machine))

        self.state_machine.push(
            FadeInState(self.state_machine),
            color=(0, 0, 0),
            time=1,
            on_complete=on_complete,
        )

    _victory_channel = None
