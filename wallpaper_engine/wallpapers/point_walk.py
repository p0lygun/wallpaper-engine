import random
import time
from math import dist

from kivy.core.window import Window
from kivy.clock import Clock
from kivy.properties import NumericProperty
from kivy.properties import ColorProperty
from kivy.properties import BooleanProperty

from kivy.uix.floatlayout import FloatLayout
from kivy.graphics import Line, InstructionGroup, Color
from kivy.utils import get_color_from_hex

from .wallpaper_base import WallpaperBase
from ..utils.logger import LoggerClass

Logger = LoggerClass(__name__)
Logger.module = "point_walk"


class Point(FloatLayout):
    pos_x = NumericProperty()
    pos_y = NumericProperty()
    x_velocity = NumericProperty()
    y_velocity = NumericProperty()
    point_size = NumericProperty()
    color = ColorProperty()
    spotlight = BooleanProperty(False)


class Wallpaper(WallpaperBase):
    primary_color = ColorProperty(defaultvalue=get_color_from_hex("949494"))
    secondary_color = ColorProperty(defaultvalue=get_color_from_hex("3b3b3b"))
    spotlight_color = ColorProperty(defaultvalue=(1, 0, 0, 1))
    time_init = NumericProperty(time.time())
    number_of_points = NumericProperty(100)

    # in pixels
    velocity = NumericProperty(60)
    line_length = NumericProperty(150)
    point_size = NumericProperty(7)

    def __init__(self):
        super(Wallpaper, self).__init__()
        self.points = list()

    def animate(self):
        Lines = InstructionGroup()
        connection = dict().fromkeys(self.points, [])
        self.canvas.before.add(Lines)

        def animation_loop(dt: int = None):
            tf = time.time()
            dt = tf - self.time_init
            Lines.clear()
            for point in self.points:
                if point.pos_x > Window.width:
                    point.pos_x += -Window.width
                elif point.pos_x < 0:
                    point.pos_x += Window.width

                if point.pos_y > Window.height:
                    point.pos_y += -Window.height
                elif point.pos_y < 0:
                    point.pos_y += Window.height
                for p in self.points:
                    if p == point:
                        continue
                    distance = dist(
                        [point.center_x, point.center_y], [p.center_x, p.center_y]
                    )
                    if distance <= self.line_length:
                        if point not in connection[p] and p not in connection[point]:
                            connection[p].append(point)
                            connection[point].append(p)

                            if point.spotlight or p.spotlight:
                                color = Color(rgba=self.spotlight_color)
                            else:
                                color = Color(rgba=self.secondary_color)

                            color.a = (self.line_length - distance) / 100
                            Lines.add(color)
                            Lines.add(
                                Line(
                                    points=(
                                        point.center_x,
                                        point.center_y,
                                        p.center_x,
                                        p.center_y,
                                    ),
                                    width=1.5,
                                )
                            )
                    else:
                        if p in connection[point]:
                            connection[point].remove(p)
                        if point in connection[p]:
                            connection[p].remove(point)

                point.pos_x += point.x_velocity * dt
                point.pos_y += point.y_velocity * dt

            self.time_init = tf

        Clock.schedule_interval(animation_loop, 1 / 60)

    def build(self):
        self.container = self.app.root.children[0].ids.container
        Logger.debug(self.container)
        for i in range(self.number_of_points):
            point = Point()
            point.pos_x = random.randint(0, Window.width)
            point.pos_y = random.randint(0, Window.height)
            point.x_velocity = (
                self.velocity * (1 if random.random() > 0.5 else -1) * random.random()
            )
            point.y_velocity = (
                self.velocity * (1 if random.random() > 0.5 else -1) * random.random()
            )
            point.color = self.primary_color
            point.point_size = self.point_size
            self.points.append(point)

        spotlight = random.choice(self.points)
        spotlight.spotlight = True
        spotlight.color = self.spotlight_color

        for point in self.points:
            self.container.add_widget(point)
