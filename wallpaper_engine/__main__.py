from colorama import init

from .libs.kivy_manager import WallpaperEngine
from .utils.logger import Logger

if __name__ == '__main__':
    init()
    try:
        WallpaperEngine().run()
    except KeyboardInterrupt:
        Logger.info("Exiting...")
