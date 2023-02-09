import tkinter as tk
import tkinter.ttk as ttk

import classes.config as config

class AnalyticsWindow(tk.Toplevel):

    # treeview paramaters
    _n_round = 4 # round all values to 4 digits
    _width   = 100

    def __init__(self, parent, analytics_list):
        super().__init__(parent)

        self.title("Analytics")
        self.config(bg=config.widget_bg_color)

        # reform the data to pass to treeview
        self._analytics = self._reform_analytics(analytics_list)
        keys = list(self._analytics.keys())   # any key works here
        n = len(self._analytics[keys[0]])         # get length of lists in dict

        self._treeview = ttk.Treeview(self, columns=list(self._analytics.keys()), show='headings', height=n)
        # add headers, prevent column expansion
        for key in keys:
            self._treeview.column(key, stretch=False, width=self._width)
            self._treeview.heading(key, text=key)
        # add data
        for i in range(n):
            values = self._get_row_strs(self._analytics, i, self._n_round)
            self._treeview.insert('', 0, values=values)
        self._treeview.pack()

    def _reform_analytics(self, analytics_list: list) -> dict:
        """Class receives a list of dictionaries, convert to one dict with a list for each value."""
        # create empty lists to append to
        analytics = {}
        keys = analytics_list[0].keys()
        for key in keys:
            analytics[key] = []
        # append all data
        for analytics_orig in analytics_list:
            for key in keys:
                analytics[key].append(analytics_orig[key])
        return analytics

    def _get_row_strs(self, analytics: dict, i: int, n_round: int) -> list:
        """Return the i-th entry as a rounded string in all value lists"""
        values = []
        for key in analytics.keys():
            values.append(str(round(analytics[key][i], n_round)))
        return values
        


