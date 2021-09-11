import math
import pathlib
import random

from kivy.properties import (
    NumericProperty,
    ColorProperty,
    ListProperty,
    OptionProperty,
)

from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.clock import Clock
from kivy.utils import get_color_from_hex
from kivy.animation import Animation, AnimationTransition
from kivy.core.window import Window
from kivy.graphics import InstructionGroup, Color
from kivy.graphics import SmoothLine


from wallpaper_engine.wallpapers.wallpaper_base import WallpaperBase
from wallpaper_engine.utils.config import Config
from wallpaper_engine.utils.logger import LoggerClass

Logger = LoggerClass(__name__)
module = pathlib.Path(__file__).stem
Logger.module = module


settings_json = [
    {"type": "title", "title": "Rose maths Wallpaper Settings"},
    {
        "type": "string",
        "title": "Color of the points",
        "desc": "Set the color of the points. Must be a hex value",
        "section": "wallpaper",
        "key": "line_color",
    },
    {
        "type": "numeric",
        "title": "Radius factor",
        "desc": "Base radius factor of the rose from [0 ,1]",
        "section": "wallpaper",
        "key": "base_radius_factor",
    },
    {
        "type": "string",
        "title": "Transition",
        "desc": "transition to use on points must be one of kivy.animation.AnimationTransition",
        "section": "wallpaper",
        "key": "transition",
    },
]


class Rose(FloatLayout):
    points_color = ColorProperty(get_color_from_hex("#ff0000"))
    line_points = ListProperty()
    diffusion_points = ListProperty()
    radius = NumericProperty(50)
    spacer = NumericProperty()
    n = NumericProperty()
    d_ = NumericProperty()
    inst_group = InstructionGroup()


class Wallpaper(WallpaperBase):
    line_color = ColorProperty(get_color_from_hex("#ff0000"))
    shape_center = ListProperty()
    base_radius = NumericProperty()
    base_radius_factor = NumericProperty(0.2)
    point_factor = NumericProperty(0.001)
    transition = OptionProperty(
        defaultvalue="in_out_expo",
        options=[
            str(key)
            for key, values in AnimationTransition.__dict__.items()
            if type(values) == staticmethod and key[0] != "_"
        ],
        errorvalue="in_out_expo",
    )

    def __init__(self, debug=False):
        super(Wallpaper, self).__init__()
        if not debug:
            self.config = Config(local=True, module=module)
            self.load_config(settings_json)

    def animate(self):
        rose = self.container.children[0]
        rose.canvas.add(rose.inst_group)
        anim_dur = 2

        def inner_loop(dt: int):
            d = [i for i in range(1, 10)]
            n = [i for i in range(1, 8)]
            full_animation = None
            for i in n:
                for j in d:
                    new_points = self.shuffle_list(
                        self.calc_points(i, j, precision=self.point_factor)
                    )
                    cur_anim = Animation(
                        diffusion_points=new_points,
                        n=i,
                        d_=j,
                        transition=self.transition,
                        duration=anim_dur,
                    )
                    cur_anim.bind(on_start=self.anim_start)
                    cur_anim.bind(on_progress=self.on_prog)

                    if full_animation is None:
                        full_animation = cur_anim
                    else:
                        full_animation += cur_anim

                    full_animation += Animation(spacer=1, transition="linear")

            full_animation.repeat = True
            full_animation.start(rose)

        self.animation_loop_clock = Clock.schedule_once(inner_loop, 0)

    def on_prog(self, anim, widget, prog):
        if prog * 100 >= 95:
            if len(widget.inst_group.children) == 0:
                n = int(anim.animated_properties["n"])
                d = int(anim.animated_properties["d_"])
                color = Color(rgba=self.line_color)
                color.a = 0
                duration = anim.duration * (1 - prog)
                alpha_anim = (
                    Animation(a=1, transition=self.transition, duration=duration)
                    + Animation()
                    + Animation(a=0, transition=self.transition, duration=duration)
                )
                widget.inst_group.add(color)
                widget.inst_group.add(SmoothLine(points=self.calc_points(n, d)))
                alpha_anim.start(color)

    def anim_start(self, anim, widget):
        widget.inst_group.clear()

    def build(self):
        Window.bind(on_resize=self.on_resize)
        self.app = App.get_running_app()
        self.container = self.app.root.children[0].ids.container
        self.base_radius = Window.width * self.base_radius_factor
        self.shape_center = (Window.width / 2, Window.height / 2)
        Logger.debug(self.shape_center)
        rose = Rose()
        rose.points_color = self.line_color
        rose.diffusion_points = self.shuffle_list(
            self.calc_points(1, 1, self.point_factor)
        )
        self.container.add_widget(rose)

    def on_resize(self, cls, w, h):
        self.base_radius = w * self.base_radius_factor
        self.shape_center = (w / 2, h / 2)

    def calc_points(self, n, d, precision: float = 0.01):
        a = 0
        points = []
        k = n / d
        while a < 2 * math.pi * d:
            radius = self.base_radius * math.cos(k * a)
            x = self.shape_center[0] + radius * math.cos(a)
            y = self.shape_center[1] + radius * math.sin(a)
            points.append((x, y))
            a += precision

        tmp = []
        [tmp.extend([*point]) for point in points]
        return tmp

    @staticmethod
    def shuffle_list(point_list: list):
        diffusion_points_copy = point_list.copy()
        new_points_iter = iter(diffusion_points_copy)
        new_points_tuples = list(zip(new_points_iter, new_points_iter))
        random.shuffle(new_points_tuples)
        new_points = []
        [new_points.extend([*point]) for point in new_points_tuples]
        return new_points
