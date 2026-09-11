"""
ISPPV1 2023
Study Case: Ultimate Fantasy (RPG)

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains wrap_text, a small greedy word-wrap helper shared by
every screen that renders a paragraph too long for one line (see
TheEndState, ConfirmState) -- a single unbroken font.render(text, ...)
has no notion of the surface it'll end up on, so a long enough paragraph
would otherwise run straight off the screen's edge.
"""

from typing import List

import pygame


def wrap_text(font: pygame.font.Font, text: str, max_width: float) -> List[str]:
    """Greedily packs words into as few lines as possible, each rendering
    no wider than max_width."""
    words = text.split(" ")
    lines: List[str] = []
    current = ""

    for word in words:
        candidate = f"{current} {word}".strip()

        if current and font.size(candidate)[0] > max_width:
            lines.append(current)
            current = word
        else:
            current = candidate

    if current:
        lines.append(current)

    return lines
