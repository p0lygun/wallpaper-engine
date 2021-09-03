import sys
from pathlib import Path
import win32api

from colorama import init
from kivy.config import Config
import trio

from .utils.logger import LoggerClass

Logger = LoggerClass(__name__)


async def launch_menu():
    command = f"{sys.executable} {Path(__file__).parent / 'libs' / 'menu.py'}"
    await trio.open_process(command)


if __name__ == "__main__":
    try:

        Logger.set_level(10)
        init()
        trio.run(launch_menu)
        Config.read((Path(__file__).parent / "data" / "kivy_backend_config").as_posix())
        Config.write()
        Config.set("graphics", "borderless", "1")
        Config.set("kivy", "log_level", "warning")
        Config.set("graphics", "resizable", "0")
        Config.set("graphics", "width", f"{win32api.GetSystemMetrics(0)}")
        Config.set("graphics", "height", f"{win32api.GetSystemMetrics(1)}")

        from .libs.kivy_manager import WallpaperEngine

        app = WallpaperEngine()
        app.run()
        app.window_manager.reset_wallpaper()

    except KeyboardInterrupt:
        from kivy.app import App

        App.get_running_app().window_manager.reset_wallpaper()
        Logger.info("Exiting...")
