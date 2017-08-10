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
    * fixedscale - the image scale. automatic sizing when 0.
    """

    def __init__(self, master=None, cnf={}, **kw):
        tix.Label.__init__(self, master, cnf, **kw)
        self.config(borderwidth=0)
        self.config(background="#333")
        self.imagescale = tix.IntVar(value=0)
        self.animating = tix.BooleanVar(value=False)
        self.repeatanimations = tix.BooleanVar(value=False)
        self.animation_speed = None
        self.frames = None
        self.imagesize = None
        self.currentframe = tix.IntVar(value=-1)
        self.n_frames = tix.IntVar(value=0)
        self.bind("<Configure>", self._resize)
        self.currentframe.trace("w", self._onframechanged)
        self.animating.trace("w", self._onanimatingchanged)
        self.imagescale.trace("w", self._resize)

    def open(self, filename):
        """Opens an image file and preloads its frame(s)."""
        # Reset values
        self.currentframe.set(-1)  # set invalid to force onframechanged to fire.
        self.n_frames.set(0)
        self.config(image=[])
        self.animating.set(False)
        self.animation_speed = None
        self.frames = None
        self.imagesize = None
        if filename is None:
            return
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
            if self.animation_speed is not None:
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
        """Fires when currentframe changes. Displays the image."""
        if self.currentframe.get() == -1:
            return
        if self.imagesize is None:
            # _resize calls this method again so just return after calling it.
            self._resize([])
            return
        w, h = self.imagesize
        if w == 0 or h == 0:
            return
        currentimage = self.frames[self.currentframe.get()]
        self.photoimage = pil.ImageTk.PhotoImage(
            currentimage.resize(self.imagesize, self.imagefilter))  # keep a reference!
        self.config(image=self.photoimage)

    def _resize(self, *args):
        """Fires when the widget resizes. Calculates an aspect-corrected scale and size for the images."""
        if self.currentframe.get() == -1:
            return
        currentimage = self.frames[self.currentframe.get()]
        w, h = currentimage.size
        if self.imagescale.get() == 0:
            imagescale = min(self.winfo_width() / float(w), self.winfo_height() / float(h))
        else:
            imagescale = self.imagescale.get()
        self.imagefilter = pil.Image.NEAREST if imagescale >= 1 else pil.Image.BICUBIC
        self.imagesize = (int(w * imagescale), int(h * imagescale))
        self._onframechanged()

    def _animate(self, index):
        if not self.animating.get():
            return
        if index >= self.n_frames.get():
            if self.repeatanimations.get():
                index = 0
            else:
                self.animating.set(False)
                return
        self.currentframe.set(index)
        self.after(self.animation_speed, self._animate, index + 1)

    def _onanimatingchanged(self, *args):
        if self.animating.get():
            currentframe = self.currentframe.get()
            if currentframe == self.n_frames.get() - 1:
                self.after(0, self._animate, 0)
            else:
                self.after(0, self._animate, currentframe)
