#
# A widget to view images complete with navigation buttons, etc.
#

from .Resources import Resources
import tkinter.tix as tix
from .ImageLabel import ImageLabel

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
                        padx=0,
                        pady=0,
                        ipadx=0,
                        ipady=0)
        self.image.currentframe.trace("w", lambda *args: self._onframechanged(self.image.currentframe.get()))
        self.image.n_frames.trace("w", lambda *args: self._onframecountchanged(self.image.n_frames.get()))
        self.image.animating.trace("w", lambda *args: self._onanimating(self.image.animating.get()))
        # Prepare tooltip balloon.
        self.tooltip = tix.Balloon(master)
        for sub in self.tooltip.subwidgets_all():
            sub.config(background='#ffffe1')
        self.tooltip.subwidget('label')['image'] = tix.BitmapImage()
        # Buttons
        self.backbutton = tix.Button(self, text='Backward', command=lambda: self._navigate(-1))
        self.backbutton.image = Resources.getimage('backward.png')
        self.backbutton.config(image=self.backbutton.image)
        self.backbutton.grid(row=1,
                             column=0,
                             sticky='news',
                             )
        self.tooltip.bind_widget(self.backbutton, balloonmsg='Go back 1 frame')
        self.playbutton = tix.Button(self, text='Play', command=lambda: self.image.animating.set(not self.image.animating.get()))
        self.playbutton.image = Resources.getimage('play.png')
        self.playbutton.config(image=self.playbutton.image)
        self.playbutton.grid(row=2,
                             column=0,
                             )
        self.tooltip.bind_widget(self.playbutton, balloonmsg='Play animation')
        self.forwardbutton = tix.Button(self, text="Forward", command=lambda: self._navigate(1))
        self.forwardbutton.image = Resources.getimage('forward.png')
        self.forwardbutton.config(image=self.forwardbutton.image)
        self.forwardbutton.grid(row=1,
                                column=2,
                                sticky='news',
                                )
        # Labels
        self.framecount = tix.StringVar(value='Frames')
        self.infolabel = tix.Label(self, textvariable=self.framecount)
        self.infolabel.grid(row=1,
                            column=1,
                            sticky='news',
                            )
        # Configure grid sizing.
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)
        self.grid_columnconfigure(0, weight=1, uniform='button')
        self.grid_columnconfigure(1, weight=5)
        self.grid_columnconfigure(2, weight=1, uniform='button')

    def _navigate(self, delta):
        framenumber = self.image.currentframe.get()
        framenumber += delta
        if framenumber < 0:
            framenumber = self.image.n_frames.get() - 1
        elif framenumber >= self.image.n_frames.get():
            framenumber = 0
        self.image.currentframe.set(framenumber)

    def _onframechanged(self, framenumber):
        pass

    def _onframecountchanged(self, framecount):
        self.framecount.set("{} frames".format(framecount))
        state = tix.NORMAL if framecount > 1 else tix.DISABLED
        self.backbutton.config(state=state)
        self.forwardbutton.config(state=state)

    def open(self, filename):
        self.image.open(filename)

    def _onanimating(self, animating):
        self.playbutton.image = Resources.getimage('stop.png' if animating else 'play.png')
        self.playbutton.config(image=self.playbutton.image)
        self.tooltip.bind_widget(self.playbutton, balloonmsg=('Stop' if animating else 'Play') + ' animation')
