import os
import tkinter.tix as tix


class Resources(object):
    _path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "resources")

    @classmethod
    def getimage(cls, filename):
        return tix.PhotoImage(file=os.path.join(Resources._path, filename))
