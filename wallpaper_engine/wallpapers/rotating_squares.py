import pathlib
import time

from kivy.clock import Clock
from kivy.properties import NumericProperty, BoundedNumericProperty, ColorProperty
from kivy.uix.widget import Widget
from kivy.utils import get_random_color

from wallpaper_engine.wallpapers.wallpaper_base import WallpaperBase
from wallpaper_engine.utils.config import Config

module = pathlib.Path(__file__).stem

settings_json = [
    {"type": "title", "title": "Rotating Squares Wallpaper Settings"},
    {
        "type": "string",
        "title": "Color of the square",
        "desc": "Set the color of the square. Must be a hex value",
        "section": "wallpaper",
        "key": "square_color",
    },
    {
        "type": "numeric",
        "title": "Number of square",
        "desc": "Total number of squares",
        "section": "wallpaper",
        "key": "number_of_squares",
        "is_int": True,
    },
    {
        "type": "numeric",
        "title": "Width of square",
        "desc": "1.0 < width < 10.0",
        "section": "wallpaper",
        "key": "square_width",
    },
]


class Square(Widget):
    square_color = ColorProperty()
    square_width = BoundedNumericProperty(0.1, min=0.1, max=10.0, errorvalue=1.0)
    s_x = NumericProperty(150)
    s_y = NumericProperty(200)
    s_width = NumericProperty(100)
    rot_angle = NumericProperty()


class Wallpaper(WallpaperBase):
    square_color = ColorProperty(get_random_color())
    square_width = NumericProperty(1, errorvalue=1)
    number_of_squares = NumericProperty(50)
    time_init = NumericProperty(time.time())

    def __init__(self, debug=False):
        super(Wallpaper, self).__init__()
        if not debug:
            self.config = Config(local=True, module=module)
            self.load_config(settings_json)

    def animate(self):
        squares = self.container.children[::-1]

        def inner_loop(dt: int):
            for index, square in enumerate(squares, start=1):
                dt = time.time() - self.time_init
                square.rot_angle = -(dt * index)

        Clock.schedule_interval(inner_loop, 1 / 60.0)

    def build(self):
        self.container = self.ids.container
        origin = self.center
        max_width = min(self.width, self.height) * 0.8
        for i in range(1, self.number_of_squares + 1):
            square = Square()
            square.s_width = max_width
            max_width *= 0.9
            square.s_x = origin[0] - square.s_width / 2 - self.square_width
            square.s_y = origin[1] - square.s_width / 2 - self.square_width
            square.square_color = self.square_color
            square.square_width = self.square_width
            self.container.add_widget(square)
