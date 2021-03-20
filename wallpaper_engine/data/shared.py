from ..libs.storage import Storage
import pygame
global storage
storage = Storage()
storage.store('pygame_font',pygame.font.Font('freesansbold.ttf', 15))
global colors
colors = dict()

colors['white'] = [255, 255, 255, 255]
colors['black'] = [0, 0, 0, 255]
colors['red'] = [255, 0, 0, 255]
colors['green'] = [0, 255, 0, 255]
colors['blue'] = [0, 0, 255, 255]

colors['dark_red'] = [138, 22, 22, 255]
