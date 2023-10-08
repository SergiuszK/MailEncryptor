import random
import ctypes
import os

user32 = ctypes.windll.user32
screensize = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)

def randomFile():
    fileDir = "./Random Source/"
    name = random.choice(os.listdir(fileDir))
    return os.path.abspath("./Random Source/"+name)

def findXCenter(canvas, item):
    coords = canvas.bbox(item)
    xOffset = (canvas.width / 2) - ((coords[2] - coords[0]) / 2)
    return xOffset