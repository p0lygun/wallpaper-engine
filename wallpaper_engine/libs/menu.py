from pathlib import Path
import importlib
import sys

try:
    from kivy.config import Config as KvConfig

    KvConfig.read(str((Path(__file__).parents[1] / "data" / "kivy_menu_config")))
    KvConfig.write()
    KvConfig.set("kivy", "log_level", "warning")
    KvConfig.set("graphics", "window_state", "hidden")
except ImportError:
    pass

from kivy.app import App
from kivy.lang.builder import Builder
from kivy.uix.settings import SettingsWithSidebar
from kivy.core.window import Window
import stackprinter
import trio

try:
    from wallpaper_engine.utils.logger import LoggerClass

    LoggerClass.prefix = "WE-MENU"
    Logger = LoggerClass(__name__)
    Logger.module = "Menu"
    Logger.debug(f"python exe at : {sys.executable}")
except ImportError:
    pass
from wallpaper_engine.utils.config import Config
from wallpaper_engine.libs.osc import OscHighway
from wallpaper_engine.utils.common import (
    commands,
    valid_wallpapers,
    wallpaper_dir,
    build_settings_json,
)

stackprinter.set_excepthook(style="darkbg2")

kv = """
StackLayout:
    Button:
        text: "change / reload wallpaper"
        size_hint : [.2,.1]
        on_release: app.change_wallpaper()
    Button:
        text: "HIDE / SHOW"
        size_hint : [.2,.1]
        on_release: app.toggle_window_visibility()
    Button:
        text: "Play / Pause"
        size_hint : [.2,.1]
        on_release: app.toggle_state()
    Button:
        text: "Show settings"
        size_hint : [.2,.1]
        on_release: app.open_settings()
    Button:
        text: "Exit"
        size_hint : [.2,.1]
        on_release: app.exit()
"""

menu_json = [
    {"type": "title", "title": "App"},
    {
        "type": "numeric",
        "title": "log level",
        "key": "log_level",
        "desc": "Set the Level of debug [0, 10, 20, 30, 40, 50, 60]",
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
        self.connection_ok = False
        self.we_config = Config()
        self.wallpaper_dir = wallpaper_dir
        self.valid_wallpapers = valid_wallpapers
        self.wallpaper_name = self.we_config.config.get("wallpaper", "active")
        self.wallpaper_changed = False
        self.wallpaper_config = None

        self.playing = True

    def on_start(self):
        Logger.info("Starting Menu")
        self.we_config.config.set("app", "first_run", False)
        log_level = self.we_config.config.get("app", "log_level")
        if type(log_level) == str and log_level.isnumeric():
            log_level = int(log_level)
            if log_level in [0, 10, 20, 30, 40, 50]:
                Logger.set_level(log_level)
            else:
                self.we_config.config.set("app", "log_level", 10)
        self.we_config.write()
        menu_osc.start()
        menu_osc.server.bind(b"/pong", self.pong)

        async def check_connection():
            menu_osc.send_message(b"/ping", [True])
            while not self.connection_ok:
                menu_osc.config.reload()
                menu_osc.send_message(b"/ping", [True], log=False)
                await trio.sleep(0.5)
            Logger.debug("Connected to wallpaper")
            Window.show()

        trio.run(check_connection)

    def on_stop(self):
        Logger.debug("Closing.... Menu")

    def on_config_change(self, config, section, key, value):
        Logger.debug(f"on_config_changed {(config, section, key, value)}")
        if section == "app":
            if key == "log_level":
                Logger.set_level(int(value))

        if config == self.we_config.config:
            if section == "wallpaper":
                if key == "active":
                    Logger.debug("Wallpaper Changed")
                    self.wallpaper_name = value
                    self.wallpaper_changed = True

        if config == self.wallpaper_config.config:
            self.change_wallpaper()

    def build(self):
        self.use_kivy_settings = (
            True if self.we_config.config.getint("app", "kivy_settings") else False
        )
        self.settings_cls = SettingsWithSidebar

        return Builder.load_string(kv)

    def build_settings(self, settings):
        wallpaper_module = importlib.import_module(
            f".wallpapers.{self.wallpaper_name}", "wallpaper_engine"
        )
        wallpaper_module.Wallpaper()
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
        Logger.debug("Closing Settings")
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


if __name__ == "__main__":
    WallpaperEngineMenu().run()
