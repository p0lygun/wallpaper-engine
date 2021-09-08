from kivy.uix.floatlayout import FloatLayout
from kivy.app import App


class WallpaperBase(FloatLayout):
    def __init__(self):
        super(WallpaperBase, self).__init__()
        self.app = App.get_running_app()
        self.container = None
        self.animation_loop_clock = None

    def build(self):
        pass

    def animate(self):
        pass

    def play(self):
        pass

    def pause(self):
        pass
