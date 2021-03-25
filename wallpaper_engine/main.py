import importlib
import logging
import pathlib
from functools import lru_cache

import win32api
import win32con
import win32gui

from .data.shared import init
from .data.shared import storage as global_storage
from .libs import pygame_manager
from .libs.storage import Storage

global logger

any_maximized = False
found = False
active_window_class = None
workerw = None
debug = global_storage.get("debug")
local_storage = Storage(local=True)


@lru_cache(None)
def clog(message: str):
    logger.debug(message)


def enum_windows():
    logger.debug(f'enum windows for finding progman')
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
    logger.debug("Finding workew...")
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
            workerw_handle = win32gui.FindWindowEx(
                0,
                tophandle,
                "WorkerW",
                None
            )
            logger.debug(f"Found workew... {hex(workerw_handle)}")
            return workerw_handle


def is_maximized(hwnd):
    if not win32gui.IsIconic(hwnd) and win32gui.IsWindowVisible(hwnd) and win32gui.GetClassName(
            hwnd) != "ApplicationFrameWindow":
        gwl_style = win32api.GetWindowLong(hwnd, win32con.GWL_STYLE)
        is_visible = gwl_style & win32con.WS_VISIBLE != 0
        is_minimized = gwl_style & win32con.WS_MINIMIZE != 0

        if is_visible and not is_minimized:
            if gwl_style & win32con.WS_MAXIMIZE != 0:
                return True, hwnd

    return False, 0


def any_maximized_window(hwnd, ctx):
    clog('In active')
    global active_window_class
    global any_maximized
    global found

    exceptions = []
    if global_storage.get('debug'):  # my code editor add yours classmate here find using lib\window_inspector.py
        exceptions.append("SunAwtFrame")

    if win32gui.GetClassName(hwnd) in exceptions:
        return

    # if visible
    # https://docs.microsoft.com/en-us/windows/win32/winmsg/window-styles

    gwl_style = None
    if any_maximized:
        if is_maximized(any_maximized)[0]:
            found = True
            return
        else:
            tmp = is_maximized(hwnd)
            if tmp[0]:
                any_maximized = tmp[1]
                found = True
                if any_maximized:
                    if local_storage.get('MaxWindow') == hwnd:
                        pass
                    else:
                        local_storage.store('MaxWindow', hwnd)
                        logger.debug(
                            f'found maximized window {hwnd}, {win32gui.GetClassName(hwnd)}, {win32gui.GetWindowText(hwnd)},')
    else:
        tmp = is_maximized(hwnd)
        if tmp[0]:
            any_maximized = tmp[1]
            found = True
            if any_maximized:
                if local_storage.get('MaxWindow') == hwnd:
                    pass
                else:
                    local_storage.store('MaxWindow', hwnd)
                    logger.debug(
                        f'found maximized window {hwnd}, {win32gui.GetClassName(hwnd)}, {win32gui.GetWindowText(hwnd)},')

    if win32gui.IsIconic(hwnd):
        if hwnd == win32gui.GetForegroundWindow():
            active_window_class = (hex(hwnd), win32gui.GetWindowText(hwnd), win32gui.GetClassName(hwnd))


def get_window_state(hwnd=None, class_name=None):
    """
        hwnd : int
        class_name : str

        returns
            win32con.SW_SHOWMAXIMIZED for maximized
            win32con.SW_SHOWNORMAL for normal
            win32con.SW_SHOWMINIMIZED for minimized
            0 if no window is found
    """

    window = 0
    if hwnd or class_name:
        if hwnd:
            class_name = win32gui.GetClassName(hwnd)
            window = win32gui.FindWindow(str(class_name), None)
        else:
            window = win32gui.FindWindow(str(class_name), None)

    if window:
        tup = win32gui.GetWindowPlacement(window)
        if tup[1] == win32con.SW_SHOWMAXIMIZED:
            return win32con.SW_SHOWMAXIMIZED

        elif tup[1] == win32con.SW_SHOWMINIMIZED:
            return win32con.SW_SHOWMINIMIZED

        elif tup[1] == win32con.SW_SHOWNORMAL:
            return win32con.SW_SHOWNORMAL
    return 0


def start(wallpaper_name, theme):
    global active_window_class
    global workerw
    global any_maximized
    global found
    global logger

    logger = logging.getLogger(global_storage.get('logger_name'))

    logger.debug(f"Starting main with wallpaper {wallpaper_name}, and theme {theme}")
    if wallpaper_name not in (pathlib.Path(__file__) / 'wallpaper').glob('*.py') and wallpaper_name == "pygame_manager":
        raise ValueError("Wallpaper Not Found")
    logger.debug("Finding progman")
    progman = find_progman()
    logger.debug(f"Found progman {progman} Sending Message....")
    win32gui.SendMessageTimeout(
        int(progman),
        int(0x052C),
        0,
        0,
        0,
        1000
    )
    logger.debug("Done")
    logger.debug("Finding Workerw")
    workerw = find_workerw()
    running = True

    wallpaper = importlib.import_module('.wallpapers.' + wallpaper_name, package='wallpaper_engine').Wallpaper()
    wallpaper.setup(theme=theme)

    # shared init for fonts
    init()
    logger.debug("initial start successful")

    while running:
        try:
            if not debug:
                found = False
                clog('Find any maximized window...')
                win32gui.EnumWindows(any_maximized_window, None)
        except Exception as e:
            print(e)
            raise
        if not found:
            focus_on_desktop = True
        else:
            focus_on_desktop = False
        global_storage.store('focus_on_desktop', focus_on_desktop)

        # pygame freeze
        # if pygame.events.get() is not called
        # windows thinks  its not accepting events
        if global_storage.get('debug'):
            clog("checking for events")
            pygame_manager.events()

        if focus_on_desktop:
            clog("calling updates")
            wallpaper.window.reset_screen()
            wallpaper.window.reset_surface()
            wallpaper.update()
