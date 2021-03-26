import math
import random

import pygame

from ..libs.pygame_manager import Screen, get_size


class Wallpaper:

    def __init__(self):
        self.window = Screen()
        self.angle = 0.0
        self.rects = []
        self.pad = 10
        self.colors = [(42, 157, 143, 100), (233, 196, 106)]
        self.rects = []
        self.dh = 0
        self.bg = (38, 70, 83)
        self.setup_once = False
        self.themes = ["default"]

    def setup(self, theme=None):
        if self.window:
            self.window.bg = self.bg
            self.rects.clear()
            self.window.tick(tick_rate=60)
            for i in range(
                    int((self.pad / 100) * get_size()[0]),
                    int(((100 - self.pad) / 100) * get_size()[0]),
                    15
            ):
                center = (i, int(get_size()[1] // 2) - 50)
                self.rects.append(
                    (pygame.Rect(*center, 10, 100),
                     random.uniform(0, 2 * math.pi),
                     random.choice(self.colors))
                )

    def update(self):
        if not self.setup_once:
            self.setup()
            self.setup_once = True
        if self.angle % 2 * math.pi == 0:
            self.angle = 0
            self.setup()

        for rect in self.rects:
            self.dh = math.sin(self.angle + rect[1])
            pygame.draw.rect(self.window.surface, rect[2], rect[0].inflate(0, self.dh * 100))
        self.angle += 0.1
        self.window.update()
