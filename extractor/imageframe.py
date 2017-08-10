#
# A widget to view images complete with navigation buttons, etc.
#

import tkinter.tix as tix
import tkinter.ttk as ttk

from .resources import Resources
from .imagelabel import ImageLabel


def _get_button_state(condition):
    return tix.NORMAL if condition else tix.DISABLED


class ImageFrame(tix.Frame):
    """
    A widget that displays an image, information about the image,
    and controls to animate the image or change frames for multi-image files.
    """

    def __init__(self, master=None, **options):
        tix.Frame.__init__(self, master, options)
        self.config(borderwidth=0)
        self.imageview = ImageLabel(self)
        self.imageview.grid(row=0,
                            column=0,
                            columnspan=3,
                            sticky='news',
                            )
        self.imageview.currentframe.trace("w", lambda *args: self._onframechanged())
        self.imageview.n_frames.trace("w", lambda *args: self._onframecountchanged())
        self.imageview.animating.trace("w", lambda *args: self._onanimating())
        self.repeatanimations = self.imageview.repeatanimations
        self.imagescale = self.imageview.imagescale
        self.master.bind("<Key>", self._onkey)
        # Prepare tooltip balloon.
        self.tooltip = tix.Balloon(self)
        for sub in self.tooltip.subwidgets_all():
            # Don't change the background of "." or the main Toplevel background changes, too.
            if str(sub) != ".":
                sub.config(background='#ffffe1')
        self.tooltip.subwidget('label')['image'] = tix.BitmapImage()
        # Buttons
        buttonframe = tix.Frame(self)
        buttonframe.grid(row=1, column=1)
        # first
        self.firstbutton = tix.Button(buttonframe, text='First', command=self.gotofirst)
        self.firstbutton.image = Resources.getimage('first.png')
        self.firstbutton.config(image=self.firstbutton.image)
        self.firstbutton.pack(side='left')
        self.tooltip.bind_widget(self.firstbutton, balloonmsg='Go back to the first frame')
        # back
        self.backbutton = tix.Button(buttonframe, text='Backward', command=self.gobackward)
        self.backbutton.image = Resources.getimage('backward.png')
        self.backbutton.config(image=self.backbutton.image)
        self.backbutton.pack(side='left')
        self.tooltip.bind_widget(self.backbutton, balloonmsg='Go back one frame')
        # play
        self.playbutton = tix.Button(buttonframe, text='Play', command=self.toggleanimation)
        self.playbutton.image = Resources.getimage('play.png')
        self.playbutton.config(image=self.playbutton.image)
        self.playbutton.pack(side='left')
        self.tooltip.bind_widget(self.playbutton, balloonmsg='Play animation')
        # forward
        self.forwardbutton = tix.Button(buttonframe, text="Forward", command=self.goforward)
        self.forwardbutton.image = Resources.getimage('forward.png')
        self.forwardbutton.config(image=self.forwardbutton.image)
        self.forwardbutton.pack(side='left')
        self.tooltip.bind_widget(self.forwardbutton, balloonmsg='Go forward one frame')
        # last
        self.lastbutton = tix.Button(buttonframe, text='Last', command=self.gotolast)
        self.lastbutton.image = Resources.getimage('last.png')
        self.lastbutton.config(image=self.lastbutton.image)
        self.lastbutton.pack(side='left')
        self.tooltip.bind_widget(self.lastbutton, balloonmsg='Go back to the last frame')
        # frame number label
        self.frameinfo = tix.StringVar(value='')
        self.infolabel = tix.Label(self, textvariable=self.frameinfo)
        self.infolabel.grid(row=1, column=2)
        # Configure grid sizing.
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)
        self.grid_rowconfigure(2, weight=0)
        self.grid_columnconfigure(0, weight=1, uniform='side')
        self.grid_columnconfigure(1, weight=0)
        self.grid_columnconfigure(2, weight=1, uniform='side')
        # Force these event handlers to run.
        self._onframechanged()
        self._onframecountchanged()

    def open(self, filename):
        self.imageview.open(filename)

    def clear(self):
        self.imageview.open(None)

    @property
    def currentframe(self):
        return self.imageview.currentframe.get()

    @currentframe.setter
    def currentframe(self, value):
        self.imageview.currentframe.set(value)

    @property
    def framecount(self):
        return self.imageview.n_frames.get()

    @property
    def isanimating(self):
        return self.imageview.animating.get()

    def _onkey(self, event):
        if event.keysym == "Left":
            self.gobackward()
        elif event.keysym == "Right":
            self.goforward()
        elif event.keysym == "Home":
            self.gotofirst()
        elif event.keysym == "End":
            self.gotolast()
        elif event.keysym == "space":
            self.toggleanimation()

    def gobackward(self):
        if self.currentframe > 0:
            self.currentframe -= 1

    def goforward(self):
        if self.currentframe < self.framecount - 1:
            self.currentframe += 1

    def gotofirst(self):
        self.currentframe = 0

    def gotolast(self):
        self.currentframe = self.framecount - 1

    def toggleanimation(self):
        if self.framecount > 1:
            self.imageview.animating.set(not self.isanimating)

    def _onframechanged(self):
        self.firstbutton.config(state=_get_button_state(self.currentframe > 0))
        self.backbutton.config(state=_get_button_state(self.currentframe > 0))
        self.forwardbutton.config(state=_get_button_state(0 <= self.currentframe < self.framecount - 1))
        self.lastbutton.config(state=_get_button_state(0 <= self.currentframe < self.framecount - 1))
        self.frameinfo.set("Frame {} of {}".format(self.currentframe + 1, self.framecount))

    def _onframecountchanged(self):
        self.playbutton.config(state=_get_button_state(self.framecount > 1))
        # self.repeatcheckbox.config(state=_get_button_state(self.framecount > 1))
        if self.framecount > 1:
            self.infolabel.grid()
        else:
            self.infolabel.grid_remove()

    def _onanimating(self):
        self.playbutton.image = Resources.getimage('stop.png' if self.isanimating else 'play.png')
        self.playbutton.config(image=self.playbutton.image)
        self.tooltip.bind_widget(self.playbutton, balloonmsg=('Stop' if self.isanimating else 'Play') + ' animation')
