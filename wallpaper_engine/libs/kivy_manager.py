import logging
import importlib

from kivy.app import App
from kivy.clock import Clock
from kivy.lang.builder import Builder
from kivy.resources import resource_find

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
        self.wallpaper = None
        self.wallpaper_module = None
        self.wallpaper_file_name = None
        self.kv_file_name = None
        self.kv_file = resource_find("wallpaperengine.kv")

    def on_start(self):
        self.title = (
            self.get_application_name() + "_" + self.we_config.config.get("app", "uuid")
        )

    def on_stop(self, *args):
        Logger.debug("Stopping Wallpaper and exiting")
        wallpaper_osc.stop()

    def run(self):
        Logger.debug("Starting Wallpaper Layer")
        wallpaper_osc.start()
        wallpaper_osc.server.bind(b"/receive", self.receive)
        wallpaper_osc.server.bind(b"/ping", self.ping)

        Clock.schedule_once(lambda dt: self.window_manager.reset_wallpaper(), 0.5)
        Clock.schedule_once(lambda dt: self.window_manager.set_as_wallpaper(), 0.5)
        super().run()

    def toggle_window_visibility(self):
        if self.playing:
            self.pause()
        else:
            self.play()
        self.window_manager.toggle_workerw_visibility()

    def play(self):
        self.wallpaper.play()
        self.playing = True

    def pause(self):
        self.wallpaper.pause()
        self.playing = False

    def change_wallpaper(self):
        self.we_config.reload()
        wallpaper_file_name = self.we_config.config.get("wallpaper", "active")
        if self.wallpaper_file_name != wallpaper_file_name:
            self.wallpaper_file_name = self.we_config.config.get("wallpaper", "active")

            # remove prev wallpaper
            self.root.clear_widgets()
            if self.wallpaper is not None:
                for child in self.root.walk():
                    child.canvas.before.clear()
                    child.canvas.clear()
                    child.canvas.after.clear()
                Builder.unload_file(resource_find(self.kv_file_name))
                Builder.unbind_widget(self.wallpaper.uid)
                del self.wallpaper
                del self.wallpaper_module

            # load  wallpaper kv before init
            # sin_wave -> sinwave.kv
            self.kv_file_name = (
                "".join(self.wallpaper_file_name.lower().split("_")) + ".kv"
            )
            Builder.load_file(resource_find(self.kv_file_name))
            try:
                self.wallpaper_module = importlib.import_module(
                    f".wallpapers.{wallpaper_file_name}", "wallpaper_engine"
                )
            except ImportError as e:
                Logger.critical(f"{e.name} not found...")
                raise
            # put the new one and start the animation
            self.wallpaper = self.wallpaper_module.Wallpaper()
            self.root.add_widget(self.wallpaper)
            self.wallpaper.build()
            self.wallpaper.animate()

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
