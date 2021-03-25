import importlib
import logging
import os
import win32con
import pygame
import win32gui
from ..data.shared import storage as global_storage
logger = logging.getLogger(global_storage.get('logger_name'))


def get_size():
    return pygame.display.get_window_size()


def events():
    # pygame freezes without this as windows thinks its not taking any input
    if global_storage.get("debug"):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:

                quit(0)
    else:
        pygame.event.pump()

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
        workerw = importlib.import_module(".main", package="wallpaper_engine").workerw
        if global_storage.get('debug'):
            """if debug is true then don't attach the pygame to workERW instance"""
            size = 720
            self.screen_instance = pygame.display.set_mode((size,size), flags=pygame.SHOWN, vsync=1)

            # fix it to be topmost
            win32gui.SetWindowPos(
                pygame.display.get_wm_info()['window'],
                win32con.HWND_TOPMOST,
                0, 0, 0, 0,
                win32con.SWP_NOMOVE | win32con.SWP_NOSIZE
            )

        else:
            self.screen_instance = pygame.display.set_mode((0, 0), flags=pygame.HIDDEN, vsync=1)
            win32gui.SetParent(pygame.display.get_wm_info()['window'], workerw)
            self.screen_instance = pygame.display.set_mode((0, 0), flags=pygame.SHOWN, vsync=1)

        self.surface = pygame.Surface(get_size())

    def fill(self, color):
        """color -> tuple (R, G, B)"""
        if type(color) == tuple:
            self.surface.fill(color)

    def tick(self, tick_rate=None):
        if not self._tick:
            if tick_rate is None:
                self._tick = 30
            else:
                self._tick = tick_rate
        else:
            if tick_rate:
                self._tick = tick_rate
            else:
                pygame.time.Clock().tick(self._tick)
                return
        pygame.time.Clock().tick(self._tick)

    def reset_screen(self):
        self.screen_instance.fill(self.bg)

    def reset_surface(self):
        self.surface.fill(self.bg)

    def update(self):
        """Updates  screen"""
        self.tick()
        self.screen_instance.blit(self.surface, (0, 0))
        pygame.display.flip()

