from . import ImageFrame,CelImagePlugin
import os
import tkinter.tix as tix
import tkinter.ttk as ttk
import PIL as pil
from PIL import Image,ImageTk


class MainApplication(tix.Tk):
    def __init__(self, screenName=None, baseName=None, className='Tix'):
        # Set up the window.
        tix.Tk.__init__(self, screenName, baseName, className)
        self.title('Isle of the Dead Graphics Extractor')
##        self.protocol("WM_DELETE_WINDOW", self.on_closing)
##        self.settings = Settings()
        # Add widgets
        self.tree = ttk.Treeview(self)
        self.tree.heading('#0', text='Path')
        self.tree.bind('<<TreeviewSelect>>', self.open_selection)
        self.tree.bind('<Double-Button-1>', self.play_animation)
        self.tree.pack(side='left', fill='y')
        self.imageviewer = ImageFrame.ImageFrame(self)
        self.imageviewer.pack(expand=True, fill=tix.BOTH, padx=0, pady=0, ipadx=0, ipady=0)
        self.minsize(700, 500)
        self.center_window(700, 500)
        # Added focus_force because Balloon widgets mess with focus.
        self.focus_force()
        self.loadfiles('input', ('.cel', '.fli'))

    def open_selection(self, event):
        path = 'input/' + self.tree.focus()
        if os.path.isfile(path):
            self.imageviewer.open(path)
        else:
            self.imageviewer.clear()

    def play_animation(self, event):
        self.imageviewer.toggleanimation()

    def center_window(self, width, height):
        x = (self.winfo_screenwidth() - width) // 2
        y = (self.winfo_screenheight() - height) // 2
        self.geometry('{}x{}+{}+{}'.format(width, height, x, y))

    def loadfiles(self, path, extensions):
        self.tree.delete(*self.tree.get_children())
        for root, dirnames, filenames in os.walk(path):
            root = os.path.relpath(root, path)#.replace("\\", "/")
            addedfolder = False
            for filename in filenames:
                if filename.lower().endswith(extensions):
                    if not addedfolder:
                        self.tree.insert('', 'end', iid=root, text=root, open=False)
                        addedfolder = True
                    self.tree.insert(root, 'end', iid=os.path.join(root, filename), text=filename)
