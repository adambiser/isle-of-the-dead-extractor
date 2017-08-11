import json
import tkinter as tk
from collections import OrderedDict


class JsonMenu:
    """This builds a window's menu structure from a json file."""

    def __init__(self, master, filename, globals, locals):
        self.globals = globals
        self.locals = locals
        with open(filename, "r") as f:
            parentmenudict = json.load(f, object_pairs_hook=OrderedDict)
        parentmenu = tk.Menu(master, tearoff=0, name="menubar")
        master.config(menu=parentmenu)
        self._loadmenufromdict(master, parentmenu, parentmenudict)


    def _safeeval(self, _menuitemdict, _key, _default=None):
        _value = _menuitemdict.get(_key)
        if _value and isinstance(_value, str):
            try:
                _value = eval(_value, self.globals, self.locals)
            except NameError:
                pass
        if _value is None:
            return _default
        return _value


    def _loadmenufromdict(self, master, _parentmenu, _parentmenudict):
        for _name in _parentmenudict.keys():
            _menuitemdict = _parentmenudict.get(_name)
            _label = str(_name)
            _underline = _label.find("&")
            if _underline >= 0:
                _label = _label.replace("&", "")
            else:
                _underline = None
            _arglist = [("tearoff", 0)]
            _args = {_arg[0]: self._safeeval(_menuitemdict, *_arg) for _arg in _arglist}
            _menuitem = tk.Menu(_parentmenu, name=_label.replace(" ", "_").lower(), **_args)
            if _menuitemdict.get("children"):
                _parentmenu.add_cascade(label=_label, underline=_underline, menu=_menuitem)
                self._loadmenufromdict(master, _menuitem, _menuitemdict.get("children"))
            else:
                _menutype = _menuitemdict.get("type", "command")
                if _menutype == "command":
                    _addmethod = _parentmenu.add_command
                    _arglist = ["command"]
                elif _menutype == "check":
                    _addmethod = _parentmenu.add_checkbutton
                    _arglist = ["variable"]
                elif _menutype == "radio":
                    _addmethod = _parentmenu.add_radiobutton
                    _arglist = ["variable", "value"]
                elif _menutype == "separator":
                    _parentmenu.add_separator()
                    continue
                else:
                    raise Exception("Unsupported menutype: " + _menutype)
                _arglist.append("accelerator")
                _args = { _arg: self._safeeval(_menuitemdict, _arg) for _arg in _arglist}
                _addmethod(label=_label, underline=_underline, **_args)
                # Add binding to match accelerator key.
                if _args.get("accelerator") is not None:
                    bind = self._safeeval(_menuitemdict, "bind")
                    eventname = (bind if bind else _args.get("accelerator").lower().replace("ctrl+", "Control-"))
                    eventname = "<" + eventname + ">"
                    if _args.get("command") is not None:
                        master.bind_all(eventname, lambda *args, _args=_args: _args.get("command")())
                    elif _args.get("variable"):
                        if _args.get("value"):  # radio button
                            master.bind_all(eventname,
                                            lambda *args, _args=_args:
                                            _args.get("variable").set(_args.get("value")))
                        else:  # check button
                            master.bind_all(eventname,
                                            lambda *args, _args=_args:
                                            _args.get("variable").set(not _args.get("variable").get()))
