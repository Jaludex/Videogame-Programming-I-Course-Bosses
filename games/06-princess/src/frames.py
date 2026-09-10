from typing import List

import pygame

from gale.animation import Animation
from gale.frames import generate_frames

def generate_arrow_frames() -> List[pygame.Rect]:
    frames: List[pygame.Rect] = []
    for i in range(0, 2):
        frames.append(pygame.Rect(0, i * 5, 16, 5))
        frames.append(pygame.Rect(i * 5, 10, 5, 16))

    return frames

def generate_dragon_boss_frames() ->list[pygame.Rect]:
    frames: List[pygame.Rect] = []
    # 40, 32.  9, 16  8, 12

    for y in [0, 32]:
        frames.append(pygame.Rect(0, y, 40, 32))
        frames.append(pygame.Rect(40, y, 39, 32))

        for x in [79, 87]:
            frames.append(pygame.Rect(x, y, 8, 16))
        x = 95

        frames.append(pygame.Rect(x, y, 8, 12))

    return frames