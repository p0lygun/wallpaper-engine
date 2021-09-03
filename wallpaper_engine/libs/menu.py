try:
    from kivy.config import Config as KvConfig

    KvConfig.set("kivy", "log_level", "warning")
except ImportError:
    pass

from kivy.app import App
from kivy.lang.builder import Builder
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
        text: "Exit"
        size_hint : [.2,.1]
        on_release: app.exit()

"""

menu_json = [{"type": "title", "title": "Wallpaper Engine"}]

menu_osc = OscHighway("menu")


class WallpaperEngine(App):
    def __init__(self):
        super(WallpaperEngine, self).__init__()
        self.connection_ok = False
        self.we_config = Config()

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
            count = 0
            menu_osc.send_message(b"/ping", [True])
            while not self.connection_ok:
                if count < 10:
                    menu_osc.config.reload()
                    menu_osc.send_message(b"/ping", [True], log=False)
                    count += 1
                else:
                    Logger.debug("Unable to connect to wallpaper backend exiting ...")
                    exit(0)
                await trio.sleep(1)
            Logger.debug("Connected to wallpaper")

        trio.run(check_connection)

    def on_stop(self):
        Logger.debug("Closing.... Menu")

    def build(self):
        # Window.bind(on_request_close=self.on_request_close)
        return Builder.load_string(kv)

    def pong(self, *values):
        if True in values:
            self.connection_ok = True

    def exit(self, *args):
        menu_osc.send_message(b"/receive", commands["EXIT"])
        self.stop()

    @staticmethod
    def change_wallpaper():
        menu_osc.send_message(b"/receive", commands["CHANGE"])

    @staticmethod
    def toggle_window_visibility():
        menu_osc.send_message(b"/receive", commands["VISIBILITY"])


if __name__ == "__main__":
    WallpaperEngine().run()
