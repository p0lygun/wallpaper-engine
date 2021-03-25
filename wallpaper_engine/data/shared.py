from ..libs.storage import Storage
import win32api
import pygame
global storage
global colors


def init():
    storage.store('pygame_font', pygame.font.Font('freesansbold.ttf', 15))


storage = Storage()
storage.store('screen_size', (win32api.GetSystemMetrics(0), win32api.GetSystemMetrics(1)))

colors = dict()

# primary colors
colors['white'] = [255, 255, 255, 255]
colors['black'] = [0, 0, 0, 255]
colors['red'] = [255, 0, 0, 255]
colors['green'] = [0, 255, 0, 255]
colors['blue'] = [0, 0, 255, 255]


# secondary colors
colors['dark_red'] = [138, 22, 22, 255]
