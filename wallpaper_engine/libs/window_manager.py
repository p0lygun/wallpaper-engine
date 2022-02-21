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
        # windows that will not pause the wallpaper (a list of Class Name of the windows)
        self.excluded_windows = ["SunAwtFrame"]

    def init_data(self):
        self.kivy_window = win32gui.FindWindowEx(0, 0, 0, self.app.title)

    def set_as_wallpaper(self):
        """Set's kivy windows as wallpaper."""

        # make a new workerw window
        self._kill_workerw()
        self.spawn_workerw()

        win32gui.ShowWindow(self.WorkerW, 1)
        # set kivy window as the wallpaper
        win32gui.SetParent(self.kivy_window, self.WorkerW)  # child , new parent

    def reset_wallpaper(self):
        self._kill_workerw()

    def set_workerw(self, hwnd, extra):
        """Set the hwnd of correct WorkerW instance."""
        # get correct WorkerW window
        # // 0x00010190 "" WorkerW
        # //   ...
        # //   0x000100EE "" SHELLDLL_DefView
        # //     0x000100F0 "FolderView" SysListView32
        # // 0x00100B8A "" WorkerW       <-- This is the WorkerW instance we are after!
        # // 0x000100EC "Program Manager"
        self.desktop_icons = win32gui.FindWindowEx(hwnd, 0, "SHELLDLL_DefView", None)
        if self.desktop_icons:
            logger.debug(f"SHELLDLL_DefView found at {hex(self.desktop_icons)}")
            self.WorkerW = win32gui.FindWindowEx(0, hwnd, "WorkerW", None)
            if extra and self.WorkerW:
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
                        if (
                            self.app.engine_debug
                            and win32gui.GetClassName(hwnd) in self.excluded_windows
                        ):
                            pass
                        else:
                            if hwnd not in self.maximized_windows:
                                self.maximized_windows.append(hwnd)
                                if extra:
                                    logger.debug(
                                        f"Maximized Window "
                                        f"{win32gui.GetWindowText(hwnd)}, "
                                        f"{hex(hwnd)}, {window_placement}"
                                    )
                                self.last_maximized = hwnd
                            self.any_maximized = True

            else:
                if hwnd in self.maximized_windows:
                    self.maximized_windows.remove(hwnd)

        if not self.app.engine_debug:
            win32gui.EnumWindows(inner_check, True)

        return self.any_maximized

    def spawn_workerw(self):
        progman = win32gui.FindWindow("Progman", "Program Manager")
        # set message to progman
        logger.debug(f"Progman at {hex(progman)}")

        # all the messages below must be sent in the same order for a successfully workerw creation
        # this method :- https://www.codeproject.com/Articles/856020/Draw-Behind-Desktop-Icons-in-Windows-plus
        # no longer works on win 11
        # below is the only working way
        win32gui.SendMessageTimeout(progman, 0x052C, 0xD, 1, win32con.SMTO_NORMAL, 1000)
        win32gui.SendMessageTimeout(
            progman, win32con.WM_ERASEBKGND, 0, 0, win32con.SMTO_NORMAL, 1000
        )
        win32gui.SendMessageTimeout(
            progman, win32con.WM_ERASEBKGND, 0, 0, win32con.SMTO_NORMAL, 1000
        )
        win32gui.SendMessageTimeout(
            progman, win32con.WM_ERASEBKGND, 0, 0, win32con.SMTO_NORMAL, 1000
        )
        win32gui.SendMessageTimeout(progman, 0x052C, 0xD, 1, win32con.SMTO_NORMAL, 1000)
        win32gui.EnumWindows(self.set_workerw, True)

    def _kill_workerw(self):
        win32gui.EnumWindows(self.set_workerw, True)
        if self.WorkerW:
            win32gui.SendMessage(self.WorkerW, win32con.WM_CLOSE)


if __name__ == "__main__":
    wm = WindowManager()
    # wm.kill_workerw()
    wm.spawn_workerw()
