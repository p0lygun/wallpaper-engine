import pathlib
import random

from kivy.clock import Clock
from kivy.properties import NumericProperty, ColorProperty, BoundedNumericProperty
from kivy.utils import get_color_from_hex
from kivy.uix.widget import Widget

from wallpaper_engine.wallpapers.wallpaper_base import WallpaperBase
from wallpaper_engine.utils.config import Config


settings_json = [
    {"type": "title", "title": "Star Field wallpaper Settings"},
    {
        "type": "string",
        "title": "Star Color",
        "desc": "Color of the stars (Hex)",
        "section": "wallpaper",
        "key": "star_color",
    },
    {
        "type": "string",
        "title": "Background Color",
        "desc": "Background Color (Hex)",
        "section": "wallpaper",
        "key": "background_color",
    },
]


def map_range(value, min_vale, max_value, map_min, map_max):
    return (value - min_vale) / (max_value - min_vale) * (map_max - map_min) + map_min


class Star(Widget):
    star_size = NumericProperty(1)
    star_color = ColorProperty(get_color_from_hex("#c7c6c5"))
    velocity = NumericProperty(0.1)
    z = NumericProperty(0)


class Wallpaper(WallpaperBase):
    number_of_stars = NumericProperty(400)
    star_color = ColorProperty(get_color_from_hex("#c7c6c5"))
    background_color = ColorProperty(get_color_from_hex("#000000"))
    streak_color = ColorProperty(get_color_from_hex("#ababab"))
    star_size = BoundedNumericProperty(6, min=1.0, max=100.0, errorvalue=5)
    warp_speed = BoundedNumericProperty(10.0, min=1.0, max=100.0, errorvalue=1.0)

    def __init__(self, debug=False):
        super().__init__()
        if not debug:
            self.config = Config(local=True, module=pathlib.Path(__file__).stem)
            self.load_config(settings_json)

    def animate(self):
        margin = 20

        def inner_loop(df: int):
            for star in self.container.children:
                if star.x < -margin:
                    star.x += self.width + margin
                elif star.x > self.width + margin:
                    star.x = -margin
                if star.y < -margin:
                    star.y += self.height + margin
                elif star.y > self.height:
                    star.y = -margin

                star.x -= star.velocity
                star.y -= star.velocity

        self.animation_loop_clock = Clock.schedule_interval(inner_loop, 0)

    def build(self):
        self.container = self.ids.container
        self.number_of_stars = int(max(self.width, self.height) * 0.5)
        for i in range(self.number_of_stars):
            star = Star()
            star.x = random.uniform(0, self.width)
            star.y = random.uniform(0, self.height)
            star.star_size = random.uniform(1, self.star_size)
            star.velocity = random.uniform(1, self.warp_speed) / 80
            star.z = self.width
            star.star_color = self.star_color
            self.container.add_widget(star)

    def play(self):
        if self.animation_loop_clock:
            self.animation_loop_clock()

    def pause(self):
        if self.animation_loop_clock:
            self.animation_loop_clock.cancel()
