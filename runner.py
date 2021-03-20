import sys
from wallpaper_engine import main
from wallpaper_engine.data.shared import storage

import logging

logger = logging.getLogger('WE_LOGGER')
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)

logger.addHandler(ch)

if __name__ == '__main__':
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

    if wallpaper is None:
        raise ValueError("specify wallpaper using --wallpaper=wallpaper_name or -W=wallpaper_name")

    main.start(wallpaper, theme)
