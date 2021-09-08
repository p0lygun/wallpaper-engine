import pathlib
import json

commands = {
    "VISIBILITY": 0,
    "PAUSE": 1,
    "PLAY": 2,
    "EXIT": 3,
    "CHANGE": 5,
}

project_dir = pathlib.Path(__file__).parents[1]

wallpaper_dir = project_dir / "wallpapers"
valid_wallpapers = [
    i.stem
    for i in wallpaper_dir.glob("*.py")
    if i.name not in ["wallpaper_base.py", "__init__.py"]
]


def build_settings_json(json_data: list) -> str:
    tmp = json_data
    for item in tmp:
        if item.get("is_int"):
            item.pop("is_int")
    return json.dumps(tmp)
