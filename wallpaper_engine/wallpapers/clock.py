import pathlib
from datetime import datetime
from kivy.clock import Clock
from kivy.properties import NumericProperty
from kivy.properties import ColorProperty
from kivy.properties import OptionProperty
from kivy.animation import Animation
from kivy.utils import get_color_from_hex

from wallpaper_engine.wallpapers.wallpaper_base import WallpaperBase
from wallpaper_engine.utils.config import Config

settings_json = [
    {"type": "title", "title": "Clock wallpaper Settings"},
    {
        "type": "numeric",
        "title": "Hand width",
        "desc": "Width of each hand",
        "section": "wallpaper",
        "key": "hand_width",
    },
    {
        "type": "numeric",
        "title": "Spacing",
        "desc": "Spacing between arcs",
        "section": "wallpaper",
        "key": "spacing",
    },
    {
        "type": "string",
        "title": "Second Hand Color",
        "desc": "color in hex",
        "section": "wallpaper",
        "key": "second_hand_color",
    },
    {
        "type": "string",
        "title": "Minute Hand Color",
        "desc": "color in hex",
        "section": "wallpaper",
        "key": "minute_hand_color",
    },
    {
        "type": "string",
        "title": "Hour Hand Color",
        "desc": "color in hex",
        "section": "wallpaper",
        "key": "hour_hand_color",
    },
    {
        "type": "options",
        "title": "Hand arc end cap",
        "options": ["square", "round"],
        "desc": "How the end of arc should look",
        "section": "wallpaper",
        "key": "line_end_cap",
    },
]


class Wallpaper(WallpaperBase):
    sec_angle = NumericProperty(int(datetime.now().strftime("%S")) * 6)
    min_angle = NumericProperty(int(datetime.now().strftime("%M")) * 6)
    hour_angle = NumericProperty(int(datetime.now().strftime("%I")) * 30)
    clock_width_factor = NumericProperty(0.1)

    # settings

    hand_width = NumericProperty(3)
    spacing = NumericProperty(15)
    second_hand_color = ColorProperty(get_color_from_hex("D4ECDD"))
    minute_hand_color = ColorProperty(get_color_from_hex("345B63"))
    hour_hand_color = ColorProperty(get_color_from_hex("152D35"))
    line_end_cap = OptionProperty("square", options=["square", "round", "none"])

    def __init__(self):
        super(Wallpaper, self).__init__()
        Clock.schedule_interval(lambda dt: self.animate(), 1)
        self.config = Config(local=True, module=pathlib.Path(__file__).stem)
        self.load_config(settings_json)

    def animate(self):
        now = datetime.now()
        self.animation = Animation(
            sec_angle=int(now.strftime("%S")) * 6,
            min_angle=int(now.strftime("%M")) * 6,
            hour_angle=int(now.strftime("%I")) * 30,
        )
        self.animation.start(self)

    def pause(self):
        if self.playing:
            self.animation.stop(self)
            self.playing = False

    def play(self):
        if not self.playing:
            self.animation.stop(self)
            self.playing = True
