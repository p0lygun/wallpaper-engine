import logging
import random

from kivy.app import App
from kivy.uix.label import Label
from kivy.clock import Clock

from .osc import OscHighway
from ..utils.config import Config
from ..utils.logger import LoggerClass
from ..utils.common import commands
from .window_manager import WindowManager

Logger = LoggerClass(__name__)
Logger.module = "kivy_manager"

wallpaper_osc = OscHighway("wallpaper")


class WallpaperEngine(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Logger.set_level(logging.DEBUG)
        self.we_config = Config()
        self.window_manager = WindowManager()
        self.hwnd = None
        self.playing = True
        self.hidden = False

    def on_start(self):
        self.title = (
            self.get_application_name() + "_" + self.we_config.config.get("app", "uuid")
        )

    def on_stop(self, *args):
        Logger.debug("Stopping Wallpaper and exiting")
        wallpaper_osc.stop()

    def build(self):
        seed = random.random()
        Logger.debug(f"seed {seed}")
        return Label(text=f"{seed}")

    def run(self):
        Logger.debug("Starting Wallpaper Layer")
        wallpaper_osc.start()
        wallpaper_osc.server.bind(b"/receive", self.receive)
        wallpaper_osc.server.bind(b"/ping", self.ping)

        Clock.schedule_once(lambda dt: self.window_manager.reset_wallpaper(), 0.5)
        Clock.schedule_once(lambda dt: self.window_manager.set_as_wallpaper(), 0.5)
        super().run()

    def toggle_window_visibility(self):
        self.playing = False
        self.window_manager.toggle_workerw_visibility()

    def play(self):
        self.playing = True

    def pause(self):
        self.playing = False

    def change_wallpaper(self):
        pass

    def receive(self, *values):
        if commands["EXIT"] in values:
            Logger.debug("exit command received")
            # self.window_manager.reset_wallpaper()
            self.stop()
        elif commands["VISIBILITY"] in values:
            Logger.debug("Hide / Show command received")
            self.toggle_window_visibility()
        elif commands["PLAY"] in values:
            Logger.debug("Play command received")
            self.play()
        elif commands["PAUSE"] in values:
            Logger.debug("Pause command received")
            self.pause()
        elif commands["CHANGE"] in values:
            Logger.debug("Change command received")
            self.change_wallpaper()

    @staticmethod
    def ping(self, *values):
        wallpaper_osc.send_message(b"/pong", [True], log=False)
