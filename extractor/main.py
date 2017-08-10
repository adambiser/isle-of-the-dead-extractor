import os
import tkinter.tix as tix
import tkinter.ttk as ttk
from tkinter import filedialog

from .pil import CelImagePlugin
from .imageframe import ImageFrame
from .settings import Settings
from .scrolltreeview import ScrollTreeView


def _allparentpaths(path):
    paths = []
    while len(path):
        paths.insert(0, path)
        path = os.path.dirname(path)
    return paths


class MainApplication(tix.Tk):
    def __init__(self, screenName=None, baseName=None, className='Tix'):
        # Set up the window.
        tix.Tk.__init__(self, screenName, baseName, className)
        self.title('Isle of the Dead Graphics Extractor')
        self.settings = Settings()
        self.protocol("WM_DELETE_WINDOW", self._onclosing)
        # Menu
        menubar = tix.Menu(self)
        self.config(menu=menubar)
        # File menu
        filemenu = tix.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", underline=0, menu=filemenu)
        filemenu.add_command(label="Open Folder", underline=0, command=self._choosefolder, accelerator="Ctrl+O")
        self.bind_all("<Control-o>", lambda *args: self._choosefolder())
        # Option menu
        optionsmenu = tix.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Options", underline=0, menu=optionsmenu)
        optionsmenu.add_checkbutton(label="Loop Animations", underline=0, variable=self.settings.repeatanimations)
        scalemenu = tix.Menu(menubar, tearoff=0)
        optionsmenu.add_cascade(label="Image Scale", underline=0, menu=scalemenu)
        scalemenu.add_radiobutton(label="Auto", underline=0, variable=self.settings.imagescale, value=0)
        for x in range(1, 8):
            scalemenu.add_radiobutton(label=str(x), underline=0, variable=self.settings.imagescale, value=x)
        optionsmenu.add_checkbutton(label="Save Animations as GIF", underline=19)
        # Treeview
        scrolltree = ScrollTreeView(self)
        self.tree = scrolltree.tree
        self.tree.heading('#0', text='Files', anchor='w')
        self.tree.bind('<<TreeviewSelect>>', lambda *args: self._ontreeviewselect())
        self.tree.bind('<Double-Button-1>', lambda *args: self._playanimation())
        scrolltree.pack(side='left', fill='y')
        # Image viewer
        self.imageviewer = ImageFrame(self)
        self.imageviewer.pack(expand=True, fill='both', padx=0, pady=0, ipadx=0, ipady=0)
        # Finish window
        self.minsize(800, 500)
        self._centerwindow(800, 500)
        # Added focus_force because Balloon widgets mess with focus.
        self.focus_force()
        self._supportedextensions = ('.cel', '.fli')
        self.settings.gamefolder.trace("w", lambda *args: self._loadtreeview())
        self.settings.repeatanimations.trace("w", lambda  *args: self.imageviewer.repeatanimations.set(self.settings.repeatanimations.get()))
        self.settings.imagescale.trace("w", lambda  *args: self.imageviewer.imagescale.set(self.settings.imagescale.get()))
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

    def _ontreeviewselect(self):
        selectedpath = os.path.join(self.gamefolder, self.tree.focus())
        if os.path.isfile(selectedpath):
            self.imageviewer.open(selectedpath)
        else:
            self.imageviewer.clear()

    def _playanimation(self):
        self.imageviewer.toggleanimation()

    def _centerwindow(self, width, height):
        x = (self.winfo_screenwidth() - width) // 2
        y = (self.winfo_screenheight() - height) // 2
        self.geometry('{}x{}+{}+{}'.format(width, height, x, y))

    def _loadtreeview(self):
        self.imageviewer.clear()
        self.tree.delete(*self.tree.get_children())
        gamefolder = self.gamefolder
        if gamefolder is None:
            return
        addedfolders = []
        files = []
        for root, dirnames, filenames in os.walk(gamefolder):
            root = os.path.relpath(root, gamefolder)
            if root == ".":
                root = ""
            for filename in filenames:
                if filename.lower().endswith(self._supportedextensions):
                    if root and root not in addedfolders:
                        lastpath = ""
                        for path in _allparentpaths(root):
                            if path not in addedfolders:
                                self.tree.insert(lastpath, "end", iid=path, text=os.path.basename(path), open=False)
                                addedfolders.append(path)
                            lastpath = path
                    files.append(os.path.join(root, filename))
        for fullpath in files:
            root, filename = os.path.split(fullpath)
            self.tree.insert(root, 'end', iid=fullpath, text=filename)

    def _choosefolder(self):
        options = {
            "title": "Select the game folder",
            "initialdir": self.settings.gamefolder.get(),
        }
        newpath = filedialog.askdirectory(**options)
        if newpath:
            self.settings.gamefolder.set(newpath),