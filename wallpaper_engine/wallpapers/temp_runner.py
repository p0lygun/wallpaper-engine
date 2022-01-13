from kivy.app import App
from kivy.clock import Clock
from kivy.lang.builder import Builder
from wallpaper_engine.wallpapers.fibonacci_sphere import Wallpaper


class Temp(App):
    def __init__(self):
        super(Temp, self).__init__()
        self.wallpaper = None

    def build(self):
        return Wallpaper()

    def on_start(self):
        Clock.schedule_once(self.start_wallpaper, 0)

    def start_wallpaper(self, dt: int):
        self.root.build()


Builder.load_file(
    r"D:\!!PROJECTS\wallpaper-engine\wallpaper_engine\wallpapers\kv\gradient.kv"
)
if __name__ == "__main__":
    Temp().run()
