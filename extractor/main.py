import os
import tkinter.tix as tix
import tkinter.ttk as ttk
import PIL as pil
from PIL import Image,ImageTk

from .pil import CelImagePlugin
from .imageframe import ImageFrame
from .settings import Settings

class MainApplication(tix.Tk):
    def __init__(self, screenName=None, baseName=None, className='Tix'):
        # Set up the window.
        tix.Tk.__init__(self, screenName, baseName, className)
        self.title('Isle of the Dead Graphics Extractor')
        self.settings = Settings()
        self.protocol("WM_DELETE_WINDOW", self._onclosing)
        # Treeview
        self.tree = ttk.Treeview(self)
        self.tree.heading('#0', text='Files')
        self.tree.bind('<<TreeviewSelect>>', self._ontreeviewselect)
        self.tree.bind('<Double-Button-1>', self._playanimation)
        self.tree.pack(side='left', fill='y')
        # Image viewer
        self.imageviewer = ImageFrame(self)
        self.imageviewer.pack(expand=True, fill='both', padx=0, pady=0, ipadx=0, ipady=0)
        # Finish window
        self.minsize(700, 500)
        self._centerwindow(700, 500)
        # Added focus_force because Balloon widgets mess with focus.
        self.focus_force()
        self._supportedextensions = ('.cel', '.fli')
        self.settings.gamefolder.trace("w", lambda *args: self._loadtreeview())
        # Force the initial load.
        self._loadtreeview()

    @property
    def gamefolder(self):
        return self.settings.gamefolder.get()

    @gamefolder.setter
    def gamefolder(self, value):
        self.settings.gamefolder.set(value)

    def _onclosing(self):
        self.settings.save()
        self.destroy()

    def _ontreeviewselect(self, event):
        selectedpath = os.path.join(self.gamefolder, self.tree.focus())
        if os.path.isfile(selectedpath):
            self.imageviewer.open(selectedpath)
        else:
            self.imageviewer.clear()

    def _playanimation(self, event):
        self.imageviewer.toggleanimation()

    def _centerwindow(self, width, height):
        x = (self.winfo_screenwidth() - width) // 2
        y = (self.winfo_screenheight() - height) // 2
        self.geometry('{}x{}+{}+{}'.format(width, height, x, y))

    def _loadtreeview(self):
        self.tree.delete(*self.tree.get_children())
        path = self.gamefolder
        if path is None:
            return
        for root, dirnames, filenames in os.walk(path):
            root = os.path.relpath(root, path)#.replace("\\", "/")
            addedfolder = False
            for filename in filenames:
                if filename.lower().endswith(self._supportedextensions):
                    if not addedfolder:
                        self.tree.insert('', 'end', iid=root, text=root, open=False)
                        addedfolder = True
                    self.tree.insert(root, 'end', iid=os.path.join(root, filename), text=filename)
