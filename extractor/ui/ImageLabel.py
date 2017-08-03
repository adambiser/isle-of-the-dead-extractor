import tkinter.tix as tix
import PIL as pil
from PIL import ImageTk

class ImageLabel(tix.Label):
    def __init__(self, master=None, cnf={}, **kw):
        tix.Label.__init__(self, master, cnf, **kw)
        self.config(borderwidth=0)
        self.original = None
        self.bind("<Configure>", self.resize)

    def open(self, filename):
        self.original = pil.Image.open(filename)
        self.image = pil.ImageTk.PhotoImage(self.original) # keep a reference!
        self.config(image=self.image)

    def resize(self, event):
        if self.original == None:
            return
        old_size = self.original.size
        new_size = (event.width, event.height)
        ratio = min(new_size[0] / float(old_size[0]), new_size[1] / float(old_size[1]))
        new_size = (int(old_size[0] * ratio), int(old_size[1] * ratio))
        image_filter = pil.Image.NEAREST if ratio >= 1 else pil.Image.BICUBIC
        self.image = pil.ImageTk.PhotoImage(self.original.resize(new_size, image_filter))
        self.config(image=self.image)
