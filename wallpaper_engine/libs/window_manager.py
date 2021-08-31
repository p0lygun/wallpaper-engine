"""
todo
    make window manager class []
        follow :- https://www.codeproject.com/Articles/856020/Draw-Behind-Desktop-Icons-in-Windows-plus
        1. get Progman window handle []
        2. Send Message to Program Manager []
        3. Obtain Handle to Newly Created Window []
        4. set WorkerW window as the kivy's windows handle []

"""
import win32gui
import win32api

from kivy.app import App
from kivy.core.window import Window

from ..utils.logger import Logger


class WindowManager:
    def __init__(self):
        self.app = App.get_running_app()
        self.WorkerW = 0

    def set_as_wallpaper(self):
        """Set's kivy windows as wallpaper."""
        # get progman window handle
        progman = win32gui.FindWindowEx(0, 0, "Progman", None)
        # set message to progman
        win32gui.SendMessage(progman, int("0x052C", 16))
        # get correct WorkerW window
        # // 0x00010190 "" WorkerW
        # //   ...
        # //   0x000100EE "" SHELLDLL_DefView
        # //     0x000100F0 "FolderView" SysListView32
        # // 0x00100B8A "" WorkerW       <-- This is the WorkerW instance we are after!
        # // 0x000100EC "Program Manager"

        win32gui.EnumWindows(self.set_workerw, None)
        # set kivy window as the wallpaper
        kivy_window = win32gui.FindWindowEx(0, 0, 0, self.app.title)
        win32gui.SetParent(kivy_window, self.WorkerW)  # child , new parent
        # win32gui.SetWindowPos(kivy_window, self.WorkerW, 0, 0, 800, 800)

        # make window visible
        Window.show()

    def set_workerw(self, hwnd, extra):
        """Set the hwnd of correct WorkerW instance."""
        desktop_icons = win32gui.FindWindowEx(hwnd, 0, "SHELLDLL_DefView", None)
        if desktop_icons:
            self.WorkerW = win32gui.FindWindowEx(0, hwnd, 'WorkerW', None)
            Logger.debug(f"WorkerW hwnd {hex(self.WorkerW)}")



