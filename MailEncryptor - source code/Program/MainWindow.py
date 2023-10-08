from tkinter import *
from Canvas import *
from math import *
from Functions import *
from tkinter import messagebox
import sys
from math import *
from Database import *
from os.path import exists
from Canvas import *

class MainWindow:
    def __init__(self):
        self.root = Tk()
        self.root.minsize(int(screensize[0]/3), int(screensize[1]/3))
        self.root.iconbitmap("Files/icon.ico")
        self.root.state('zoomed')
        self.root.protocol("WM_DELETE_WINDOW", self.onClosing)
        myframe = Frame(self.root)
        myframe.pack(fill=BOTH, expand=YES)
        self.width = screensize[0]
        self.height = screensize[1]
        self.canvas = ResizingCanvas(
            myframe, False, width=screensize[0], height=screensize[1], bg="#18191A", highlightthickness=0)
        self.canvas.pack(fill=BOTH, expand=YES)

    def onClosing(self):
        if messagebox.askokcancel("Wyjście", "Czy chcesz zamknąć aplikację?"):
            self.root.destroy()
            sys.exit(0)
    
    def destroy(self):
        self.canvas.delete()
        self.root.destroy()

    def startLoop(self):
        self.root.mainloop()
    
    def stopLoop(self):
        self.root.quit()