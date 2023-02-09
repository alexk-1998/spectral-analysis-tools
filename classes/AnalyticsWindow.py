import tkinter as tk
import tkinter.ttk as ttk

import pandas as pd

import classes.config as config

class AnalyticsWindow(tk.Toplevel):

    def __init__(self, parent, analytics):
        super().__init__(parent)

        self.title("Analytics")
        self.config(bg=config.widget_bg_color)

        # save for later access
        self._analytics = analytics

        self._treeview = ttk.Treeview(self, columns=list(analytics.columns), show='headings', height=len(analytics))
        # add headers, prevent column expansion
        width = 100
        for column in list(analytics.columns):
            self._treeview.column(column, stretch=False, width=width)
            self._treeview.heading(column, text=column)
        # add data
        n_round = 4
        for i in range(len(analytics)):
            self._treeview.insert('', 0, values=list(analytics.iloc[i, :].round(n_round).values))
        self._treeview.grid(row=0, column=0, columnspan=len(analytics.columns), sticky=tk.NSEW)

        # add save button beneath
        self._save_button = ttk.Button(self, 
                                       text='Save', 
                                       command=self._save)
        self._save_button.grid(row=0, column=len(analytics.columns), padx=5)

    def _save(self) -> None:
        """Callback for saving the stored data"""
        allowed_types = [('csv', '*.csv')]
        filename = tk.filedialog.asksaveasfilename(filetypes=allowed_types, defaultextension=allowed_types)
        if filename is not None and filename != '':
            self._analytics.to_csv(filename, index=False)
