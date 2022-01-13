from pathlib import Path
from wallpaper_engine.wallpapers.wallpaper_base import WallpaperBase, ShaderBase

settings_json = [
    {"type": "title", "title": "Fibonacci sphere wallpaper Settings"},
]


class Wallpaper(WallpaperBase):
    def __init__(self, **kwargs):
        super().__init__()
        self.is_shader_wallpaper = True
        file_path = Path(__file__)
        self.glsl_source = Path(
            str(file_path.parent / "glsl_wallpapers" / file_path.stem) + ".glsl"
        )

    def build(self):
        s = ShaderBase()
        s.fs = self.glsl_source.read_text()
        self.add_widget(s)
