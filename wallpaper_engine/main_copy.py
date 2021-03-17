import win32gui
import pathlib
import importlib
import win32con
import os

any_maximized = False
found = False
active_window_class = None
workerw = None


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


def set_active_window_class(hwnd, ctx):
    global active_window_class
    global any_maximized
    global found
    if win32gui.IsWindowVisible(hwnd):
        if get_window_state(hwnd=hwnd) == win32con.SW_SHOWMAXIMIZED and not found:
            any_maximized = True
            found = True

        if win32gui.IsIconic(hwnd):
            if hwnd == win32gui.GetForegroundWindow():
                active_window_class = (hex(hwnd), win32gui.GetWindowText(hwnd), win32gui.GetClassName(hwnd))
    if not found:
        any_maximized = False

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


def start(wallpaper_name):
    global active_window_class
    global workerw
    global any_maximized
    global found
    if wallpaper_name not in (pathlib.Path(__file__) / 'wallpaper').glob('*.py') and wallpaper_name == "pygame_manager":
        print("Wallpaper Not Found")
        exit(-1)
    progman = find_progman()
    win32gui.SendMessageTimeout(
        int(progman),
        int(0x052C),
        0,
        0,
        0,
        1000
    )
    workerw = find_workerw()
    running = True
    wallpaper = importlib.import_module('.wallpapers.' + wallpaper_name, package='wallpaper_engine').Wallpaper()
    wallpaper.setup()
    focus_on_desktop = False

    while running:

        try:
            found = False
            win32gui.EnumWindows(set_active_window_class, None)
        except Exception as e:
            print(e)
            raise
        if not any_maximized:
            focus_on_desktop = True
        else:
            focus_on_desktop = False

        if focus_on_desktop:
            wallpaper.update()
