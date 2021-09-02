import win32gui

from kivy.app import App
from kivy.core.window import Window

from ..utils.logger import LoggerClass

Logger = LoggerClass(__name__)


class WindowManager:
    def __init__(self):
        self.app = App.get_running_app()
        self.WorkerW = 0
        self.desktop_icons = 0

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
        win32gui.ShowWindow(self.WorkerW, 1)
        # set kivy window as the wallpaper
        kivy_window = win32gui.FindWindowEx(0, 0, 0, self.app.title)
        self.app.hwnd = self.WorkerW
        win32gui.SetParent(kivy_window, self.WorkerW)  # child , new parent
        Window.window_state = "visible"

    def reset_wallpaper(self):
        win32gui.EnumWindows(self.set_workerw, True)
        win32gui.ShowWindow(self.WorkerW, 0)
        win32gui.ShowWindow(self.WorkerW, 1)

    def set_workerw(self, hwnd, extra):
        """Set the hwnd of correct WorkerW instance."""
        self.desktop_icons = win32gui.FindWindowEx(hwnd, 0, "SHELLDLL_DefView", None)
        if self.desktop_icons:
            self.WorkerW = win32gui.FindWindowEx(0, hwnd, "WorkerW", None)
            if extra:
                Logger.debug(f"WorkerW hwnd {hex(self.WorkerW)}")
