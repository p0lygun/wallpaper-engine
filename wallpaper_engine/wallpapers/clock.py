from datetime import datetime
from ..libs.pygame_manager import get_size, Screen
from ..data.shared import colors, storage
import pygame.gfxdraw
import numpy as np
import math


def remove_holes(surface, background=(0, 0, 0)):
    """
    Removes holes caused by aliasing.

    The function locates pixels of color 'background' that are surrounded by pixels of different colors and set them to
    the average of their neighbours. Won't fix pixels with 2 or less adjacent pixels.

    Args:
        surface (pygame.Surface): the pygame.Surface to anti-aliasing.
        background (3 element list or tuple): the color of the holes.

    Returns:
        anti-aliased pygame.Surface.
    """
    width, height = surface.get_size()
    array = pygame.surfarray.array3d(surface)
    contains_background = (array == background).all(axis=2)

    neighbours = (0, 1), (0, -1), (1, 0), (-1, 0)

    for row in range(1, height - 1):
        for col in range(1, width - 1):
            if contains_background[col, row]:
                average = np.zeros(shape=(1, 3), dtype=np.uint16)
                elements = 0
                for y, x in neighbours:
                    if not contains_background[col + x, row + y]:
                        elements += 1
                        average += array[col + x, row + y]
                    if elements > 2:  # Only apply average if more than 2 neighbours is not of background color.
                        array[col, row] = average // elements

    return pygame.surfarray.make_surface(array)


class Wallpaper:
    def __init__(self):

        self.base_length = int(storage.get('screen_size')[0] * 0.1)
        self.s_arm_length = 35
        surface_size = 2*(self.base_length+self.s_arm_length)   
        screen_size = storage.get("screen_size")
        surface_cords = int((screen_size[0] // 2) - (surface_size // 2)), int(
            (screen_size[1] // 2) - (surface_size // 2))

        self.window = Screen(surface_size=(surface_size, surface_size), surface_cords=surface_cords)
        self.time = None
        self.h_arm_color = [0, 129, 167, 175]
        self.m_arm_color = [253, 252, 220, 175]
        self.s_arm_color = [240, 113, 103, 175]

        self.h_arm_length = 5
        self.m_arm_length = 20

        self.origin = int(surface_size // 2), int(surface_size // 2)

        self.themes = ["normal"]
        self.theme = None

    def setup(self, theme):
        if theme is None:
            self.theme = "normal"
        elif theme in self.themes:
            self.theme = theme
        else:
            raise ValueError(f"Invalid Theme available themes are {self.themes}")
        self.time = datetime.now()
        self.window.tick(tick_rate=60)

    def update(self):
        if self.time:
            self.time = datetime.now()
            s_arm_angle = int(self.time.second * 6.0) - 90
            m_arm_angle = int(self.time.minute * 6.0) - 90
            h_arm_angle = int(self.time.hour * 30) - 90
            self.window.reset_surface()

            for i in range(10):
                pygame.gfxdraw.arc(self.window.surface, self.origin[0], self.origin[1],
                                   self.base_length + self.s_arm_length - i, -90,
                                   s_arm_angle,
                                   self.s_arm_color)

                pygame.gfxdraw.arc(self.window.surface, self.origin[0], self.origin[1],
                                   self.base_length + self.m_arm_length - i, -90, m_arm_angle,
                                   self.m_arm_color)

                pygame.gfxdraw.arc(self.window.surface, self.origin[0], self.origin[1],
                                   self.base_length + self.h_arm_length - i, -90, h_arm_angle,
                                   self.h_arm_color)

            self.window.surface = remove_holes(self.window.surface)
            self.window.update()
