from pathlib import Path
from typing import Union

from wallpaper_engine.utils.config import Config

from wallpaper_engine.wallpapers.wallpaper_base import WallpaperBase, ShaderBase
from wallpaper_engine.utils.common import wallpaper_dir

settings_json = [
    {"type": "title", "title": "GLSL loader Settings"},
    {
        "type": "options",
        "title": "shader file",
        "key": "shader_file",
        "options": [i.stem for i in (wallpaper_dir / "glsl_wallpapers").glob("*.glsl")],
        "desc": "Shader to set as wallpaper",
        "section": "wallpaper",
    },
]


class Wallpaper(WallpaperBase):
    def __init__(self, **kwargs):
        super().__init__()
        self.is_shader_wallpaper = True
        file_path = Path(__file__)
        self.shader_file: Union[str, None] = None
        self.config = Config(local=True, module=file_path.stem)
        self.load_config(settings_json)
        if self.shader_file:
            self.glsl_source = Path(
                str(file_path.parent / "glsl_wallpapers" / self.shader_file) + ".glsl"
            )

    def build(self):
        s = ShaderBase()
        s.fs = self.glsl_source.read_text()
        self.add_widget(s)
