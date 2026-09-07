from typing import List

import pygame

from gale.frames import generate_frames

def generate_arrow_frames() -> List[pygame.Rect]:
    frames: List[pygame.Rect] = []
    for i in range(0, 2):
        frames.append(pygame.Rect(0, i * 5, 16, 5))
        frames.append(pygame.Rect(i * 5, 11, 5, 16))

    return frames