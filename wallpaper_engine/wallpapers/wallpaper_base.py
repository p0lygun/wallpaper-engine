from pathlib import Path
from typing import Union

from kivy.app import App
from kivy.clock import Clock
from kivy.uix.floatlayout import FloatLayout
from kivy.utils import get_color_from_hex, get_hex_from_color
from kivy.core.window import Window
from kivy.graphics import RenderContext
from kivy.properties import StringProperty
from kivy.uix.widget import Widget


class WallpaperBase(FloatLayout):
    def __init__(self):
        super(WallpaperBase, self).__init__()
        self.app = App.get_running_app()
        self.container = None
        self.animation_loop_clock = None
        self.animation = None
        self.playing = False
        self.is_shader_wallpaper = False
        self.glsl_source = None

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
                        if item.get("is_int") in ["True", True]:
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

    def reset_wallpaper(self):
        if self.animation_loop_clock:
            Clock.unschedule(self.animation_loop_clock)


class ShaderBase(Widget):
    fs = StringProperty(None)

    def __init__(self, **kwargs):
        self.canvas = RenderContext()
        self.glsl_source: Union[Path, None] = None
        super().__init__(**kwargs)
        self.custom_headers = """
$HEADER$
uniform vec2 iResolution;
uniform float iTime;
#define fragCoord gl_FragCoord
#define fragColor gl_FragColor
"""
        # We'll update our glsl variables in a clock
        Clock.schedule_interval(self.update_glsl, 1 / 60.0)

    def on_fs(self, instance, value):
        shader = self.canvas.shader
        old_value = shader.fs
        shader.fs = self.custom_headers + value
        if not shader.success:
            shader.fs = old_value
            raise Exception("failed")

    def update_glsl(self, *largs):
        self.canvas["iTime"] = Clock.get_boottime()
        self.canvas["iResolution"] = list(map(float, self.size))
        win_rc = Window.render_context
        self.canvas["projection_mat"] = win_rc["projection_mat"]
        self.canvas["modelview_mat"] = win_rc["modelview_mat"]
        self.canvas["frag_modelview_mat"] = win_rc["frag_modelview_mat"]
