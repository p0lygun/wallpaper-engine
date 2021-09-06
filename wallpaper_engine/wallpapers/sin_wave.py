import random
from kivy.uix.anchorlayout import AnchorLayout
from kivy.app import App
from kivy.clock import Clock
from kivy.animation import Animation
from kivy.properties import NumericProperty
from kivy.properties import ColorProperty
from kivy.properties import BooleanProperty

from kivy.utils import get_color_from_hex

from wallpaper_engine.utils.logger import LoggerClass
from .wallpaper_base import WallpaperBase

Logger = LoggerClass(__name__)
Logger.module = "Wallpaper_Sin_wave"


class Rect(AnchorLayout):
    height_var = NumericProperty(defaultvalue=1)
    width_var = NumericProperty(defaultvalue=1)
    offset = NumericProperty(defaultvalue=1)
    animation_going_on = BooleanProperty(defaultvalue=False)


class Wallpaper(WallpaperBase):
    number_of_rect = NumericProperty(defaultvalue=50)
    primary_color = ColorProperty(defaultvalue=get_color_from_hex("949494"))
    secondary_color = ColorProperty(defaultvalue=get_color_from_hex("3b3b3b"))
    dh = NumericProperty(defaultvalue=0.01)
    id = 0
    angle = NumericProperty()

    def __init__(self):
        super(Wallpaper, self).__init__()
        Logger.debug("In Wallpaper Class")
        self.duration = 1
        self.app = App.get_running_app()
        self.container = None
        self.transition = "in_out_circ"

        Logger.debug(f"app.root.ids ->  {self.app.root.ids}")

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

        Clock.schedule_interval(animation_loop, self.duration)

    def build(self):

        Logger.debug("Building wallpaper")
        self.app = App.get_running_app()
        self.container = self.app.root.children[0].ids.container
        Logger.debug(str(self.app.root.children[0].height))
        for i in range(self.number_of_rect):
            test_rect = Rect()
            test_rect.width_var = 0.1 * self.container.width

            test_rect.height_var = self.container.height * random.uniform(1, 2)
            self.container.add_widget(test_rect)
