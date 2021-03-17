import importlib

import pygame
import win32gui


def get_size():
    return pygame.display.get_window_size()


class Screen:
    """pygame screen"""

    def __init__(self):
        self.screen_instance = None
        self.surface = None
        self.surface_pos = (0, 0)
        self._tick = 30
        self.bg = (0, 0, 0)

        self._init_screen()

    def _init_screen(self):
        pygame.init()
        workerw = importlib.import_module(".main_copy", package="wallpaper_engine").workerw
        self.screen_instance = pygame.display.set_mode((0, 0), flags=pygame.HIDDEN, vsync=1)
        win32gui.SetParent(pygame.display.get_wm_info()['window'], workerw)
        self.screen_instance = pygame.display.set_mode((0, 0), flags=pygame.SHOWN, vsync=1)

        self.surface = pygame.Surface(get_size())

    def fill(self, color):
        """color -> tuple (R, G, B)"""
        if type(color) == tuple:
            self.surface.fill(color)

    def tick(self, tick_rate=30):
        self._tick = tick_rate
        pygame.time.Clock().tick(self._tick)

    def reset_screen(self):
        self.screen_instance.fill(self.bg)

    def reset_surface(self):
        self.surface.fill(self.bg)

    def update(self):
        """Updates  screen"""
        self.screen_instance.blit(self.surface, (0, 0))
        pygame.display.flip()
