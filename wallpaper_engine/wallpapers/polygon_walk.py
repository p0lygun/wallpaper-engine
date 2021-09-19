import colorsys
import pathlib

from kivy.graphics import Color
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.effectwidget import HorizontalBlurEffect
from kivy.properties import NumericProperty, ColorProperty, ListProperty
from kivy.utils import get_color_from_hex
from kivy.clock import Clock
from kivy.animation import Animation

from wallpaper_engine.wallpapers.wallpaper_base import WallpaperBase
from wallpaper_engine.utils.config import Config


settings_json = [
    {"type": "title", "title": "Polygon walk Wallpaper Settings"},
    {
        "type": "string",
        "title": "Color of the first polygon",
        "desc": "Must be a hex value",
        "section": "wallpaper",
        "key": "start_color",
    },
    {
        "type": "numeric",
        "title": "Number of polygons",
        "desc": "min. 0",
        "section": "wallpaper",
        "key": "number_of_polygons",
        "is_int": True,
    },
    {
        "type": "numeric",
        "title": "Sides in polygon",
        "desc": "Must be >1",
        "section": "wallpaper",
        "key": "sides",
        "is_int": True,
    },
]


class Polygon(FloatLayout):
    part_color = ColorProperty(get_color_from_hex("#ff0000"))
    poly_width = NumericProperty(1)
    sides = NumericProperty(1)
    effects = ListProperty()
    lwidth = NumericProperty(1.5)
    temp = NumericProperty(1)


class Wallpaper(WallpaperBase):
    background_color = ColorProperty(
        defaultvalue=get_color_from_hex("000000"),
        errorhandler=lambda x: get_color_from_hex("000000"),
    )
    number_of_polygons = NumericProperty(12)
    sides = NumericProperty(6)
    shift = NumericProperty(0)
    start_color = ColorProperty(get_color_from_hex("#03fcf0"))

    def __init__(self, debug=False):
        super().__init__()
        if not debug:
            self.config = Config(local=True, module=pathlib.Path(__file__).stem)
            self.load_config(settings_json)

    def animate(self):
        polygons = self.container.children
        trans = "in_out_quad"

        def inner_loop(dt: float):
            for index, polygon in enumerate(polygons, start=1):
                anim = Animation(duration=(index * 0.09), transition=trans)
                anim.bind(on_complete=self.start_anim)
                anim.start(polygon)

        Clock.schedule_once(inner_loop, 0)

    def start_anim(self, anim, widget):
        dur = 2
        anim = Animation(
            center_x=self.width * 0.80, transition=anim.transition, duration=dur
        ) + Animation(center_x=self.shift, transition=anim.transition, duration=dur)
        anim.repeat = True
        anim.start(widget)

    def build(self):
        self.container = self.ids.container
        self.shift = self.width * 0.2
        for i in reversed(range(self.number_of_polygons)):
            size = self.width * 0.2
            polygon = Polygon(size=(size, size))
            polygon.center_x = self.shift
            polygon.center_y = self.center_y
            polygon.poly_width = size * 0.9
            blur = i + 1
            if i > 0:
                polygon.effects = [HorizontalBlurEffect(size=blur)]
            polygon.sides = 6
            if i == 0:
                polygon.part_color = self.start_color
                polygon.lwidth = 2
            else:
                c = Color(*colorsys.rgb_to_hsv(*self.start_color[0:-1]), mode="hsv")
                c.h = (c.h - (c.h * 0.05) * i * 2) % 1
                polygon.part_color = c.rgba
                polygon.lwidth = 1 + (4 * (i / self.number_of_polygons))
            self.container.add_widget(polygon)
