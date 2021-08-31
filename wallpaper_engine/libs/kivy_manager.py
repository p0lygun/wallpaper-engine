import logging
import random

from kivy.app import App
from kivy.uix.label import Label
from kivy.clock import Clock

from ..utils.config import Config
from ..utils.logger import Logger
from .window_manager import WindowManager


class WallpaperEngine(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Logger.set_level(logging.DEBUG)
        self.we_config = Config(self.user_data_dir)
        self.window_manager = WindowManager()
        self.hwnd = None

    def on_start(self):
        self.we_config.config.set("app", "first_run", False)
        log_level = self.we_config.config.get("app", "log_level")
        if log_level.isnumeric():
            log_level = int(log_level)
            if log_level in [0, 10, 20, 30, 40, 50]:
                Logger.set_level(log_level)
            else:
                self.we_config.config.set("app", "log_level", 10)
        self.we_config.write()
        self.title = (
            self.get_application_name() + "_" + self.we_config.config.get("app", "uuid")
        )

    def on_stop(self):
        self.window_manager.reset_wallpaper()

    def build(self):
        seed = random.random()
        Logger.debug(f"seed {seed}")
        return Label(text=f"{seed}")

    def run(self):
        Clock.schedule_once(lambda dt: self.window_manager.set_as_wallpaper(), 0.5)
        super().run()
