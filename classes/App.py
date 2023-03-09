# file:   App.py
# author: Alex Krosney
# date:   December 15, 2022
#
# description: backend for the application.
# Handles GUI creation, interactivity, analysis.

import tkinter as tk
import tkinter.ttk as ttk

import numpy as np
import pandas as pd

from classes.EmbeddedPlot import EmbeddedPlot
from classes.EmbeddedTable import EmbeddedTable
from classes.AnalyticsWindow import AnalyticsWindow

import classes.config as config

class App(tk.Tk):

    NO_TOOL = 0
    STRAIGHT_LINE_CONTINUUM = 1

    # GUI window parameters
    _window_title = 'Spectral Analysis Tools'
    _window_size = '1280x720'

    # GUI table parameters
    _table_x = 0.02
    _table_y = 0.02
    _table_w = 0.47
    _table_h = 0.96

    # GUI plot parameters
    _plot_x = 0.51
    _plot_y = 0.02
    _plot_w = 0.47
    _plot_h = 0.96

    def __init__(self):
        super().__init__()
        self.bind('<Configure>', self._resize)

        # make the GUI less ugly
        self.config(bg=config.bg_color)
        self._style = ttk.Style(self)
        self._style.theme_use('default')
        self._configure_widgets()

        # initialize the window
        self.title(self._window_title)
        self.geometry(self._window_size)

        # initialize the GUI components
        self._table = EmbeddedTable(self, self._table_x, self._table_y, self._table_w, self._table_h)
        self._plot = EmbeddedPlot(self, self._plot_x, self._plot_y, self._plot_w, self._plot_h)
        self._plot._update_button.config(command=self._update_plot)
        self._plot._save_button.config(command=self._save_plot)

        # create the menu bar
        self._menubar = tk.Menu(self)

        # create the file menu
        self._filemenu = tk.Menu(self._menubar, tearoff=0)
        self._filemenu.add_command(label="Open", command=self._open_file)

        # create the tools menu
        self._toolmenu = tk.Menu(self._menubar, tearoff=0)
        self._toolmenu.add_command(label="Straight Line Continuum Removal",
                                   command=self._straight_line_continuum_removal_cb)
        self._toolmenu.add_separator()
        self._toolmenu.add_command(label="Run Tool", command=self._run_tool)

        # add menu bars to window
        self._menubar.add_cascade(label="File", menu=self._filemenu)
        self._menubar.add_cascade(label="Tools", menu=self._toolmenu)
        self.config(menu=self._menubar)

        self._analytics_tool = self.NO_TOOL

    def run(self) -> None:
        """Run the GUI."""
        tk.mainloop()

    def _open_file(self) -> None:
        """See EmbeddedTable.open()."""
        allowed_types = [('Excel', '*.xlsx'), ('csv', '*.csv'), ('txt', '*.txt')]
        filename = tk.filedialog.askopenfilename(filetypes=allowed_types, header=None)
        if filename is not None:
            self._table.open(filename)

    def _update_plot(self) -> None:
        """
        See EmbeddedPlot.draw().
        Pass all currently selected x, y, and point data.
        """
        self._plot.draw(self._table.get_x(), self._table.get_y())

    def _save_plot(self) -> None:
        """See EmbeddedPlot.save()."""
        allowed_types = [('PDF', '*.pdf'), ('PNG', '*.png'), ('JPEG', '*.jpeg')]
        filename = tk.filedialog.asksaveasfilename(filetypes=allowed_types, defaultextension=allowed_types)
        if filename != '' and filename.find('.') != 0: # non-empty name with filename length >= 1, not including extension
            self._plot.save(filename)

    def _clear_plot(self) -> None:
        """See EmbeddedPlot.clear()."""
        self._plot.clear()

    def _clear_data(self) -> None:
        """See EmbeddedTable.clear()."""
        self._table.clear()
        self._plot.clear()  # doesn't make sense to plot non-existent data

    def _run_tool(self) -> None:
        """Perform the active tool analysis."""
        analytics = None

        # run the straight line continuum removal tool
        if self._analytics_tool == self.STRAIGHT_LINE_CONTINUUM:
            x = self._table.get_x()
            y_list = self._table.get_y()
            x_pts, y_pts = self._plot.get_selected_points()
            self._plot.enable_point_selection(False)
            y_removed_list, analytics = self._straight_line_continuum_removal(x, y_list, x_pts, y_pts)
            self._plot.draw(x, y_list, y_removed_list)

        # display window with analytical results
        if analytics is not None:
            AnalyticsWindow(self, analytics)

    def _straight_line_continuum_removal_cb(self) -> None:
        """Perform the continuum removal calculations."""
        #self._analytics_list = None
        self._plot.enable_point_selection(True)
        self._analytics_tool = self.STRAIGHT_LINE_CONTINUUM

    def _straight_line_continuum_removal(self, x: np.array, y_list: list, x_pts: list, y_pts: list) -> list:
        """Performs continuum removal and calls all analysis functions on the resultant curve."""

        # do removal on all selected y-data
        y_removed  = []

        # currently empty data store, fill lists then add to df
        analytics = pd.DataFrame(None, columns=['band fwhm', 'band min', 
                                                'band centre', 'band depth',
                                                'band area', 
                                                'x min', 'x max',
                                                'y min', 'y max'])
        band_fwhms   = []
        band_minima  = []
        band_centres = []
        band_depths  = []
        band_areas   = []
        x_minima     = []
        x_maxima     = []
        y_minima     = []
        y_maxima     = []

        for y in y_list:

            # get x-, y-data for analysis
            length = min(len(x), len(y))
            y_raw = y[:length]                # actual y-values
            y_continuum = np.ones_like(y_raw) # temporarily set all values to 1, do removal below
            x_continuum = x[:length]          # get corresponding x-data

            # iterate over removal points and do relative reflectance only between consecutive points
            for x_pt, y_pt in zip(x_pts, y_pts):

                # get min/max values, swap if max < min
                x_pt_min = x_pt[0]
                x_pt_max = x_pt[1]
                y_pt_min = y_pt[0]
                y_pt_max = y_pt[1]
                if x_pt_min > x_pt_max:
                    x_pt_min, x_pt_max = x_pt_max, x_pt_min
                    y_pt_min, y_pt_max = y_pt_max, y_pt_min

                # get the continuum mask
                mask = (x_continuum >= x_pt_min) & (x_continuum <= x_pt_max)
                # do continuum removal
                straight_line = np.linspace(y_pt_min, y_pt_max, len(x_continuum[mask]))
                y_continuum[mask] = y_raw[mask] / straight_line
                y_continuum[y_continuum > 1] = 1

                # analysis calculations
                band_fwhms.append(self._continuum_band_fwhm(x_continuum[mask], y_continuum[mask]))
                band_minima.append(self._continuum_band_min(y_continuum[mask]))
                band_centres.append(self._continuum_band_centre(x_continuum[mask], y_continuum[mask]))
                band_depths.append(self._continuum_band_depth(y_raw[mask], y_continuum[mask]))
                band_areas.append(self._continuum_band_area(x_continuum[mask], y_continuum[mask]))
                x_minima.append(x_pt_min)
                x_maxima.append(x_pt_max)
                y_minima.append(y_pt_min)
                y_maxima.append(y_pt_max)

            # append continuum-removed curve
            y_removed.append(y_continuum)

        # populate the dataframe from the lists
        analytics['band fwhm']   = band_fwhms
        analytics['band min']    = band_minima
        analytics['band centre'] = band_centres
        analytics['band depth']  = band_depths
        analytics['band area']   = band_areas
        analytics['x min']       = x_minima
        analytics['x max']       = x_maxima
        analytics['y min']       = y_minima
        analytics['y max']       = y_maxima

        return y_removed, analytics

    def _continuum_band_fwhm(self, x: np.array, y: np.array) -> float:
        """
        Returns the full-width half-maximum of a given curve.
        fwhm is the x-width between the y-midpoints of a curve.
        """
        retval = -1
        try:
            # get y-curve half-value and minima index
            y_min_idx = y.argmin()
            y_half = (y.max() + y.min()) / 2
            # get x-value at minima
            x_mid = x[y_min_idx]
            # get x-value at closest value on minima LHS
            y_lhs_idx = (np.abs(y[x < x_mid] - y_half)).argmin()
            x_lhs = x[y_lhs_idx]
            # get x-value at closest value on minima RHS
            y_rhs_idx = (np.abs(y[x > x_mid] - y_half)).argmin() + len(y[x <= x_mid])
            x_rhs = x[y_rhs_idx]
            retval = x_rhs - x_lhs
        except ValueError as e:
            pass
        return retval

    def _continuum_band_min(self, y: np.array) -> float:
        """Returns the minimum value of a curve."""
        return y.min()

    def _continuum_band_centre(self, x: np.array, y: np.array) -> float:
        """Returns the x-value at the minimum value of a curve."""
        return x[y.argmin()]

    def _continuum_band_depth(self, y_raw: np.array, y_cont: np.array) -> float:
        """
        Returns the band depth.
        Band depth is (Rc - Rb) / Rc
        where Rc is the reflectance of the continuum at band centre and
        Rb is the band reflectance at band centre.
        """
        band_centre_idx = y_cont.argmin()
        return 1 - y_raw[band_centre_idx] / y_cont[band_centre_idx]

    def _continuum_band_area(self, x: np.array, y: np.array) -> float:
        """Returns the upper area of a constrained curve."""
        # boxed area around the removed curve
        box_area = np.trapz(np.ones_like(y), x=x)
        # area underneath the curve
        under_area = np.trapz(y, x=x)
        # area between curve and y=1
        return box_area - under_area

    def _configure_widgets(self):
        """
        Bundles widget configuration methods for code simplicity.
        """
        self._configure_button()
        self._configure_frame()
        self._configure_entry()
        self._configure_scrollbar()
        self._configure_treeview()

    def _configure_button(self):
        """
        Handles configuration of button styling.
        """
        self._style.configure('TButton', 
                    background=config.widget_bg_color, 
                    foreground=config.text_color,
                    highlightthickness=0)

    def _configure_frame(self):
        """
        Handles configuration of frame styling.
        """
        self._style.configure('Bordered.TFrame', 
                    background=config.widget_bg_color,
                    borderwidth=config.border_width,
                    relief=config.relief)
        self._style.configure('TFrame', 
                    background=config.bg_color, 
                    borderwidth=0)

    def _configure_entry(self):
        """
        Handles configuration of entry styling.
        """
        self._style.configure('TEntry',
                    fieldbackground=config.widget_bg_color,
                    borderwidth=config.border_width,
                    relief=config.relief)

    def _configure_scrollbar(self):
        """
        Handles configuration of entry styling.
        """
        self._style.configure('Vertical.TScrollbar',
                    background=config.bg_color,
                    troughcolor=config.widget_bg_color,
                    highlightcolor=config.bg_color)
        self._style.configure('Horizontal.TScrollbar',
                    background=config.bg_color,
                    troughcolor=config.widget_bg_color,
                    highlightcolor=config.bg_color)
        # disable up/down arrows
        self._style.layout('Vertical.TScrollbar', 
                    [('Vertical.Scrollbar.trough',
                    {'children': [('Vertical.Scrollbar.thumb', 
                    {'expand': '1', 'sticky': 'nswe'})],
                    'sticky': 'nsew'})])
        self._style.layout('Horizontal.TScrollbar', 
                    [('Vertical.Scrollbar.trough',
                    {'children': [('Vertical.Scrollbar.thumb', 
                    {'expand': '1', 'sticky': 'nswe'})],
                    'sticky': 'nsew'})])

    def _configure_treeview(self):
        """
        Handles configuration of treeview styling.
        """
        self._style.configure('Treeview',
                    background=config.widget_bg_color,
                    foreground=config.text_color,
                    fieldbackground=config.widget_bg_color)

    def _resize(self, event):
        """
        This is a resize callback used for the entire app frame.
        We use this method to call other resizing methods since each widget
        callback does the exact same calculation for a given class.
        """
        # all widgets receive this callback, so only resize the button if the main GUI is resized
        if event.widget == self:
            self._resize_button(event.width, event.height)

    def _resize_button(self, width, height):
        """Resize the button text based on the button dimensions."""
        max_font_size = 12
        rel_w = width / 125   # found by trial and error
        rel_h = height / 70   # 720 * 125 / 1280 (scaled by default res.)
        font_size = int(min(rel_w, rel_h))
        if font_size > max_font_size:
            font_size = max_font_size
        font = (None, font_size)
        self._style.configure('TButton', font=font)
