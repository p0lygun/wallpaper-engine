import json
from pathlib import Path

try:
    from kivy.config import Config as KvConfig

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
except ImportError:
    pass

from wallpaper_engine.utils.config import Config
from wallpaper_engine.libs.osc import OscHighway
from wallpaper_engine.utils.common import commands

stackprinter.set_excepthook(style="darkbg2")

kv = """
StackLayout:
    Button:
        text: "change wallpaper"
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

wallpaper_dir = Path(__file__).parents[1] / "wallpapers"
valid_wallpapers = [
    i.stem
    for i in wallpaper_dir.glob("*.py")
    if i.name not in ["wallpaper_base.py", "__init__.py"]
]

menu_json = json.dumps(
    [
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
)

menu_osc = OscHighway("menu")


class WallpaperEngineMenu(App):
    def __init__(self):
        super(WallpaperEngineMenu, self).__init__()
        self.connection_ok = False
        self.we_config = Config()
        self.wallpaper_dir = wallpaper_dir
        self.valid_wallpapers = valid_wallpapers
        self.playing = True

    def on_start(self):
        Logger.info("Starting Menu")
        self.we_config.config.set("app", "first_run", False)
        log_level = self.we_config.config.get("app", "log_level")
        if log_level.isnumeric():
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
        if section == "app":
            if key == "log_level":
                Logger.set_level(int(value))

    def build(self):
        self.use_kivy_settings = (
            True
            if self.we_config.config.get("app", "kivy_settings") == "True"
            else False
        )
        self.settings_cls = SettingsWithSidebar
        return Builder.load_string(kv)

    def build_settings(self, settings):
        settings.add_json_panel(
            "Wallpaper engine", self.we_config.config, data=menu_json
        )

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
