from Canvas import *
from math import *
from Account import *
from Functions import *

class TopWindow:
    def __init__(self,ifScroll):
        self.root = Toplevel()
        self.root.iconbitmap("Files/icon.ico")
        self.root.minsize(150, 100)
        self.root.geometry(
            str(int(screensize[0]/2))+"x"+str(int(screensize[1]/2)))
        myframe = Frame(
            self.root, width=screensize[0]/2, height=screensize[1]/2)
        myframe.pack(fill=BOTH, expand=YES)
        self.width = screensize[0]
        self.height = screensize[1]
        self.canvas = ResizingCanvas(
            myframe, ifScroll, width=screensize[0]/2, height=screensize[1]/2, bg="#18191A", highlightthickness=0)
        self.canvas.pack(fill=BOTH, expand=YES)
        self.root.protocol("WM_DELETE_WINDOW", self.closeWindow)

    def closeWindow(self):
        self.root.destroy()

    def startLoop(self):
        self.root.mainloop()