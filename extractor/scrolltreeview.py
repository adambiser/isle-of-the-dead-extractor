import tkinter.tix as tix
import tkinter.ttk as ttk


class ScrollTreeView(tix.Frame):
    def __init__(self, master=None, cnf={}, **kw):
        tix.Frame.__init__(self, master, cnf, **kw)
        self.config(borderwidth=2, relief='sunken')
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.tree = ttk.Treeview(self)
        self.vscrollbar = Scrollbar(self, orient='vertical', command=self.tree.yview)
        self.hscrollbar = Scrollbar(self, orient='horizontal', command=self.tree.xview)
        self.tree.configure(yscroll=self.vscrollbar.set, xscroll=self.hscrollbar.set)
        # self.tree.heading('#0', text=path, anchor='w')
        # self.hscrollbar.pack(side='bottom', fill='x')
        # self.vscrollbar.pack(side='right', fill='y')
        # self.tree.pack(side='left', fill='both')
        self.tree.grid(row=0, column=0, sticky='nsew')
        self.vscrollbar.grid(row=0, column=1, sticky='ns')
        self.hscrollbar.grid(row=1, column=0, sticky='ew')
        # self.pack()


class Scrollbar(ttk.Scrollbar):
    def set(self, first, last):
        disabled = float(first) <= 0.0 and float(last) >= 1.0
        if disabled:
            self.grid_remove()
        else:
            self.grid()
        ttk.Scrollbar.set(self, first, last)
