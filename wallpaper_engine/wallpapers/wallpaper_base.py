from kivy.uix.floatlayout import FloatLayout
from kivy.utils import get_color_from_hex, get_hex_from_color
from kivy.app import App


class WallpaperBase(FloatLayout):
    def __init__(self):
        super(WallpaperBase, self).__init__()
        self.app = App.get_running_app()
        self.container = None
        self.animation_loop_clock = None
        self.animation = None
        self.playing = False

    def build(self):
        pass

    def animate(self):
        pass

    def play(self):
        pass

    def pause(self):
        pass

    def load_config(self, list_json):
        s_json = list_json
        # set defaults
        if not self.config.config.has_section("wallpaper"):
            self.config.config.add_section("wallpaper")
        for item in s_json:
            if item["type"] != "title":
                var_name = item["key"]
                if "color" in var_name:
                    self.config.config.setdefault(
                        "wallpaper",
                        var_name,
                        get_hex_from_color(getattr(self, var_name)),
                    )
                else:
                    self.config.config.setdefault(
                        "wallpaper", var_name, getattr(self, var_name)
                    )
        self.config.reload()
        self.config.write()
        # read from config
        for item in s_json:
            if item["type"] != "title":
                var_name = item["key"]
                if "color" in var_name:
                    setattr(
                        self,
                        var_name,
                        get_color_from_hex(
                            self.config.config.get("wallpaper", var_name)
                        ),
                    )
                else:
                    if item["type"] == "numeric":
                        if item.get("is_int") == "True":
                            setattr(
                                self,
                                var_name,
                                self.config.config.getint("wallpaper", var_name),
                            )
                        else:
                            setattr(
                                self,
                                var_name,
                                self.config.config.getfloat("wallpaper", var_name),
                            )
                    else:
                        setattr(
                            self,
                            var_name,
                            self.config.config.get("wallpaper", var_name),
                        )
