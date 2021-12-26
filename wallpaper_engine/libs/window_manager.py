import win32con
import win32gui
import win32api

from kivy.app import App
from loguru import logger


class WindowManager:
    def __init__(self):
        self.app = App.get_running_app()
        self.hidden = False
        self.WorkerW = 0
        self.desktop_icons = 0
        self.kivy_window = 0
        self.any_maximized = False
        self.maximized_windows = []

    def set_as_wallpaper(self):
        """Set's kivy windows as wallpaper."""
        # get progman window handle
        self.reset_wallpaper()
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
        self.kivy_window = win32gui.FindWindowEx(0, 0, 0, self.app.title)
        win32gui.SetParent(self.kivy_window, self.WorkerW)  # child , new parent

    def reset_wallpaper(self):
        win32gui.EnumWindows(self.set_workerw, False)
        win32gui.ShowWindow(self.WorkerW, 0)
        win32gui.ShowWindow(self.WorkerW, 1)

    def set_workerw(self, hwnd, extra):
        """Set the hwnd of correct WorkerW instance."""
        self.desktop_icons = win32gui.FindWindowEx(hwnd, 0, "SHELLDLL_DefView", None)
        if self.desktop_icons:
            self.WorkerW = win32gui.FindWindowEx(0, hwnd, "WorkerW", None)
            if extra:
                logger.debug(f"WorkerW hwnd {hex(self.WorkerW)}")

    def toggle_workerw_visibility(self):
        win32gui.EnumWindows(self.set_workerw, False)
        if self.hidden:
            win32gui.ShowWindow(self.WorkerW, 1)
            self.hidden = False
        else:
            win32gui.ShowWindow(self.WorkerW, 0)
            self.hidden = True

    def check_maximized_window(self) -> bool:
        """
        Checks for maximized window and retuns a bool
        """
        self.any_maximized = False

        def inner_check(hwnd, extra):
            window_placement = win32gui.GetWindowPlacement(hwnd)
            # GetWindowPlacement
            # returns (flags, showCmd, (minposX, minposY), (maxposX, maxposY), (normalposX, normalposY))
            if (
                win32gui.IsWindowVisible(hwnd)
                and window_placement[1] == win32con.SW_SHOWMAXIMIZED
            ):
                monitor_handle = win32api.MonitorFromWindow(
                    hwnd, win32con.MONITOR_DEFAULTTONULL
                )
                # check if the window is on primary window
                if monitor_handle == win32api.MonitorFromPoint(
                    (0, 0), win32con.MONITOR_DEFAULTTOPRIMARY
                ):
                    if win32gui.GetWindowText(hwnd) != "Settings":
                        if hwnd not in self.maximized_windows:
                            self.maximized_windows.append(hwnd)
                            if extra:
                                logger.debug(
                                    f"Maximized Window {win32gui.GetWindowText(hwnd)}, {hex(hwnd)}, {window_placement}"
                                )
                            self.last_maximized = hwnd
                        self.any_maximized = True
            else:
                if hwnd in self.maximized_windows:
                    self.maximized_windows.remove(hwnd)

        win32gui.EnumWindows(inner_check, True)

        return self.any_maximized


if __name__ == "__main__":
    wm = WindowManager()
    print(wm.check_maximized_window())
