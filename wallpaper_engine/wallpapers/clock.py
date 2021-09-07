from datetime import datetime
from kivy.clock import Clock
from kivy.properties import NumericProperty
from kivy.properties import ColorProperty
from kivy.properties import StringProperty
from kivy.animation import Animation
from kivy.utils import get_color_from_hex

from wallpaper_engine.wallpapers.wallpaper_base import WallpaperBase


class Wallpaper(WallpaperBase):
    sec_angle = NumericProperty(int(datetime.now().strftime("%S")) * 6)
    min_angle = NumericProperty(int(datetime.now().strftime("%M")) * 6)
    hour_angle = NumericProperty(int(datetime.now().strftime("%I")) * 30)

    # settings

    hand_width = NumericProperty(3)
    clock_width_factor = NumericProperty(0.1)
    spacing = NumericProperty(15)
    second_hand_color = ColorProperty(get_color_from_hex("D4ECDD"))
    minute_hand_color = ColorProperty(get_color_from_hex("345B63"))
    hour_hand_color = ColorProperty(get_color_from_hex("152D35"))
    line_end_cap = StringProperty("square")

    def __init__(self):
        super(Wallpaper, self).__init__()
        Clock.schedule_interval(lambda dt: self.animate(), 1)

    def animate(self):
        now = datetime.now()
        anim = Animation(
            sec_angle=int(now.strftime("%S")) * 6,
            min_angle=int(now.strftime("%M")) * 6,
            hour_angle=int(now.strftime("%I")) * 30,
        )
        anim.start(self)
