import sys
from pathlib import Path
import win32api

from colorama import init
from kivy.config import Config
import trio

from .utils.logger import LoggerClass

Logger = LoggerClass(__name__)

command = f"{sys.executable} {Path(__file__).parent / 'libs' / 'menu.py'}"
Logger.debug(command)


async def launch_menu():
    await trio.open_process(command)


if __name__ == "__main__":
    try:
        engine_debug = False
        init()
        Logger.debug("Starting Menu")
        trio.run(launch_menu)
        Config.read(str(Path(__file__).parent / "data" / "kivy_backend_config"))
        Config.write()
        Config.set("kivy", "log_level", "warning")
        if not engine_debug:
            Config.set("graphics", "borderless", "1")
            Config.set("graphics", "resizable", "0")
            Config.set("graphics", "width", f"{win32api.GetSystemMetrics(0)}")
            Config.set("graphics", "height", f"{win32api.GetSystemMetrics(1)}")
        else:
            Config.set("graphics", "borderless", "0")
            Config.set("graphics", "resizable", "1")

        from kivy.resources import resource_add_path

        from .libs.kivy_manager import WallpaperEngine
        from .utils.common import project_dir

        resource_add_path(str((project_dir / "libs" / "kv")))
        resource_add_path(str((project_dir / "wallpapers" / "kv")))

        Logger.debug("Starting Wallpaper Engine App")
        app = WallpaperEngine(engine_debug=engine_debug)
        app.run()
        app.window_manager.reset_wallpaper()

    except KeyboardInterrupt:
        from kivy.app import App

        App.get_running_app().window_manager.reset_wallpaper()
        Logger.info("Exiting...")
