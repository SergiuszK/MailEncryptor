from tkinter import *

class ResizingCanvas(Canvas):
    def __init__(self, parent, isScroll, **kwargs):
        Canvas.__init__(self, parent, **kwargs)
        self.isScroll = isScroll
        if(self.isScroll == True):
            self.scrollbar = Scrollbar(
                parent, orient=VERTICAL, command=self.yview)
            self.scrollbar.pack(side=RIGHT, fill=Y)
            self.configure(yscrollcommand=self.scrollbar.set)
        self.height = self.winfo_reqheight()
        self.width = self.winfo_reqwidth()
        self.bind("<Configure>", self.onResize)

    def onResize(self, event):
        wscale = float(event.width)/self.width
        hscale = float(event.height)/self.height
        self.width = event.width
        self.height = event.height
        self.config(width=self.width, height=self.height)
        if(self.isScroll == True):
            self.configure(scrollregion=self.bbox("all"))
        self.scale("all", 0, 0, wscale, hscale)

    