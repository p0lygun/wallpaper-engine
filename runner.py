import logging
import pathlib
import sys
from random import choice
from wallpaper_engine.data.shared import storage

storage.store('logger_name', 'WE_LOGGER')
logger = logging.getLogger(storage.get('logger_name'))
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(filename)s - %(funcName)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

from wallpaper_engine import __main__

if __name__ == '__main__':
    available_wallpapers = [i.stem for i in (pathlib.Path.cwd() / "wallpaper_engine" / "wallpapers").glob("*.py") if
                            i.stem != "__init__"]
    print(available_wallpapers)
    wallpaper = None
    theme = None
    storage.store('debug', False)
    for arg in sys.argv[1:]:
        if arg == "--debug":
            storage.store('debug', True)
            logger.debug(f"got args {sys.argv[1:]}")
        else:
            split_arg = arg.split('=')
            logger.debug(f'Current arg {split_arg}')
            if len(split_arg) > 2:
                raise ValueError(f"bad argument {arg}, has more than one '='")

            if split_arg[0] in ["--wallpaper", "-W"]:
                logger.debug(f"using {split_arg[1]} as wallpaper")
                wallpaper = split_arg[1]

            if split_arg[0] in ["--theme", "-T"]:
                logger.debug(f"using {split_arg[1]} as theme")
                theme = split_arg[1]

    if not storage.get('debug'):
        logger.setLevel(logging.INFO)

    if wallpaper not in available_wallpapers:
        if wallpaper is None:
            # use random
            wallpaper = choice(available_wallpapers)
        else:
            raise ValueError(
                f"\n\n specify wallpaper using --wallpaper=wallpaper_name or -W=wallpaper_name \n available wallpapers {available_wallpapers}")

    __main__.start(wallpaper, theme)
