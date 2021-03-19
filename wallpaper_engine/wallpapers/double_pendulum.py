import math
from typing import List, Union, Tuple

import pygame
import pygame.gfxdraw

from ..libs.pygame_manager import Screen, get_size
from ..data.shared import colors
# from wallpaper_project.wallpaper_engine.data.shared import colors


def diff(num1, num2):
    return num1 - num2


class Wallpaper:

    def __init__(self):
        self.window = Screen()

        self.origin = (get_size()[0] // 2, int(0.1 * get_size()[1]))
        self.angle = [0.0, 0.0]
        self.length = [int(0.3 * get_size()[1]), int(0.3 * get_size()[1])]
        self.mass = [5, 5]
        self.v = [0, 0]
        self.g = 1
        self.acc = [0, 0]
        self.resistance = 1

        self.bg = (38, 70, 83)
        self.alpha = 150
        self.colors = [(42, 157, 143, self.alpha), (233, 196, 106, self.alpha)]
        self.tracer_color = colors['blue']

        self.points = []
        self.chasing = False

        self.setup_once = False

    def setup(self):
        self.angle = [math.pi / 2, 0]
        self.window.tick(tick_rate=60)

    def update(self):
        # angular acceleration for bob 1
        num1 = - self.g * (2 * self.mass[0] + self.mass[1]) * math.sin(self.angle[0])
        num2 = -self.mass[1] * self.g * math.sin(diff(self.angle[0], 2 * self.angle[1]))
        num3 = - 2 * math.sin(diff(self.angle[0], self.angle[1])) * self.mass[1]
        num4 = pow(self.v[1], 2) * self.length[1] + pow(self.v[0], 2) * self.length[0] * math.cos(diff(
            self.angle[0], self.angle[1])
        )

        den = (2 * self.mass[0] + self.mass[1] - (self.mass[1] * math.cos(2 * self.angle[0] - 2 * self.angle[1])))

        self.acc[0] = (num1 + num2 + num3 * num4) / (den * self.length[0])

        # angular acceleration for bob 2
        num1 = 2 * math.sin(diff(*self.angle))
        num2 = pow(self.v[0], 2) * self.length[0] * sum(self.mass)
        num3 = self.g * (sum(self.mass)) * math.cos(self.angle[0])
        num4 = pow(self.v[1], 2) * self.length[1] * self.mass[1] * math.cos(diff(*self.angle))

        self.acc[1] = (num1 * (num2 + num3 + num4)) / (den * self.length[1])

        x1 = self.length[0] * math.sin(self.angle[0]) + self.origin[0]
        y1 = self.length[0] * math.cos(self.angle[0]) + self.origin[1]

        x2 = x1 + self.length[1] * math.sin(self.angle[1])
        y2 = y1 + self.length[1] * math.cos(self.angle[1])

        self.v[0] += self.acc[0]
        self.v[1] += self.acc[1]

        self.angle[0] += self.v[0]
        self.angle[1] += self.v[1]

        self.v[0] *= self.resistance
        self.v[1] *= self.resistance


        # drawing part

        x1 = int(x1)
        y1 = int(y1)

        x2 = int(x2)
        y2 = int(y2)

        if self.chasing:
            if len(self.points) > 256:
                self.points = self.points[1:]

        if not ((x1, y1), (x2, y2)) in self.points:
            self.points.append(((x1, y1), (x2, y2)))

        pairs = [self.points[i:i+2] for i in range(len(self.points))]

        for index, points in enumerate(pairs):
            if len(self.points) > 255 and self.chasing:
                self.tracer_color[-1] = index % 255
            if len(points) == 1:
                # noinspection PyTypeChecker
                pygame.gfxdraw.pixel(self.window.surface, *points[0][1], self.tracer_color)
            else:
                # noinspection PyTypeChecker
                pygame.gfxdraw.line(self.window.surface, *points[0][1], *points[1][1], self.tracer_color)

        # layering

        # second Pendulum
        pygame.gfxdraw.line(self.window.surface, x1, y1, x2, y2, self.colors[1])
        pygame.gfxdraw.filled_circle(self.window.surface, x2, y2, 5*self.mass[1], self.colors[0])

        # first Pendulum
        # noinspection PyTypeChecker
        pygame.gfxdraw.line(self.window.surface, *self.origin, x1, y1, self.colors[1])
        pygame.gfxdraw.filled_circle(self.window.surface, x1, y1, 5*self.mass[0], self.colors[0])

        self.window.update()
