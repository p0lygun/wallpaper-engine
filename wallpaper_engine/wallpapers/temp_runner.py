from kivy.app import App
from kivy.clock import Clock
from kivy.lang.builder import Builder
from wallpaper_engine.wallpapers.startfield import Wallpaper
from kivy.modules import inspector
from kivy.core.window import Window


class Temp(App):
    def __init__(self):
        super(Temp, self).__init__()
        self.wallpaper = None

    def build(self):
        a = Builder.load_file(
            r"D:\!!PROJECTS\wallpaper-engine\wallpaper_engine\wallpapers\kv\starfield.kv"
        )
        self.wallpaper = Wallpaper(debug=True)
        inspector.create_inspector(Window, a)
        return a

    def on_start(self):
        self.root.add_widget(self.wallpaper)
        Clock.schedule_once(self.start_wallpaper, 1 / 60.0)

    def start_wallpaper(self, dt: int):
        self.wallpaper.build()
        self.wallpaper.animate()


if __name__ == "__main__":
    Temp().run()
