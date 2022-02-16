import os
import sys
from pathlib import Path
import win32api

from dotenv import load_dotenv
from kivy.config import Config
from loguru import logger
import stackprinter
import trio

load_dotenv()
logger.remove()
logger.add(
    sys.stdout,
    colorize=True,
    format="[ <lr>Wallpaper</> ]"
    "[<b><fg #3b3b3b>{level: ^8}</></>]"
    "[{name}.{function}:{line}]"
    "[ {message} ]",
    level=os.getenv("WE_DEBUG_LEVEL"),
)


async def launch_menu():
    command = f"{sys.executable} {Path(__file__).parent / 'libs' / 'menu.py'}"
    await trio.open_process(command)


stackprinter.set_excepthook(style="darkbg2")

if __name__ == "__main__":
    try:
        engine_debug = os.getenv("WE_ENGINE_DEBUG", False)
        logger.debug("Starting Menu")
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
            Config.set(
                "graphics", "width", f"{int(win32api.GetSystemMetrics(0) * 0.5)}"
            )
            Config.set(
                "graphics", "height", f"{int(win32api.GetSystemMetrics(1) * 0.5)}"
            )
        Config.write()
        from kivy.resources import resource_add_path

        from .libs.kivy_manager import WallpaperEngine
        from .utils.common import project_dir

        resource_add_path(str((project_dir / "libs" / "kv")))
        resource_add_path(str((project_dir / "wallpapers" / "kv")))

        logger.debug("Starting Wallpaper Engine App")
        app = WallpaperEngine(engine_debug=engine_debug)
        app.run()
        app.window_manager.reset_wallpaper()

    except KeyboardInterrupt:
        from kivy.app import App

        App.get_running_app().window_manager.reset_wallpaper()
        logger.info("Exiting...")
