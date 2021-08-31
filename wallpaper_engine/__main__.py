from colorama import init
import win32api

from kivy.config import Config

from .utils.logger import Logger


if __name__ == "__main__":
    init()
    Config.set("graphics", "borderless", "1")
    Config.set("graphics", "resizable", "0")
    Config.set("graphics", "width", f"{win32api.GetSystemMetrics(0)}")
    Config.set("graphics", "height", f"{win32api.GetSystemMetrics(1)}")

    try:
        from .libs.kivy_manager import WallpaperEngine

        WallpaperEngine().run()
    except KeyboardInterrupt:
        from kivy.app import App

        App.get_running_app().window_manager.reset_wallpaper()
        Logger.info("Exiting...")
