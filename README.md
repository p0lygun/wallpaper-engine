# Wallpaper Engine
# Currently Windows Only
Hi, there this project lets you set a [kivy](https://kivy.org/) Window as your wallpaper. What does that mean ?

Anything you can make in Kivy can be set as you wallpaper (given it does not require user input)

## A few of the current available wallpapers
[![Wallpaper_engine_showcase](https://i.imgur.com/rnKPpAo.png)](https://youtu.be/MnW2TFL00b8)

------------

## Installation  

### only tested on [CPython](https://www.python.org/)

installing Wallpaper Engine  is very easy 

First install [Poetry](https://python-poetry.org/) (it's an awesome package manager for python)  

  clone this repo and cd into dir

	git clone "https://github.com/p0lygun/wallpaper-engine.git" && cd wallpaper-engine
	
  Install required packages using poetry

	poetry install  

  RUN !!!

	poetry run python wallpaper_engine    
	
 
That's it. The wallpaper-engine is now installed, you should see a window like this  

![image](https://user-images.githubusercontent.com/22869882/134038091-7ec94b3a-501e-458c-830c-80a9c05b34d9.png)

To choose a wallpaper click on `Show settings` and choose a wallpaper

The wallpaper is updated when you click on `Change/Reload wallpaper` in the main menu (You need to press this button when u start the program or change the wallpaper)

Each wallpaper comes with its onw settings, to change the go to the `wallpaper settings` section in settings  

settings are updated as soon as you enter the value and close the pop-up  

------------

## Making you own wallpaper

if you want to make you own wallpaper its very easy  

but first you should make familiar with the directory structure   

```py
D:.
  \---wallpaper_engine  # main app folder
      |
      +---data          # runtime data is stored here
      |
      +---libs          # contains main libs (kivy manager, menu ...)
      |   +---kv        # kv lang files for each lib
      |
      +---utils         # contaings things that are used by both menu and kivy manager
      |
      +---wallpapers    # contains all the wallpapers and there configs, and kv lang files
      |   +---configs
      |   +---kv
```
so to make a new wallpaper make a new file in wallpaper directory `(the file name must follow snake case i.e snake_case)`  

then in `wallpapers\kv` make a kv file with name `snakecase.kv`

> so If your wallpaper name is `my_wallpaper.py` its kv file name will be `mywallpaper.kv` 

Ok  now lets make a Wallpaper

### I will use [starfield](https://github.com/p0lygun/wallpaper-engine/blob/main/wallpaper_engine/wallpapers/starfield.py) and [starfeild.kv](https://github.com/p0lygun/wallpaper-engine/blob/main/wallpaper_engine/wallpapers/kv/starfield.kv) as an example

Now any wallpaper has a `Wallpaper` Class that inherits from `WallpaperBase`
So this is the main class for any wallpaper and only this will be called by `kivy_manager`

Each kivy file also must contain the following kv code 
```
<Wallpaper>:
    size_hint : (1,1)
    canvas.before:
        Color:
            rgba: self.background_color
        Rectangle:
            pos: (0,0)
            size: self.size
    FloatLayout:
        size_hint : (1,1)
        id : container
```

now each `Wallpaper` class gets two function from WallpaperBase that one must override  
`build` & `animate`.  

[`build`](https://github.com/p0lygun/wallpaper-engine/blob/main/wallpaper_engine/wallpapers/starfield.py#L80) is the function where you should add widgets to your class (In the floatlayout which has `id:container`)  

[`animate`](https://github.com/p0lygun/wallpaper-engine/blob/main/wallpaper_engine/wallpapers/starfield.py#L61) is the function where all the animation will happen this function is called only once  

So you shuld handle the animation in your wallpaper using `Animation` or using `Clock.schedule_interval` or `Clock.schedule_once` or a combination of all three

>If you use `Clock.schedule_interval` as your main animation driver set the `self.animation_loop_clock` to the `schedule_interval`  
>Example [point_walk.py#L199](https://github.com/p0lygun/wallpaper-engine/blob/main/wallpaper_engine/wallpapers/point_walk.py#L199) 
>and set `self.playing = True`

No matter how you handle the animation try to implement (or override) function for [`play`](https://github.com/p0lygun/wallpaper-engine/blob/main/wallpaper_engine/wallpapers/point_walk.py#L230) and [`pause`](https://github.com/p0lygun/wallpaper-engine/blob/main/wallpaper_engine/wallpapers/point_walk.py#L225) so that the kivy_manager can pause your wallpaper when your desktop is not in focus

## Making wallpaper config and Settings

> #### You need to do this only if you want to save settings to disk 

To make a config for your wallpaper 
define the `__init__` as [defined](https://github.com/p0lygun/wallpaper-engine/blob/main/wallpaper_engine/wallpapers/starfield.py#L55)

the `Config` object takes two optional args `local` and `module` 

> local means that this a personal config not a gloabal one
> module take the file name as the value (`pathlib.Path(__file__).stem`)

To make a settings panel we use the same format as [kivy settings](https://kivy.org/doc/stable/api-kivy.uix.settings.html#create-a-panel-from-json) 
you just need to make a Json 

here is an example 
```py
settings_json = [
    {"type": "title", "title": "Star Field wallpaper Settings"},
    {
        "type": "string",
        "title": "Star Color",
        "desc": "Color of the stars (Hex)",
        "section": "wallpaper",
        "key": "star_color",
    },
    {
        "type": "string",
        "title": "Background Color",
        "desc": "Background Color (Hex)",
        "section": "wallpaper",
        "key": "background_color",
    },
]
```
each dict in the list must have section `wallpaper` and the keys must be [class variables](https://github.com/p0lygun/wallpaper-engine/blob/main/wallpaper_engine/wallpapers/starfield.py#L48) that you want to save to disk

>if there is a interger in the variables use [`is_int`](https://github.com/p0lygun/wallpaper-engine/blob/main/wallpaper_engine/wallpapers/point_walk.py#L62) to mark that variable as an integer 

Then at last call `self.load_settings` with the `settings_json` as the first argument

now you have settings and save to disk done !!!

I know all this can be tough to understand at first so you can DM me anytime on [Discord](https://discord.com/users/338947895665360898) or join [Kivy discord server](https://chat.kivy.org)


