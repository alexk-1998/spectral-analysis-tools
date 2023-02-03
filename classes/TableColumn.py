# file:   TableColumn.py
# author: Alex Krosney
# date:   January 11, 2023
#
# description: this is an extension of the Tkinter Listbox class that
# only adds an additional index variable to avoid unnecessary searches.
# TODO: implement different display styles

from tkinter import Listbox as tkListbox
import classes.config as config

class TableColumn(tkListbox):

    def __init__(self, parent, index, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.config(background=config.widget_bg_color, 
                    foreground=config.text_color, 
                    borderwidth=0,
                    highlightthickness=0,
                    xscrollcommand=None)
        self._index = index

    def get_index(self):
        return self._index