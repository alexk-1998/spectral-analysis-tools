import tkinter as tk
import tkinter.ttk as ttk

import pandas as pd

import classes.config as config

class AnalyticsWindow(tk.Toplevel):

    def __init__(self, parent, analytics):
        super().__init__(parent)

        self.title("Analytics")
        self.config(bg=config.widget_bg_color)

        self._analytics = analytics

        #self._frame = ttk.Frame(self, style='Bordered.TFrame')
        #self._frame.place(relx=0.01, rely=0.01, relwidth=0.98, relheight=0.88)

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
        #self._treeview.pack(fill=tk.BOTH, expand=True, sticky)

        # add save button beneath
        self._save_button = ttk.Button(self, 
                                       text='Save', 
                                       command=self._save)
        self._save_button.grid(row=1, column=1, padx=5, pady=5)

    def _save(self):
        """Callback for saving the stored data"""
        allowed_types = [('csv', '*.csv')]
        filename = tk.filedialog.asksaveasfilename(filetypes=allowed_types, defaultextension=allowed_types)
        if filename is not None:
            self._analytics.to_csv(filename, index=False)
