import tkinter.tix as tix
import PIL as pil
from PIL import ImageTk

class ImageLabel(tix.Label):
    def __init__(self, master=None, cnf={}, **kw):
        tix.Label.__init__(self, master, cnf, **kw)
        self.config(borderwidth=0)
        self.original = None
        self.animating = False
        self.loop_animation = False
        self.animation_speed = None
        self.images = None
        self.currentframe = tix.IntVar(value=-1)
        self.n_frames = tix.IntVar(value=0)
        self.bind("<Configure>", self._resize)
        self.currentframe.trace("w", self._onframechanged)

    def open(self, filename):
        # Reset values
        self.animating = False
        self.animation_speed = None
        self.images = None
        # Load image.
        self.original = pil.Image.open(filename)
        try:
            n_frames = self.original.n_frames
            # FLIC animation always has an extra "ring" frame for looping.
            if type(self.original) is pil.FliImagePlugin.FliImageFile:
                n_frames -= 1
            self.n_frames.set(n_frames)
        except AttributeError:
            self.n_frames.set(1)
        try:
            self.animation_speed = self.original.info.get('duration')
            if not self.animation_speed is None:
                self.animation_speed = int(self.animation_speed)
        except AttributeError:
            pass
        if self.animation_speed is None:
            self.animation_speed = 100
        # Preload all image frames.
        self.currentframe.set(-1) # set invalid to force onframechanged to fire.
        self.images = []
        for x in range(self.n_frames.get()):
            self.original.seek(x)
            self.original.load()
            self.images.append(self.original.copy())
        # Load first frame.
        self.currentframe.set(0)

    def _onframechanged(self, *args):
        if self.original is None\
           or self.images is None\
           or self.currentframe.get() == -1:
            self.config(image=None)
            return
        new_size = (self.winfo_width(), self.winfo_height())
        # Widget size is 1,1 until displayed. This can cause a 0 height
        # image, which is not allowed. Just skip until later.
        if new_size == (1,1):
            self.config(image=None)
            return
        currentimage = self.images[self.currentframe.get()]
        old_size = currentimage.size
        imagescale = min(new_size[0] / float(old_size[0]), new_size[1] / float(old_size[1]))
        new_size = (int(old_size[0] * imagescale), int(old_size[1] * imagescale))
        image_filter = pil.Image.NEAREST if imagescale >= 1 else pil.Image.BICUBIC
        self.photoimage = pil.ImageTk.PhotoImage(currentimage.resize(new_size, image_filter)) # keep a reference!
        self.config(image=self.photoimage)

    def _resize(self, event):
        self._onframechanged()

    def _animate(self, index):
        if not self.animating:
            return
        if index >= self.n_frames.get():
            if self.loop_animation:
                index = 0
            else:
                self.stop_animation()
                return
        self.currentframe.set(index)
        self.after(self.animation_speed, self._animate, index + 1)

    def start_animation(self):
        if self.n_frames.get() <= 1:
            return
        self.animating = True
        self.after(0, self._animate, 0)

    def stop_animation(self):
        self.animating = False
