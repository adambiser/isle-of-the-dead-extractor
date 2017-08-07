#
# A widget to view images complete with navigation buttons, etc.
#

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
        self.image.pack(expand=True,
                        fill=tix.BOTH,
                        padx=0,
                        pady=0,
                        ipadx=0,
                        ipady=0)
        self.image.currentframe.trace("w", self._onframechanged)
        self.image.n_frames.trace("w", self._onframecountchanged)
        self.backbutton = tix.Button(self, text="<<", command=self._goback)
        self.backbutton.pack(side=tix.LEFT, anchor=tix.SW)
        self.forwardbutton = tix.Button(self, text=">>", command=self._goforward)
        self.forwardbutton.pack(side=tix.RIGHT, anchor=tix.SE)

    def _goback(self, *args):
        pass

    def _goforward(self, *args):
        pass

    def _onframechanged(self, *args):
        pass

    def _onframecountchanged(self, *args):
        pass

    def open(self, filename):
        self.image.open(filename)

    def start_animation(self):
        self.image.start_animation()

    def stop_animation(self):
        self.image.stop_animation()
