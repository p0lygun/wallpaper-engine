import math
import random
import copy
import pygame
import pygame.gfxdraw

from ..data.shared import colors,storage
from ..libs.pygame_manager import Screen, get_size


class Circle:
    def __init__(self, x, y, color=None):
        if color is None:
            color = [255, 255, 255, 255]
        self.x = x
        self.y = y
        self.r = 5
        self.stooped_time = 0
        self.color = pygame.Color(color)
        self.remove = False
        self.growing = True

    def grow(self):
        if self.growing:
            self.r += 1

    def edge(self):
        return self.x + self.r > get_size()[0] or self.x - self.r < 0 or self.y + self.r > get_size()[
            1] or self.y - self.r < 0


class Wallpaper:
    def __init__(self):
        self.window = Screen()
        self.clist = []
        self.themes = ["white", "rgb"]
        self.theme = None
        self.circle_color = []

        self.region_size = int((get_size())[0] // 3)
        self.left_color = pygame.Color([115, 255, 0, 255])
        self.center_color = pygame.Color([51, 82, 255, 255])
        self.right_color = pygame.Color([255, 51, 143, 255])
        self.frame_count = 0
        self.de_alpha = 1

    def setup(self, theme=None):
        self.window.tick(tick_rate=80)
        if theme in self.themes:
            self.theme = theme
        self.window.bg = colors['black']
        self.circle_color = colors['blue']

    def update(self):

        new_circle = self.add_circle()
        if new_circle:
            self.clist.append(new_circle)

        for circle in self.clist:
            if circle.growing:
                if circle.edge():
                    circle.growing = False
                else:
                    for other in self.clist:
                        if other != circle:
                            d = math.dist((circle.x, circle.y), (other.x, other.y))
                            if d < (circle.r + other.r):
                                circle.growing = False

                try:
                    if circle.x < self.region_size:
                        circle.color = self.left_color.lerp(self.center_color, circle.x / self.region_size)
                    elif circle.x < self.region_size * 2:
                        circle.color = self.center_color.lerp(self.right_color, circle.x / (self.region_size * 2))
                    else:
                        circle.color = self.right_color.lerp(self.left_color, circle.x / (self.region_size * 3))
                except ValueError:
                    raise
                circle.grow()
            else:
                if circle.color.a > self.de_alpha*2:
                    circle.color.a -= self.de_alpha
                else:
                    self.clist.remove(circle)
            # pygame.draw.circle(self.window.surface, circle.color, (circle.x, circle.y), circle.r, width=1)
            pygame.gfxdraw.aaellipse(self.window.surface, circle.x, circle.y, circle.r, circle.r, circle.color)

        self.window.update()

    def add_circle(self):
        x = random.randint(0, get_size()[0])
        y = random.randint(0, get_size()[1])
        valid = True
        for c in self.clist:
            dis = math.dist((x, y), (c.x, c.y))
            if dis < c.r + 5:
                valid = False
                break
        if valid:
            return Circle(x, y, self.circle_color.copy())
        else:
            return False
