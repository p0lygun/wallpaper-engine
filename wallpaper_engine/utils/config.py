import logging
from uuid import uuid4
from pathlib import Path

from kivy.config import ConfigParser
from kivy.app import App

from .logger import Logger


class Config:
    config = ConfigParser()

    def __init__(self, user_data_dir):
        self.config_file_path = Path(user_data_dir) / 'config.ini'
        self.config_file_path.touch(exist_ok=True)
        self.config.read(self.config_file_path.as_posix())
        Logger.debug(f'config:config file at {self.config_file_path}')
        if len(self.config.sections()) == 0:
            Logger.info('config:setting up logger')
            if not self.config.has_section('app') or self.config.get('app', 'first_run', fallback=True):
                Logger.debug('config:Making New Config')
                # set sections
                self.config.setdefaults('app', {
                    'first_run': True,
                    'log_level': logging.DEBUG,
                    'debug': True,
                    'uuid': uuid4().hex,
                    'fps': 60
                })
                self.config.setdefaults('wallpaper', {
                    'active': 'sin-wave'  # todo: set one randomly by choosing from wallpaper directory
                })
        else:
            Logger.info('config:Using existing config')

    def remove_file(self) -> None:
        """removes the config file from disk"""
        self.config_file_path.unlink(missing_ok=True)

    def write(self) -> None:
        """saves file to disk"""
        self.config.write()
