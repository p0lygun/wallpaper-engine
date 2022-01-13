import importlib
import sys
import gc

from kivy.app import App
from kivy.clock import Clock
from kivy.lang.builder import Builder
from kivy.resources import resource_find
from kivy.cache import Cache
from loguru import logger

from .osc import OscHighway
from ..utils.config import Config
from ..utils.common import commands, wallpaper_dir
from .window_manager import WindowManager


wallpaper_osc = OscHighway("wallpaper")

wallpaper_osc.start()


class WallpaperEngine(App):
    def __init__(self, **kwargs):
        self.engine_debug = kwargs.pop("engine_debug")
        super().__init__(**kwargs)
        logger.level("DEBUG")
        logger.debug("Init WallpaperEngine")
        self.we_config = Config()
        self.window_manager = WindowManager()
        self.playing = True
        self.hidden = False
        self.wallpaper = None
        self.wallpaper_module = None
        self.wallpaper_file_name = None
        self.connected = False
        self.kv_file_name = None
        self.kv_file = resource_find("wallpaperengine.kv")

    def on_start(self):
        self.title = (
            self.get_application_name() + "_" + self.we_config.config.get("app", "uuid")
        )

    def on_stop(self, *args):
        logger.debug("Stopping Wallpaper and exiting")
        wallpaper_osc.stop()

    def run(self):
        logger.debug("Starting Wallpaper Layer")
        wallpaper_osc.server.bind(b"/receive", self.receive)
        wallpaper_osc.server.bind(b"/ping", self.ping)
        Clock.schedule_interval(self.set_wallpaper, 0)
        Clock.schedule_interval(self.check_maximized_window, 1)
        super().run()

    def set_wallpaper(self, dt: int):
        if self.connected and not self.engine_debug:
            logger.debug("Connected to Menu OSC.. setting as wallpaper")
            self.window_manager.set_as_wallpaper()
            return False

    def toggle_window_visibility(self):
        if self.playing:
            self.pause()
        else:
            self.play()
        self.window_manager.toggle_workerw_visibility()

    def play(self):
        if self.wallpaper:
            self.wallpaper.play()
            self.playing = True

    def pause(self):
        if self.wallpaper:
            self.wallpaper.pause()
            self.playing = False

    def change_wallpaper(self):  # is also used to reload wallpaper
        self.we_config.reload()
        self.remove_wallpaper()
        self.wallpaper_file_name = self.we_config.config.get("wallpaper", "active")
        # load  wallpaper kv before init
        # sin_wave -> sinwave.kv
        if (
            (wallpaper_dir / "glsl_wallpapers" / self.wallpaper_file_name)
            .with_suffix(".glsl")
            .exists()
        ):
            self.kv_file_name = "shaderwallpaperbase.kv"
        else:
            self.kv_file_name = (
                "".join(self.wallpaper_file_name.lower().split("_")) + ".kv"
            )

        Builder.load_file(resource_find(self.kv_file_name))
        try:
            self.wallpaper_module = importlib.import_module(
                f".wallpapers.{self.wallpaper_file_name}", "wallpaper_engine"
            )
        except ImportError as e:
            logger.critical(f"{e.name} not found...")
            raise
        # put the new one and start the animation
        self.wallpaper = self.wallpaper_module.Wallpaper()
        self.root.add_widget(self.wallpaper)
        Clock.schedule_once(lambda x: self.wallpaper.build(), 0.5)
        Clock.schedule_once(lambda x: self.wallpaper.animate(), 1)

    def remove_wallpaper(self):
        if self.wallpaper is not None:
            self.wallpaper.reset_wallpaper()
            for child in self.root.walk():
                child.canvas.before.clear()
                child.canvas.clear()
                child.canvas.after.clear()
            Builder.unbind_widget(self.wallpaper.uid)
            Builder.unload_file(resource_find(self.kv_file_name))
            sys.modules.pop("wallpaper_engine.wallpapers")
            sys.modules.pop("wallpaper_engine.wallpapers.wallpaper_base")
            sys.modules.pop(f"wallpaper_engine.wallpapers.{self.wallpaper_file_name}")
            for name in Cache._categories.keys():
                Cache.remove(name)
            importlib.invalidate_caches()
            del self.wallpaper
            del self.wallpaper_module
            self.wallpaper = None
            gc.collect()
        self.root.clear_widgets()

    def check_maximized_window(self, dt: int):
        if self.window_manager.check_maximized_window():
            self.pause()
        else:
            self.play()

    def receive(self, *values):
        if commands["EXIT"] in values:
            logger.debug("exit command received")
            # self.window_manager.reset_wallpaper()
            self.stop()
        elif commands["VISIBILITY"] in values:
            logger.debug("Hide / Show command received")
            self.toggle_window_visibility()
        elif commands["PLAY"] in values:
            logger.debug("Play command received")
            self.play()
        elif commands["PAUSE"] in values:
            logger.debug("Pause command received")
            self.pause()
        elif commands["CHANGE"] in values:
            logger.debug("Change command received")
            self.change_wallpaper()

    def ping(self, *values):
        # logger.debug("Received ping")
        wallpaper_osc.send_message(b"/pong", [True], log=False)
        self.connected = True
