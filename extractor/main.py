import os
import tkinter as tk
import tkinter.tix as tix
import tkinter.ttk as ttk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk

from .pil import CelImagePlugin, PakImagePlugin
from .imageframe import ImageFrame
from .resources import Resources
from .settings import Settings
from .scrolltreeview import ScrollTreeView
from .xmlmenu import XmlMenu


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
        self.tk.call('wm', 'iconbitmap', self._w, '-default', os.path.join(Resources.PATH, 'icon.ico'))
        self.settings = Settings()
        self.protocol("WM_DELETE_WINDOW", self._onclosing)
        # Menu
        XmlMenu(self, os.path.join(Resources.PATH, "mainmenu.xml"), globals(), locals())
        self.filemenu = XmlMenu.findmenu(self, "file")
        # Treeview
        scrolltree = ScrollTreeView(self)
        self.tree = scrolltree.tree
        self.tree.heading('#0', text='Files', anchor='w')
        self.tree.bind('<<TreeviewSelect>>', lambda *args: self._ontreeviewselect())
        self.tree.bind('<Double-Button-1>', lambda *args: self._playanimation())
        # self.tree.bind('<Button-3>', lambda *args: print("right click"))
        scrolltree.pack(side='left', fill='y')
        # Image viewer
        self.imageviewer = ImageFrame(self)
        self.imageviewer.pack(expand=True, fill='both', padx=0, pady=0, ipadx=0, ipady=0)
        # Finish window
        self.minsize(800, 500)
        self._centerwindow(800, 500)
        # Added focus_force because Balloon widgets mess with focus.
        self.focus_force()
        self._supportedextensions = ('.cel', '.fli', '.pak')
        self.settings.gamefolder.trace("w", lambda *args: self._loadtreeview())
        self.settings.repeatanimations.trace("w",
                            lambda *args: self.imageviewer.repeatanimations.set(self.settings.repeatanimations.get()))
        self.settings.imagescale.trace("w",
                            lambda *args: self.imageviewer.imagescale.set(self.settings.imagescale.get()))
        self.settings.load()
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

    def _saveimageas(self):
        options = {
            "title": "Save Image As",
            "parent": self,
            "initialdir": self.settings.exportfolder.get(),
            "confirmoverwrite": True,
            "initialfile": os.path.splitext(os.path.basename(self.tree.focus()))[0],
            "filetypes": (("PNG Files (*.png)", "*.png"),
                          ("GIF Files (*.gif)", "*.gif"),
                          ("BMP Files (*.bmp)", "*.bmp"),
                          ("All Files (*.*)", "*.*")),
            "defaultextension": ".png",
            "typevariable": self.settings.saveimagefiletype,
        }
        filename = filedialog.asksaveasfilename(**options)
        # extension = [filetype[1] for filetype in options["filetypes"] if filetype[0] == options["typevariable"].get()][0]
        if filename:
            self.imageviewer.imageview.currentframeimage.save(filename)
            self.settings.exportfolder.set(os.path.dirname(filename))

    def _saveanimationas(self):
        options = {
            "title": "Save Animation As",
            "parent": self,
            "initialdir": self.settings.exportfolder.get(),
            "confirmoverwrite": True,
            "initialfile": os.path.splitext(os.path.basename(self.tree.focus()))[0],
            "filetypes": (("Animated GIF File (*.gif)", "*.gif"),
                          ("Separate PNG Files (*.png)", "*.png"),
                          ("Separate BMP Files (*.bmp)", "*.bmp"),
                          ("All Files (*.*)", "*.*")),
            "defaultextension": ".gif",
            "typevariable": self.settings.saveanimationfiletype,
        }
        filename = filedialog.asksaveasfilename(**options)
        if filename:
            if "Animated" in options["typevariable"].get():
                self.imageviewer.imageview.image.save(filename, save_all=True)
            else:
                filename, ext = os.path.splitext(filename)
                width = len(str(self.imageviewer.imageview.n_frames.get()))
                for f in range(self.imageviewer.imageview.n_frames.get()):
                    framefile = filename + "-{0:0{width}}".format(f, width=width) + ext
                    self.imageviewer.imageview.frames[f].save(framefile)
            self.settings.exportfolder.set(os.path.dirname(filename))

    def _saveall(self):
        options = {
            "title": "Save All Files To",
            "parent": self,
            "initialdir": self.settings.exportfolder.get(),
        }
        exportfolder = filedialog.askdirectory(**options)
        if exportfolder:
            if os.listdir(exportfolder):
                options = {
                    "title": "Confirmation",
                    "message": "The folder does not appear to be empty.\nExisting files may be overwritten.\nContinue?",
                }
                if not messagebox.askyesno(**options):
                    return
            self.settings.exportfolder.set(exportfolder)
            gamefolder = self.settings.gamefolder.get()
            for root, dirnames, filenames in os.walk(gamefolder):
                relpath = os.path.relpath(root, gamefolder)
                if relpath == ".":
                    relpath = ""
                outpath = os.path.join(exportfolder, relpath)
                for filename in filenames:
                    if filename.lower().endswith(self._supportedextensions):
                        infilename = os.path.join(root, filename)
                        os.makedirs(outpath, exist_ok=True)
                        outfilebase = os.path.join(outpath, os.path.splitext(filename)[0])
                        try:
                            image = Image.open(infilename)
                            image.load()
                            try:
                                n_frames = image.n_frames
                            except AttributeError:
                                n_frames = 1
                            if n_frames > 1:
                                image.save(outfilebase + ".gif", save_all=True)
                            else:
                                image.save(outfilebase + ".bmp")
                        except Exception as ex:
                            print(ex)
                        return


    def _ontreeviewselect(self):
        selectedpath = os.path.join(self.gamefolder, self.tree.focus())
        if os.path.isfile(selectedpath):
            self.imageviewer.open(selectedpath)
            self.filemenu.entryconfig("Save Image As", state='normal')
            self.filemenu.entryconfig("Save Animation As", state='normal' if self.imageviewer.imageview.n_frames.get() > 1 else 'disabled')
        else:
            self.imageviewer.clear()
            self.filemenu.entryconfig("Save Image As", state='disabled')
            self.filemenu.entryconfig("Save Animation As", state='disabled')

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
        self.filemenu.entryconfig("Save All Files", state='disabled')
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
        if files:
            self.filemenu.entryconfig("Save All Files", state='normal')

    def _choosefolder(self):
        options = {
            "title": "Select the game folder",
            "initialdir": self.settings.gamefolder.get(),
        }
        newpath = filedialog.askdirectory(**options)
        if newpath:
            self.settings.gamefolder.set(newpath)
