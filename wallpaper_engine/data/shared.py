from ..libs.storage import Storage

global storage
storage = Storage()

global colors
colors = dict()

colors['white'] = (255, 255, 255, 255)
colors['black'] = (0, 0, 0, 255)
colors['red'] = (255, 0, 0, 255)
colors['green'] = (0, 255, 0, 255)
colors['blue'] = [0, 0, 255, 255]
