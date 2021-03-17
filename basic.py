"""
see https://www.codeproject.com/articles/856020/draw-behind-desktop-icons-in-windows-plus for explanation
"""

import pygame
import math
from random import randint
import random
import PIL
from PIL import Image , ImageFilter
import sys

import os
import platform
import win32gui
if platform.system() != 'Windows':
    exit(1)


class Circle:

    global size

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.r = 5
        self.growing = True

    def grow(self):
        if self.growing:
            self.r += 1

    def edge(self):
        global size
        return self.x + self.r > size[0] or self.x - self.r < 0 or self.y + self.r > size[1] or self.y - self.r < 0


def add_circle():
    global clist
    global size
    x = random.randint(0, size[0])
    y = random.randint(0, size[1])
    valid = True
    for c in clist:
        dis = math.dist((x, y), (c.x, c.y))
        if dis < c.r + 5:
            valid = False
            break
    if valid:
        return Circle(x, y)
    else:
        False


def enum_windows():
    wlist = dict()
    win32gui.EnumWindows(
        lambda hwnd, result_list:
        wlist.update({hwnd: win32gui.GetWindowText(hwnd)}),
        None)
    return wlist


def find_progman() -> hex:
    """find the lowest instance of program manager returns window id is int"""
    wlist = enum_windows()
    for hwnd_id in reversed(list(wlist.keys())):
        if wlist[hwnd_id] == 'Program Manager':
            return hwnd_id


def find_workerw():
    """ returns the handle for workerw """

    """
    // Spy++ output
    // .....
    // 0x00010190 "" WorkerW
    //   ...
    //   0x000100EE "" SHELLDLL_DefView
    //     0x000100F0 "FolderView" SysListView32
    // 0x00100B8A "" WorkerW       <-- This is the WorkerW instance we are after!
    // 0x000100EC "Program Manager" Progman
    """

    wlist = enum_windows()
    for tophandle, topparamhandle in wlist.items():
        p = win32gui.FindWindowEx(
            tophandle,
            None,
            'SHELLDLL_DefView',
            None

        )

        if p != 0:
            '''Gets the WorkerW Window after the current one.'''
            return win32gui.FindWindowEx(
                0,
                tophandle,
                "WorkerW",
                None
            )


progman = find_progman()
# send message to Program manager
# int,int = SendMessageTimeout(hwnd, message , wparam , lparam , flags , timeout )
# for SendMessageTimeoutFlags check
# https://docs.microsoft.com/en-us/dotnet/api/microsoft.crm.unifiedservicedesk.dynamics.controls.nativemethods.sendmessagetimeoutflags?view=dynamics-usd-3

result = win32gui.SendMessageTimeout(
            int(progman),
            int(0x052C),
            0,
            0,
            0,
            1000
)
workerw = find_workerw()

# now the fun begins
# https://www.pygame.org/docs/ref/display.html#pygame.display.init


run = True
n = 1
if run:
    pygame.init()
    # Set up the drawing window
    screen = pygame.display.set_mode((0,0), flags=pygame.NOFRAME, vsync=1)
    # set it as a child to workerw
    win32gui.SetParent(pygame.display.get_wm_info()['window'], workerw)

    bg = (0, 0, 0)
    size = pygame.display.get_window_size()
    surface = pygame.Surface(size)

    running = True
    paused = False
    surface.fill(bg)
    changed = False

    # for i in range(100):
    clist = []
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    paused = not paused
        if not paused:
            newCircle = add_circle()
            if newCircle:
                clist.append(newCircle)
            surface.fill(bg)

            for circle in clist:
                if circle.growing:
                    if circle.edge():
                        circle.growing = False
                    else:
                        for other in clist:
                            if other != circle:
                                d = math.dist((circle.x, circle.y), (other.x, other.y))
                                if d < (circle.r + other.r):
                                    circle.growing = False
                    circle.grow()
                pygame.draw.circle(surface, (255, 255, 255), (circle.x, circle.y), circle.r, width=1)

            screen.blit(surface, (0, 0))
            pygame.display.flip()
            pygame.time.Clock().tick(30)
    size = screen.get_size()
    pygame.event.clear()

