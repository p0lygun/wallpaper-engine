import os
import sys
from pathlib import Path
import importlib

try:
    from kivy.config import Config as KvConfig

    KvConfig.read(str((Path(__file__).parents[1] / "data" / "kivy_menu_config")))
    KvConfig.write()
    KvConfig.set("kivy", "log_level", "warning")
    KvConfig.set("graphics", "window_state", "hidden")
except ImportError:
    pass

from kivy.app import App
from kivy.uix.settings import SettingsWithSidebar
from kivy.core.window import Window
import stackprinter
import trio
from loguru import logger

from wallpaper_engine.utils.config import Config
from wallpaper_engine.libs.osc import OscHighway
from wallpaper_engine.utils.common import (
    commands,
    valid_wallpapers,
    wallpaper_dir,
    build_settings_json,
    project_dir,
)

stackprinter.set_excepthook(style="darkbg2")
logger.remove()
logger.add(
    sys.stdout,
    colorize=True,
    format="[ <lc>Menu</>      ]"
    "[<b><fg #3b3b3b>{level: ^8}</></>]"
    "[{name}.{function}:{line}]"
    "[ {message} ]",
    level=os.getenv("WE_DEBUG_LEVEL"),
)

menu_json = [
    {"type": "title", "title": "App"},
    {
        "type": "options",
        "title": "log level",
        "key": "log_level",
        "options": ["DEBUG", "INFO", "WARNING", "CRITICAL"],
        "desc": "Set the Level of debug",
        "section": "app",
    },
    {
        "type": "bool",
        "title": "Debug",
        "key": "debug",
        "desc": "Turn off Debugging",
        "section": "app",
    },
    {
        "type": "bool",
        "title": "kivy settings",
        "key": "kivy_settings",
        "desc": "Show kivy settings",
        "section": "app",
    },
    {"type": "title", "title": "Wallpaper"},
    {
        "type": "options",
        "title": "Active Wallpaper",
        "options": valid_wallpapers,
        "key": "active",
        "desc": "Choose a wallpaper from the options",
        "section": "wallpaper",
    },
]

menu_osc = OscHighway("menu")


class WallpaperEngineMenu(App):
    def __init__(self):
        super(WallpaperEngineMenu, self).__init__()
        self.kv_file = (
            str(project_dir / "libs" / "kv" / self.__class__.__name__.lower()) + ".kv"
        )
        self.connection_ok = False
        self.we_config = Config()
        self.wallpaper_dir = wallpaper_dir
        self.valid_wallpapers = valid_wallpapers
        self.wallpaper_name = self.we_config.config.get("wallpaper", "active")
        self.wallpaper_changed = False
        self.wallpaper_config = None
        self.playing = True

    def on_start(self):
        logger.info("Starting Menu")
        self.we_config.config.set("app", "first_run", False)
        log_level = self.we_config.config.get("app", "log_level")
        logger.level(log_level)

        self.we_config.write()
        menu_osc.start()
        menu_osc.server.bind(b"/pong", self.pong)

        async def check_connection():
            logger.debug("Starting Connection Check Loop")
            menu_osc.send_message(b"/ping", [True])
            while not self.connection_ok:
                menu_osc.config.reload()
                menu_osc.send_message(b"/ping", [True], log=False)
                await trio.sleep(0.5)
            logger.debug("Connected to wallpaper")
            Window.show()

        trio.run(check_connection)

    def on_stop(self):
        logger.debug("Closing.... Menu")

    def on_config_change(self, config, section, key, value):
        logger.debug(f"on_config_changed {(config, section, key, value)}")
        if section == "app":
            if key == "log_level":
                logger.level(value)

        if config == self.we_config.config:
            if section == "wallpaper":
                if key == "active":
                    logger.debug("Wallpaper Changed")
                    self.wallpaper_name = value
                    self.wallpaper_changed = True

        if config == self.wallpaper_config.config:
            self.change_wallpaper()

    def build(self):
        self.use_kivy_settings = (
            True if self.we_config.config.getboolean("app", "kivy_settings") else False
        )
        self.settings_cls = SettingsWithSidebar
        Window.bind(on_request_close=self.on_request_close)

    def build_settings(self, settings):
        wallpaper_module = importlib.import_module(
            f".wallpapers.{self.wallpaper_name}", "wallpaper_engine"
        )

        wallpaper_settings_json = wallpaper_module.settings_json
        self.wallpaper_config = Config(local=True, module=self.wallpaper_name)
        settings.add_json_panel(
            "Wallpaper engine",
            self.we_config.config,
            data=build_settings_json(menu_json),
        )
        settings.add_json_panel(
            "Wallpaper settings",
            self.wallpaper_config.config,
            data=build_settings_json(wallpaper_settings_json),
        )

    def close_settings(self, settings=None):
        logger.debug("Closing Settings")
        super(WallpaperEngineMenu, self).close_settings(settings)
        if self.wallpaper_changed:
            super(WallpaperEngineMenu, self).destroy_settings()
            importlib.invalidate_caches()

    # osc
    def pong(self, *values):
        if True in values:
            self.connection_ok = True

    def exit(self, *args):
        menu_osc.send_message(b"/receive", commands["EXIT"])
        self.stop()

    def toggle_state(self):
        if self.playing:
            menu_osc.send_message(b"/receive", commands["PAUSE"])
            self.playing = False
        else:
            menu_osc.send_message(b"/receive", commands["PLAY"])
            self.playing = True

    @staticmethod
    def change_wallpaper():
        menu_osc.send_message(b"/receive", commands["CHANGE"])

    @staticmethod
    def toggle_window_visibility():
        menu_osc.send_message(b"/receive", commands["VISIBILITY"])

    def on_request_close(self, *args, **kwargs):
        self.exit()
        return False


if __name__ == "__main__":
    WallpaperEngineMenu().run()
