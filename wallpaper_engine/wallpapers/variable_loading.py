import pathlib
import random

from kivy.app import App
from kivy.clock import Clock
from kivy.uix.widget import Widget
from kivy.properties import NumericProperty
from kivy.properties import BoundedNumericProperty
from kivy.properties import ColorProperty
from kivy.utils import get_color_from_hex

from wallpaper_engine.wallpapers.wallpaper_base import WallpaperBase
from wallpaper_engine.utils.config import Config


settings_json = [
    {"type": "title", "title": "Variable Loading wallpaper Settings"},
    {
        "type": "numeric",
        "title": "Angular Velocity",
        "desc": "velocity at which the outermost arm will move (angle/second)",
        "section": "wallpaper",
        "key": "angular_velocity",
    },
    {
        "type": "numeric",
        "title": "Start Angle",
        "desc": "Angle at which the lagging part of the arc should be",
        "section": "wallpaper",
        "key": "start_angle",
    },
    {
        "type": "numeric",
        "title": "Radius",
        "desc": "Radius of the inner-most arm",
        "section": "wallpaper",
        "key": "radius",
    },
    {
        "type": "string",
        "title": "Background Color",
        "desc": "Background color in hex",
        "section": "wallpaper",
        "key": "background_color",
    },
    {
        "type": "string",
        "title": "Primary color",
        "desc": "color in hex",
        "section": "wallpaper",
        "key": "primary_color",
    },
    {
        "type": "string",
        "title": "Secondary color",
        "desc": "color in hex",
        "section": "wallpaper",
        "key": "secondary_color",
    },
    {
        "type": "numeric",
        "title": "Arm length",
        "desc": "length of the arm color in degrees",
        "section": "wallpaper",
        "key": "arm_length",
    },
    {
        "type": "numeric",
        "title": "Arm width",
        "desc": "width of the arm color in pixels",
        "section": "wallpaper",
        "key": "arm_width",
    },
    {
        "type": "numeric",
        "title": "Number of arms",
        "desc": "Number of arms [min 5]",
        "section": "wallpaper",
        "key": "number_of_arms",
        "is_int": True,
    },
]


class Arm(Widget):
    angular_velocity = NumericProperty()
    arm_color = ColorProperty(get_color_from_hex("277038"))
    radius = NumericProperty(1)
    start_angle = NumericProperty(0)
    arm_length = NumericProperty(0)
    arm_width = NumericProperty(1)


class Wallpaper(WallpaperBase):
    angular_velocity = NumericProperty(0.5)
    start_angle = NumericProperty(0)
    radius = NumericProperty(250)
    background_color = ColorProperty(get_color_from_hex("000000"))

    primary_color = ColorProperty(get_color_from_hex("525252"))
    secondary_color = ColorProperty(get_color_from_hex("2b2b2b"))
    arm_length = NumericProperty(100)
    arm_width = NumericProperty(2)
    number_of_arms = BoundedNumericProperty(
        100, min=5, max=500, errorhandler=lambda x: 100
    )

    def __init__(self):
        super(Wallpaper, self).__init__()
        self.app = None
        self.container = None
        self.config = Config(local=True, module=pathlib.Path(__file__).stem)
        self.load_config(settings_json)

    def animate(self):
        arms = self.container.children

        def inner_loop(dt: int):
            for arm in arms:
                if arm.start_angle >= 360:
                    arm.start_angle = 0
                arm.start_angle += arm.angular_velocity

        self.animation_loop_clock = Clock.schedule_interval(inner_loop, 0)
        self.playing = True

    def build(self):
        self.app = App.get_running_app()
        self.container = self.app.root.children[0].ids.container
        for i in range(1, self.number_of_arms + 1):
            arm = Arm()
            arm.angular_velocity = self.angular_velocity * (i / self.number_of_arms)
            arm.arm_color = random.choice([self.primary_color, self.secondary_color])
            arm.radius = self.radius * 0.03 * i
            arm.arm_length = self.arm_length
            arm.start_angle = self.start_angle - arm.arm_length
            arm.arm_width = self.arm_width
            self.container.add_widget(arm)

    def pause(self):
        if self.playing:
            self.animation_loop_clock.cancel()
            self.playing = False

    def play(self):
        if not self.playing:
            self.animation_loop_clock()
            self.playing = True
