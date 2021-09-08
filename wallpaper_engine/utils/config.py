import logging
import random
from uuid import uuid4
from pathlib import Path

import appdirs
from kivy.config import ConfigParser

from .logger import LoggerClass
from .common import project_dir

Logger = LoggerClass(__name__)
Logger.module = "config"


class Config:
    def __init__(self, local: bool = False, module: str = None):
        self.config = ConfigParser()
        self.appname = "Wallpaper engine"
        self.module = module
        if local and module is not None:
            self.dir = Path(__file__).parents[1] / "data" / module
        else:
            Logger.debug("using global config")
            self.dir = Path(
                appdirs.user_data_dir(appname=self.appname, appauthor="", roaming=True)
            )
        self.dir.mkdir(parents=True, exist_ok=True)
        self.config_file_path = self.dir / "config.ini"
        self.config_file_path.touch(exist_ok=True)
        self.config.read(self.config_file_path.as_posix())
        if not local:
            Logger.debug(f"config file at {self.config_file_path}")
            if len(self.config.sections()) == 0:
                if not self.config.has_section("app") or self.config.get(
                    "app", "first_run", fallback=True
                ):
                    Logger.debug("Making New Config")
                    # set sections
                    self.config.setdefaults(
                        "app",
                        {
                            "first_run": True,
                            "log_level": logging.DEBUG,
                            "debug": True,
                            "uuid": uuid4().hex,
                            "fps": 60,
                            "kivy_settings": False,
                        },
                    )
                    random_wallpaper = random.choice(
                        [
                            path.stem
                            for path in (project_dir / "wallpapers").glob("*py")
                            if path.stem not in ["wallpaper_base", "__init__"]
                        ]
                    )
                    self.config.setdefaults(
                        "wallpaper",
                        {"active": f"{random_wallpaper}"},
                    )
            else:
                Logger.info("Using existing config")
                Logger.set_level(self.config.get("app", "log_level"))

    def remove_file(self) -> None:
        """removes the config file from disk"""
        self.config_file_path.unlink(missing_ok=True)

    def write(self) -> None:
        """saves file to disk"""
        self.config.write()

    def reload(self) -> None:
        self.config.read(self.config_file_path.as_posix())
