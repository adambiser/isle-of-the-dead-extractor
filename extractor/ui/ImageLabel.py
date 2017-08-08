#
# A widget to view images.
#

import tkinter.tix as tix
import PIL as pil
from PIL import ImageTk

class ImageLabel(tix.Label):
    """
    A widget that displays an image that scales to fill the widget area
    while maintaining the correct aspect ratio.

    Also supports animation for multi-frame formats.

    Variables that can be traced:
    * currentframe - contains a number from 0 to n_frames or -1 if no image is displayed
    * n_frames - the number of frames in the image.
    * animating - the current animation state.
    """
    
    def __init__(self, master=None, cnf={}, **kw):
        tix.Label.__init__(self, master, cnf, **kw)
        self.config(borderwidth=0)
        self.config(background="black")
        self.animating = tix.BooleanVar(value=False)
        self.animation_speed = None
        self.frames = None
        self.imagesize = None
        self.currentframe = tix.IntVar(value=-1)
        self.n_frames = tix.IntVar(value=0)
        self.bind("<Configure>", self._resize)
        self.currentframe.trace("w", self._onframechanged)
        self.animating.trace("w", self._onanimatingchanged)

    def open(self, filename):
        # Reset values
        self.currentframe.set(-1) # set invalid to force onframechanged to fire.
        self.config(image=None)
        self.animating.set(False)
        self.animation_speed = None
        self.frames = None
        self.imagesize = None
        # Load image.
        original = pil.Image.open(filename)
        try:
            n_frames = original.n_frames
            # FLIC animation always has an extra "ring" frame at the end for looping.
            if type(original) is pil.FliImagePlugin.FliImageFile:
                n_frames -= 1
            self.n_frames.set(n_frames)
        except AttributeError:
            self.n_frames.set(1)
        try:
            self.animation_speed = original.info.get('duration')
            if not self.animation_speed is None:
                self.animation_speed = int(self.animation_speed)
        except AttributeError:
            pass
        if self.animation_speed is None:
            self.animation_speed = 100
        # Preload all frames.
        self.frames = []
        for x in range(self.n_frames.get()):
            original.seek(x)
            original.load()
            self.frames.append(original.copy())
        # Load first frame.
        self.currentframe.set(0)

    def _onframechanged(self, *args):
        if self.currentframe.get() == -1:
            return
        if self.imagesize is None:
            # _resize calls this method again so just return after calling it.
            self._resize([])
            return
        w,h = self.imagesize
        if w == 0 or h == 0:
            return
        currentimage = self.frames[self.currentframe.get()]
        self.photoimage = pil.ImageTk.PhotoImage(currentimage.resize(self.imagesize, self.imagefilter)) # keep a reference!
        self.config(image=self.photoimage)

    def _resize(self, event):
        if self.currentframe.get() == -1:
            return
        currentimage = self.frames[self.currentframe.get()]
        w,h = currentimage.size
        imagescale = min(self.winfo_width() / float(w), self.winfo_height() / float(h))
        self.imagefilter = pil.Image.NEAREST if imagescale >= 1 else pil.Image.BICUBIC
        self.imagesize = (int(w * imagescale), int(h * imagescale))
        self._onframechanged()

    def _animate(self, index):
        if not self.animating.get():
            return
        if index >= self.n_frames.get():
            self.animating.set(False)
            return
        self.currentframe.set(index)
        self.after(self.animation_speed, self._animate, index + 1)

    def _onanimatingchanged(self, *args):
        if self.animating.get():
            self.after(0, self._animate, 0)
