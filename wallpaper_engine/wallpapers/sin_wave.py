import pathlib
import random
from kivy.uix.anchorlayout import AnchorLayout
from kivy.app import App
from kivy.clock import Clock
from kivy.animation import Animation
from kivy.properties import NumericProperty
from kivy.properties import StringProperty
from kivy.properties import ColorProperty
from kivy.properties import BooleanProperty
from kivy.animation import AnimationTransition
from kivy.utils import get_color_from_hex
from loguru import logger

from wallpaper_engine.utils.config import Config
from .wallpaper_base import WallpaperBase


settings_json = [
    {"type": "title", "title": "Sin wave wallpaper Settings"},
    {
        "type": "numeric",
        "title": "Number of rectangles",
        "section": "wallpaper",
        "key": "number_of_rect",
        "is_int": True,
    },
    {
        "type": "string",
        "title": "Primary Color",
        "desc": "color in hex",
        "section": "wallpaper",
        "key": "primary_color",
    },
    {
        "type": "string",
        "title": "Primary Color",
        "desc": "color in hex",
        "section": "wallpaper",
        "key": "secondary_color",
    },
    {
        "type": "options",
        "title": "Transition",
        "options": [
            key
            for key, values in AnimationTransition.__dict__.items()
            if type(values) == staticmethod and key[0] != "_"
        ],
        "desc": "Which Transition to use during animation",
        "section": "wallpaper",
        "key": "transition",
    },
]


class Rect(AnchorLayout):
    height_var = NumericProperty(defaultvalue=1)
    width_var = NumericProperty(defaultvalue=1)
    offset = NumericProperty(defaultvalue=1)
    animation_going_on = BooleanProperty(defaultvalue=False)
    color = ColorProperty()


class Wallpaper(WallpaperBase):
    number_of_rect = NumericProperty(defaultvalue=70)
    primary_color = ColorProperty(defaultvalue=get_color_from_hex("949494"))
    secondary_color = ColorProperty(defaultvalue=get_color_from_hex("3b3b3b"))
    transition = StringProperty("in_out_circ")

    def __init__(self):
        super(Wallpaper, self).__init__()
        self.duration = 1
        self.app = App.get_running_app()
        self.container = None
        self.config = Config(local=True, module=pathlib.Path(__file__).stem)
        self.load_config(settings_json)

    def animate(self):
        self.app = App.get_running_app()

        def animation_loop(dt: int):
            duration = self.duration
            rect_list = self.container.children
            for r in rect_list:
                offset = random.uniform(0, 1)
                anim = Animation(
                    offset=offset, transition=self.transition, duration=duration
                )
                anim.start(r)

        self.animation_loop_clock = Clock.schedule_interval(
            animation_loop, self.duration
        )

    def build(self):

        logger.debug("Building wallpaper")
        self.app = App.get_running_app()
        self.container = self.app.root.children[0].ids.container
        for i in range(self.number_of_rect):
            test_rect = Rect()
            test_rect.color = random.choice([self.primary_color, self.secondary_color])
            test_rect.width_var = 0.1 * self.container.width

            test_rect.height_var = self.container.height * random.uniform(1, 2)
            self.container.add_widget(test_rect)

    def pause(self):
        if self.playing:
            self.animation_loop_clock.cancel()
            self.playing = False

    def play(self):
        if not self.playing:
            self.animation_loop_clock()
            self.playing = True
