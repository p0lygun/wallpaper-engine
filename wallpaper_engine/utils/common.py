import pathlib

commands = {
    "VISIBILITY": 0,
    "PAUSE": 1,
    "PLAY": 2,
    "EXIT": 3,
    "CHANGE": 5,
}

project_dir = pathlib.Path(__file__).parents[1]
