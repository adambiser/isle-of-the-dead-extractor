#
# A widget to view images complete with navigation buttons, etc.
#

from .Resources import Resources
import tkinter.tix as tix
from .ImageLabel import ImageLabel

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
        self.image = ImageLabel(self)
        self.image.grid(row=0,
                        column=0,
                        columnspan=3,
                        sticky='news',
                        )
        self.image.currentframe.trace("w", lambda *args: self._onframechanged(self.image.currentframe.get()))
        self.image.n_frames.trace("w", lambda *args: self._onframecountchanged(self.image.n_frames.get()))
        self.image.animating.trace("w", lambda *args: self._onanimating(self.image.animating.get()))
        # Prepare tooltip balloon.
        self.tooltip = tix.Balloon(self)
        for sub in self.tooltip.subwidgets_all():
            sub.config(background='#ffffe1')
        self.tooltip.subwidget('label')['image'] = tix.BitmapImage()
        # Buttons
        buttonframe = tix.Frame(self)
        buttonframe.grid(row=1, column=1)
        # first
        self.firstbutton = tix.Button(buttonframe, text='First', command=lambda: self._gotoframe(0))
        self.firstbutton.image = Resources.getimage('first.png')
        self.firstbutton.config(image=self.firstbutton.image)
        self.firstbutton.pack(side='left')
        self.tooltip.bind_widget(self.firstbutton, balloonmsg='Go back to the first frame')
        # back
        self.backbutton = tix.Button(buttonframe, text='Backward', command=lambda: self._navigate(-1))
        self.backbutton.image = Resources.getimage('backward.png')
        self.backbutton.config(image=self.backbutton.image)
        self.backbutton.pack(side='left')
        self.tooltip.bind_widget(self.backbutton, balloonmsg='Go back one frame')
        # play
        self.playbutton = tix.Button(buttonframe, text='Play', command=lambda: self.image.animating.set(not self.image.animating.get()))
        self.playbutton.image = Resources.getimage('play.png')
        self.playbutton.config(image=self.playbutton.image)
        self.playbutton.pack(side='left')
        self.tooltip.bind_widget(self.playbutton, balloonmsg='Play animation')
        # forward
        self.forwardbutton = tix.Button(buttonframe, text="Forward", command=lambda: self._navigate(1))
        self.forwardbutton.image = Resources.getimage('forward.png')
        self.forwardbutton.config(image=self.forwardbutton.image)
        self.forwardbutton.pack(side='left')
        self.tooltip.bind_widget(self.forwardbutton, balloonmsg='Go forward one frame')
        # last
        self.lastbutton = tix.Button(buttonframe, text='Last', command=lambda: self._gotoframe(self.image.n_frames.get() - 1))
        self.lastbutton.image = Resources.getimage('last.png')
        self.lastbutton.config(image=self.lastbutton.image)
        self.lastbutton.pack(side='left')
        self.tooltip.bind_widget(self.lastbutton, balloonmsg='Go back to the last frame')
        # frame number label
        self.framecount = tix.StringVar(value='')
        self.infolabel = tix.Label(self, textvariable=self.framecount)
        self.infolabel.grid(row=1,column=2)
        # Configure grid sizing.
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)
        self.grid_columnconfigure(0, weight=1, uniform='side')
        self.grid_columnconfigure(1, weight=0)
        self.grid_columnconfigure(2, weight=1, uniform='side')

    def open(self, filename):
        self.image.open(filename)

    def _navigate(self, delta):
        framenumber = self.image.currentframe.get()
        framenumber += delta
        if framenumber < 0:
            framenumber = self.image.n_frames.get() - 1
        elif framenumber >= self.image.n_frames.get():
            framenumber = 0
        self._gotoframe(framenumber)

    def _gotoframe(self, framenumber):
        self.image.currentframe.set(framenumber)

    def _onframechanged(self, framenumber):
        self.firstbutton.config(state=_get_button_state(framenumber > 0))
        self.backbutton.config(state=_get_button_state(framenumber > 0))
        self.forwardbutton.config(state=_get_button_state(framenumber < self.image.n_frames.get() - 1))
        self.lastbutton.config(state=_get_button_state(framenumber < self.image.n_frames.get() - 1))
        self.framecount.set("Frame {} of {}".format(self.image.currentframe.get() + 1, self.image.n_frames.get()))

    def _onframecountchanged(self, framecount):
        self.playbutton.config(state=_get_button_state(framecount > 1))
        if framecount > 1:
            self.infolabel.grid()
        else:
            self.infolabel.grid_remove()

    def _onanimating(self, animating):
        self.playbutton.image = Resources.getimage('stop.png' if animating else 'play.png')
        self.playbutton.config(image=self.playbutton.image)
        self.tooltip.bind_widget(self.playbutton, balloonmsg=('Stop' if animating else 'Play') + ' animation')
