import xml.etree.ElementTree as xml
import tkinter as tk


class XmlMenu:
    """This builds a window's menu structure from an xml file."""
    _SPECIAL_KEYS = {
        "`": "quoteleft",
        "~": "asciitilde",
        "!": "exclam",
        "@": "at",
        "#": "numbersign",
        "$": "dollar",
        "%": "percent",
        "^": "asciicircum",
        "&": "ampersand",
        "*": "asterisk",
        "(": "parenleft",
        ")": "parenright",
        "-": "minus",
        "_": "underscore",
        "=": "equal",
        "+": "plus",
        "{": "braceleft",
        "}": "braceright",
        "[": "bracketleft",
        "]": "bracketright",
        "\\": "backslash",
        "|": "bar",
        ";": "semicolon",
        ":": "colon",
        "'": "quoteright",
        "\"": "quotedbl",
        "<": "less",
        ">": "greater",
        ",": "comma",
        ".": "period",
        "/": "slash",
        "?": "question",
    }


    def __init__(self, master, filename, globals, locals):
        self.globals = globals
        self.locals = locals
        with open(filename, "r") as f:
            tree = xml.fromstring(f.read())
        parentmenu = tk.Menu(master, tearoff=0, name="menubar")
        master.config(menu=parentmenu)
        self._loadchildren(master, parentmenu, tree)


    def _safeeval(self, _node, _key, _default=None):
        required = _key.startswith("*")
        if required:
            _key = _key[1:]
        _value = _node.get(_key)
        if _value and isinstance(_value, str):
            try:
                _value = eval(_value, self.globals, self.locals)
            except NameError:
                pass
        if _value is None:
            if required:
                raise Exception("Node is missing a required attribute. {}.{}".format(_node.tag, _key))
            return _default
        return _value


    def _loadchildren(self, master, _parentmenu, _parentnode):
        for _node in _parentnode:
            _label, _underline, _name = self._parselabel(_node)
            _args = {"tearoff":_node.get("tearoff", 0)}
            if _node:
                _menuitem = tk.Menu(_parentmenu, name=_name, **_args)
                _parentmenu.add_cascade(label=_label, underline=_underline, menu=_menuitem)
                _parentmenu.entryconfig(_label, state=_node.get("state", 'normal'))
                self._loadchildren(master, _menuitem, _node)
            else:
                _menutype = _node.tag
                if _menutype in ("command", "menu"):
                    _addmethod = _parentmenu.add_command
                    _arglist = ["*command"]
                elif _menutype == "check":
                    _addmethod = _parentmenu.add_checkbutton
                    _arglist = ["*variable"]
                elif _menutype == "radio":
                    _addmethod = _parentmenu.add_radiobutton
                    _arglist = ["*variable", "*value"]
                elif _menutype == "separator":
                    _parentmenu.add_separator()
                    continue
                else:
                    raise Exception("Unsupported menutype: " + _menutype)
                _args = { _arg[1:] if _arg.startswith("*") else _arg: self._safeeval(_node, _arg) for _arg in _arglist}
                _args["accelerator"] = _node.get("accelerator")
                _args["state"] = _node.get("state", "normal")
                _addmethod(label=_label, underline=_underline, **_args)
                # Add binding to match accelerator key.
                eventname = self._getbindevent(_node)
                if eventname:
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


    def _parselabel(self, _node):
        _label = _node.get("label")
        if _label:
            _underline = _label.find("&")
            if _underline >= 0:
                _label = _label.replace("&", "")
            else:
                _underline = None
            _name = _label.replace(" ", "_").lower()
        else:
            _name = None
            _underline = None
        return _label, _underline, _name


    def _getbindevent(self, _node):
        event = _node.get("bind")
        if not event and _node.get("accelerator"):
            event = _node.get("accelerator").lower()
            hasctrl, event = _findandreplace(event, "ctrl+")
            hasshift, event = _findandreplace(event, "shift+")
            hasalt, event = _findandreplace(event, "alt+")
            # Convert number keys to Key-#
            if XmlMenu._SPECIAL_KEYS.get(event):
                event = XmlMenu._SPECIAL_KEYS.get(event)
            else:
                if "0" <= event <= "9":
                    event = "Key-" + event
                elif "a" <= event <= "z":
                    if hasshift:
                        event = event.upper()
                else:
                    raise Exception("Unknown key: " + event)
            if hasctrl:
                event = "Control-" + event
            if hasalt:
                event = "Alt-" + event
        if event:
            return "<" + event + ">"
        else:
            return None

    @classmethod
    def findmenu(cls, master, path):
        if not isinstance(path, list):
            path = path.split("/")
        if path[0] != "menubar":
            path.insert(0, "menubar")
        parent = master
        for child in path:
            parent = parent.children.get(child)
        return parent


def _findandreplace(string, findstring, replacestring=""):
    return string.find(findstring) >= 0, string.replace(findstring, replacestring)