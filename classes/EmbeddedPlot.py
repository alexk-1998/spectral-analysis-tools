# file:   EmbeddedPlot.py
# author: Alex Krosney
# date:   December 18, 2022
#
# description: handles plot operations for the application.
# Exposes draw() and clear() methods for updating through the GUI.

import tkinter as tk
import tkinter.ttk as ttk

import numpy as np

import matplotlib.cm as cm
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import classes.config as config

class EmbeddedPlot() :

    def __init__(self, parent, x, y, w, h):

        # create a container for the plot
        self._frame = ttk.Frame(parent)
        self._frame.place(relx=x, rely=y, relwidth=w, relheight=h)

        # create the figure
        self._fig = Figure(figsize=(12, 12), dpi=100, tight_layout=True)
        self._fig.set_facecolor(config.widget_bg_color)
        self._plot = None

        # create a frame around canvas for visual effect
        canvas_frame_x, canvas_frame_y, canvas_frame_w, canvas_frame_h = 0.00, 0.00, 1.00, 0.80
        self._canvas_frame = ttk.Frame(self._frame, style='Bordered.TFrame')
        self._canvas_frame.place(relx=canvas_frame_x, rely=canvas_frame_y, relwidth=canvas_frame_w, relheight=canvas_frame_h)
        
        # create the canvas
        self._canvas = FigureCanvasTkAgg(self._fig, master=self._canvas_frame) 
        self._canvas.get_tk_widget().place(relx=0.01, rely=0.01, relwidth=0.98, relheight=0.98)
        self._canvas.get_tk_widget().config(bg=config.widget_bg_color)
        self._canvas.mpl_connect('motion_notify_event', self._set_temp_point)
        self._canvas.mpl_connect('button_press_event', self._set_first_point)
        self._canvas.mpl_connect('button_release_event', self._set_final_point)
        self._canvas.mpl_connect('axes_leave_event', self._axis_leave_cb)
        self._canvas.mpl_connect('figure_leave_event', self._axis_leave_cb)
        self._canvas.draw() # draw blank canvas once

        # for storing data
        self._x_pts = None
        self._y_pts_list = []
        self._y_tool_pts_list = []
        self._x_selected_pts = []
        self._y_selected_pts = []
        self._do_point_selection = False

        # create frame for placing buttons
        button_frame_x, button_frame_y, button_frame_w, button_frame_h = 0.00, 0.81, 1.00, 0.19
        self._button_frame = ttk.Frame(self._frame)
        self._button_frame.place(relx=button_frame_x, rely=button_frame_y, relwidth=button_frame_w, relheight=button_frame_h)

        # for requesting input
        entry_x, entry_y, entry_w, entry_h = 0.50, 0.00, 0.50, 0.22
        self._entry = ttk.Entry(self._button_frame)
        self._entry.place(relx=entry_x, rely=entry_y, relwidth=entry_w, relheight=entry_h)

        # initialize update button, set command in App class
        update_button_x, update_button_y, update_button_w, update_button_h = 0.00, 0.00, 0.24, 0.22
        self._update_button = ttk.Button(self._button_frame, text='Update', command=None)
        self._update_button.place(relx=update_button_x, rely=update_button_y, relwidth=update_button_w, relheight=update_button_h)
        
        # initialize save button, set command in App class
        save_button_x, save_button_y, save_button_w, save_button_h = 0.00, 0.25, 0.24, 0.22
        self._save_button = ttk.Button(self._button_frame, text='Save', command=None)
        self._save_button.place(relx=save_button_x, rely=save_button_y, relwidth=save_button_w, relheight=save_button_h)
        
        # initialize clear button
        clear_button_x, clear_button_y, clear_button_w, clear_button_h = 0.00, 0.50, 0.24, 0.22
        self._clear_button = ttk.Button(self._button_frame, text='Clear', command=self.clear)
        self._clear_button.place(relx=clear_button_x, rely=clear_button_y, relwidth=clear_button_w, relheight=clear_button_h)
        
        # initialize raw data toggle button
        self._do_raw_data = True
        raw_button_x, raw_button_y, raw_button_w, raw_button_h = 0.25, 0.00, 0.24, 0.22
        self._toggle_raw_data_button = ttk.Button(self._button_frame, text='Toggle Raw Data', command=self._toggle_raw_data)
        self._toggle_raw_data_button.place(relx=raw_button_x, rely=raw_button_y, relwidth=raw_button_w, relheight=raw_button_h)
        
        # initialize tool data toggle button
        self._do_tool_data = True
        tool_button_x, tool_button_y, tool_button_w, tool_button_h = 0.25, 0.25, 0.24, 0.22
        self._toggle_tool_data_button = ttk.Button(self._button_frame, text='Toggle Tool Data', command=self._toggle_tool_data)
        self._toggle_tool_data_button.place(relx=tool_button_x, rely=tool_button_y, relwidth=tool_button_w, relheight=tool_button_h)

        # initialize selected data toggle button
        self._do_selected_data = True
        selected_button_x, selected_button_y, selected_button_w, selected_button_h = 0.25, 0.50, 0.24, 0.22
        self._toggle_selected_data_button = ttk.Button(self._button_frame, text='Toggle Selections', command=self._toggle_selected_data)
        self._toggle_selected_data_button.place(relx=selected_button_x, rely=selected_button_y, relwidth=selected_button_w, relheight=selected_button_h)
        
        # initialize title set button
        self._title = ''
        title_button_x, title_button_y, title_button_w, title_button_h = 0.50, 0.25, 0.16, 0.22
        self._title_button = ttk.Button(self._button_frame, text='Set Title', command=self._set_title)
        self._title_button.place(relx=title_button_x, rely=title_button_y, relwidth=title_button_w, relheight=title_button_h)
        
        # initialize x-label set button
        self._x_label = ''
        x_label_button_x, x_label_button_y, x_label_button_w, x_label_button_h = 0.67, 0.25, 0.16, 0.22
        self._x_label_button = ttk.Button(self._button_frame, text='Set X Label', command=self._set_x_label)
        self._x_label_button.place(relx=x_label_button_x, rely=x_label_button_y, relwidth=x_label_button_w, relheight=x_label_button_h)
        
        # initialize x-limit set button
        self._x_lim_min = 0
        self._x_lim_max = 0
        x_lim_button_x, x_lim_button_y, x_lim_button_w, x_lim_button_h = 0.67, 0.50, 0.16, 0.22
        self._x_lim_button = ttk.Button(self._button_frame, text='Set X Limits', command=self._set_x_limits)
        self._x_lim_button.place(relx=x_lim_button_x, rely=x_lim_button_y, relwidth=x_lim_button_w, relheight=x_lim_button_h)
       
        # initialize x-tick set button
        self._x_tick_vals = []
        self._x_tick_strs = []
        x_tick_button_x, x_tick_button_y, x_tick_button_w, x_tick_button_h = 0.67, 0.75, 0.16, 0.22
        self._x_tick_button = ttk.Button(self._button_frame, text='Set X Ticks', command=self._set_x_ticks)
        self._x_tick_button.place(relx=x_tick_button_x, rely=x_tick_button_y, relwidth=x_tick_button_w, relheight=x_tick_button_h)
        
        # initialize y-label set button
        self._y_label = ''
        y_label_button_x, y_label_button_y, y_label_button_w, y_label_button_h = 0.84, 0.25, 0.16, 0.22
        self._y_label_button = ttk.Button(self._button_frame, text='Set Y Label', command=self._set_y_label)
        self._y_label_button.place(relx=y_label_button_x, rely=y_label_button_y, relwidth=y_label_button_w, relheight=y_label_button_h)
        
        # initialize x-limit set button
        self._y_lim_min = 0
        self._y_lim_max = 0
        y_lim_button_x, y_lim_button_y, y_lim_button_w, y_lim_button_h = 0.84, 0.50, 0.16, 0.22
        self._y_lim_button = ttk.Button(self._button_frame, text='Set Y Limits', command=self._set_y_limits)
        self._y_lim_button.place(relx=y_lim_button_x, rely=y_lim_button_y, relwidth=y_lim_button_w, relheight=y_lim_button_h)
        
        # initialize x-tick set button
        self._y_tick_vals = []
        self._y_tick_strs = []
        y_tick_button_x, y_tick_button_y, y_tick_button_w, y_tick_button_h = 0.84, 0.75, 0.16, 0.22
        self._y_tick_button = ttk.Button(self._button_frame, text='Set Y Ticks', command=self._set_y_ticks)
        self._y_tick_button.place(relx=y_tick_button_x, rely=y_tick_button_y, relwidth=y_tick_button_w, relheight=y_tick_button_h)

    def draw(self, x, y_list, y_tool_pts_list=None) -> None:
        """Clears the existing plot and draws passed data."""
        valid_x = x is not None
        valid_y = len(y_list) > 0
        if valid_x and valid_y:
            self.clear(clear_selections=False)
            self._x_pts = x
            self._y_pts_list = y_list
            if y_tool_pts_list is not None:
                self._y_tool_pts_list = y_tool_pts_list
            self._draw()
        else:
            s = "Unable to produce the requested plot. Please ensure x- and y-data have been selected before plotting."
            tk.messagebox.showwarning(title=None, message=s)

    def _draw(self) -> None:
        """Internal method to clear the existing plot and draws passed data."""
        self._fig.clear()
        self._plot = self._fig.add_subplot(111)
        self._configure_plot()

        # manually choose colours for consistency in toggling
        n_colours = len(self._y_pts_list) + len(self._y_tool_pts_list)
        colours = iter(cm.rainbow(np.linspace(0, 1, n_colours)))

        # plot the raw data
        for y in self._y_pts_list:
            c = next(colours)
            if self._do_raw_data:
                length = min(len(self._x_pts), len(y))
                self._plot.plot(self._x_pts[:length], y[:length], c=c)
    
        # plot the analyzed data
        for y in self._y_tool_pts_list:
            c = next(colours)
            if self._do_tool_data:
                length = min(len(self._x_pts), len(y))
                self._plot.plot(self._x_pts[:length], y[:length], c=c)

        # plot the selection data
        if self._do_selected_data:
            if len(self._x_selected_pts) > 0 and len(self._x_selected_pts) == len(self._y_selected_pts):
                x_list = self._group_list(self._x_selected_pts.copy(), 2)
                y_list = self._group_list(self._y_selected_pts.copy(), 2)
                for x, y in zip(x_list, y_list):
                    self._plot.plot(x, y, ls='--', color='r')
        self._canvas.draw()

        # update labels if we didn't manually set them
        if len(self._x_tick_vals) == 0 or len(self._x_tick_strs) == 0:
            self._x_tick_vals = self._plot.get_xticks()
            self._x_tick_strs = self._plot.get_xticklabels()
        if len(self._y_tick_vals) == 0 or len(self._y_tick_strs) == 0:
            self._y_tick_vals = self._plot.get_yticks()
            self._y_tick_strs = self._plot.get_yticklabels()

        # update limits if we didn't manually set them
        if self._x_lim_min >= self._x_lim_max:
            self._x_lim_min, self._x_lim_max = self._plot.get_xlim()
        if self._y_lim_min >= self._y_lim_max:
            self._y_lim_min, self._y_lim_max = self._plot.get_ylim()

    def _configure_plot(self) -> None:
        """Applies all plot options to the current plot."""    
        self._configure_plot_colours()
        self._configure_plot_labels()
        self._configure_plot_ticks()
        self._configure_plot_limits()

    def _configure_plot_colours(self) -> None:
        """Set the plot background and text colours"""
        if self._plot is not None:
            self._plot.axes.set_facecolor(config.text_color)
            self._plot.xaxis.label.set_color(config.text_color)
            self._plot.yaxis.label.set_color(config.text_color)
            self._plot.set_facecolor(config.widget_bg_color)

    def _configure_plot_labels(self) -> None:
        """Set the plot and axis labels."""
        if self._plot is not None:
            self._plot.set_title(self._title)
            self._plot.set_xlabel(self._x_label)
            self._plot.set_ylabel(self._y_label)

    def _configure_plot_ticks(self) -> None:
        """Set axis ticks, if empty, let Matplotlib decide"""
        if self._plot is not None:
            self._plot.grid(True, which='both', axis='both')
            self._plot.tick_params(labelsize=12, top=True, right=True, 
                                   direction='in', which='both', 
                                   grid_color=config.grid_color)
            if len(self._x_tick_vals) > 0 or len(self._x_tick_strs) > 0:
                self._plot.set_xticks(self._x_tick_vals)
                self._plot.set_xticklabels(self._x_tick_strs)
            if len(self._y_tick_vals) > 0 or len(self._y_tick_strs) > 0:
                self._plot.set_yticks(self._y_tick_vals)
                self._plot.set_yticklabels(self._y_tick_strs)

    def _configure_plot_limits(self) -> None:
        """Set x- and y-limits, if stored max <= min then let Matplotlib decide"""
        if self._plot is not None:
            if self._x_lim_min < self._x_lim_max:
                self._plot.set_xlim(self._x_lim_min, self._x_lim_max)
            if self._y_lim_min < self._y_lim_max:
                self._plot.set_ylim(self._y_lim_min, self._y_lim_max)

    def clear(self, clear_selections=True) -> None:
        """Clears the existing plot and draws a blank canvas."""
        if self._plot is not None:
            self._plot = self._plot.clear()
            self._fig.clear()
            self._clear_data(clear_selections)
            self._clear_configs()
            self._canvas.draw()

    def _clear_data(self, clear_selections=True) -> None:
        self._x_pts = None
        self._y_pts_list = []
        self._y_tool_pts_list = []
        if clear_selections:
            self._x_selected_pts = []
            self._y_selected_pts = []

    def _clear_configs(self) -> None:
        """Returns plot configurations to their default states."""
        self._do_point_selection = False
        self._do_raw_data = True
        self._do_tool_data = True
        self._do_selected_data = True
        self._title = ''
        self._x_label = ''
        self._x_lim_min = 0
        self._x_lim_max = 0
        self._x_tick_vals = []
        self._x_tick_strs = []
        self._y_label = ''
        self._y_lim_min = 0
        self._y_lim_max = 0
        self._y_tick_vals = []
        self._y_tick_strs = []

    def save(self, filename: str) -> None:
        """Saves the existing plot."""
        self._fig.savefig(filename, bbox_inches='tight', transparent=True)

    def get_selected_points(self) -> tuple:
        """Return the selected points in the plot surface."""
        x_list = self._group_list(self._x_selected_pts.copy(), 2)
        y_list = self._group_list(self._y_selected_pts.copy(), 2)
        return x_list, y_list

    def enable_point_selection(self, do_point_selection: bool) -> None:
        """Enable/Disable point selection."""
        self._do_point_selection = do_point_selection
        # remove any existing selections and re-draw
        if self._do_point_selection:
            self._x_selected_pts = []
            self._y_selected_pts = []
            self._draw()

    def _axis_leave_cb(self, event) -> None:
        """Forces a canvas update to visually remove any temporary (but actually removed) scatter points."""
        self._clear_entry_text()
        self._canvas.draw()

    def _set_temp_point(self, event) -> None:
        """Draw a temporary line during click + drag."""
        if self._do_point_selection and event.inaxes:
            x, y = self._get_nearest(self._x_pts, self._y_pts_list, event.xdata, event.ydata)
            self._clear_entry_text()
            self._entry.insert(0, f'{x:.2f}, {y:.2f}')
            if len(self._x_selected_pts) % 2 == 0:
                scat = self._plot.scatter(x, y, s=5, color='r', zorder=10)
                self._configure_plot_limits()
                self._canvas.draw()
                scat.remove()
            else:
                lines = self._plot.plot([self._x_selected_pts[-1], x], [self._y_selected_pts[-1], y], ls='--', color='r')
                self._configure_plot_limits()
                self._canvas.draw()
                lines[0].remove()

    def _set_first_point(self, event) -> None:
        """Set the first selected point in the plot surface."""
        if self._do_point_selection and event.inaxes:
            x, y = self._get_nearest(self._x_pts, self._y_pts_list, event.xdata, event.ydata)
            self._x_selected_pts.append(x)
            self._y_selected_pts.append(y)
            self._clear_entry_text()
            self._entry.insert(0, f'{x:.2f}, {y:.2f}')

    def _set_final_point(self, event) -> None:
        """Set the last selected point in the plot surface."""
        if self._do_point_selection and event.inaxes:
            x, y = self._get_nearest(self._x_pts, self._y_pts_list, event.xdata, event.ydata)
            self._x_selected_pts.append(x)
            self._y_selected_pts.append(y)
            self._plot.plot(self._x_selected_pts[-2:], self._y_selected_pts[-2:], ls='--', color='r')
            self._canvas.draw()
            self._clear_entry_text()

    def _group_list(self, old_data: list, n: int) -> list:
        """
        Given a list, group the elements of the list into sublists of size-n.
        Example: _group_list([1, 2, 3, 4, 5, 6], 2) = [[1, 2], [3, 4], [5, 6]]
        Example: _group_list([1, 2, 3, 4, 5, 6], 3) = [[1, 2, 3], [4, 5, 6]]
        """
        new_data = []
        for i in range(0, len(old_data), n):
            new_data.append(old_data[i:i+n].copy())
        return new_data

    def _get_entry_text(self) -> str:
        """Returns the current text in the Entry box."""
        return self._entry.get()

    def _clear_entry_text(self) -> None:
        """Removes current text in the Entry box."""
        self._entry.delete(0, tk.END)

    def _toggle_raw_data(self) -> None:
        """Toggle whether the plot should display the raw data."""
        self._do_raw_data = not self._do_raw_data
        if self._plot is not None:
            self._draw()

    def _toggle_tool_data(self) -> None:
        """Toggle whether the plot should display the tool data."""
        self._do_tool_data = not self._do_tool_data
        if self._plot is not None:
            self._draw()

    def _toggle_selected_data(self) -> None:
        """Toggle whether the plot should display the selected data."""
        self._do_selected_data = not self._do_selected_data
        if self._plot is not None:
            self._draw()
    
    def _set_title(self) -> None:
        """Set the title of the plot. Gets input from the text box and clears after."""
        self._title = self._get_entry_text()
        self._configure_plot_labels()
        self._canvas.draw()
        self._clear_entry_text()

    def _set_x_label(self) -> None:
        """Set the x-axis label of the plot. Gets input from the text box and clears after."""
        self._x_label = self._get_entry_text()
        self._configure_plot_labels()
        self._canvas.draw()
        self._clear_entry_text()

    def _set_x_limits(self) -> None:
        """Set the x-axis ticks of the plot. Gets input from the text box and clears after."""
        entry = self._get_entry_text()
        self._clear_entry_text()
        # clear the current limits, let Matplotlib update to default
        if entry == '':
            self._x_lim_min = 0
            self._x_lim_max = 0
            self._draw()
        # use the passed ticks
        else:
            entry_list = entry.replace(' ', '').split(',') # remove whitespace, separate on commas
            try:
                # raises ValueError if float(entry) fails, IndexError if wrong length
                self._x_lim_min, self._x_lim_max = float(entry_list[0]), float(entry_list[1])
                if self._x_lim_min > self._x_lim_max:
                    self._x_lim_min, self._x_lim_max = self._x_lim_max, self._x_lim_min
                self._configure_plot_limits()
            except (ValueError, IndexError) as e:
                s = "Unable to set the x-axis ticks to the requested value. Please enter only comma-separated numeric values."
                tk.messagebox.showwarning(title=None, message=s)
        self._canvas.draw()

    def _set_x_ticks(self) -> None:
        """Set the x-axis ticks of the plot. Gets input from the text box and clears after."""
        entry = self._get_entry_text()
        self._clear_entry_text()
        # clear the current ticks, let Matplotlib update to default
        if entry == '':
            self._x_tick_vals = []
            self._x_tick_strs = []
            self._draw()
        # use the passed ticks
        else:
            entry_list = entry.replace(' ', '').split(',') # remove whitespace, separate on commas
            try:
                self._x_tick_vals = [float(entry) for entry in entry_list] # raises ValueError if float(entry) fails
                self._x_tick_strs = entry_list.copy()
                self._configure_plot_ticks()
            except ValueError as e:
                s = "Unable to set the x-axis ticks to the requested value. Please enter only comma-separated numeric values."
                tk.messagebox.showwarning(title=None, message=s)
        self._canvas.draw()

    def _set_y_label(self) -> None:
        """Set the y-axis label of the plot. Gets input from the text box and clears after."""
        self._y_label = self._get_entry_text()
        self._configure_plot_labels()
        self._canvas.draw()
        self._clear_entry_text()

    def _set_y_limits(self) -> None:
        """Set the y-axis ticks of the plot. Gets input from the text box and clears after."""
        entry = self._get_entry_text()
        self._clear_entry_text()
        # clear the current limits, let Matplotlib update to default
        if entry == '':
            self._y_lim_min = 0
            self._y_lim_max = 0
            self._draw()
        # use the passed ticks
        else:
            entry_list = entry.replace(' ', '').split(',') # remove whitespace, separate on commas
            try:
                # raises ValueError if float(entry) fails, IndexError if wrong length
                self._y_lim_min, self._y_lim_max = float(entry_list[0]), float(entry_list[1])
                if self._y_lim_min > self._y_lim_max:
                    self._y_lim_min, self._y_lim_max = self._y_lim_max, self._y_lim_min
                self._configure_plot_limits()
            except (ValueError, IndexError) as e:
                s = "Unable to set the y-axis ticks to the requested value. Please enter only comma-separated numeric values."
                tk.messagebox.showwarning(title=None, message=s)
        self._canvas.draw()

    def _set_y_ticks(self) -> None:
        """Set the y-axis ticks of the plot. Gets input from the text box and clears after."""
        entry = self._get_entry_text()
        self._clear_entry_text()
        # clear the current ticks, let Matplotlib update to default
        if entry == '':
            self._y_tick_vals = []
            self._y_tick_strs = []
            self._draw()
        # use the passed ticks
        else:
            entry_list = entry.replace(' ', '').split(',') # remove whitespace, separate on commas
            try:
                self._y_tick_vals = [float(entry) for entry in entry_list] # raises ValueError if float(entry) fails
                self._y_tick_strs = entry_list.copy()
                self._configure_plot_ticks()
            except ValueError as e:
                s = "Unable to set the y-axis ticks to the requested value. Please enter only comma-separated numeric values."
                tk.messagebox.showwarning(title=None, message=s)
        self._canvas.draw()

    def _get_nearest(self, x, y_list, x_pt, y_pt) -> tuple:
        """Given a set of x- and y-data, find the nearest data coordinate
        to the passed x- and y-points."""
        nearest_x = x_pt
        nearest_y = y_pt
        thresh = 0.0025 # don't snap until within thresh distance from mouse
        min_radius = 1000000 # any 'large' number
        if x is not None and len(y_list) > 0 and self._plot is not None:
            # normalize x- and y-points to plot dimensions
            min_x, max_x = self._plot.get_xlim()
            min_y, max_y = self._plot.get_ylim()
            x_pt = (x_pt - min_x) / (max_x - min_x)
            y_pt = (y_pt - min_y) / (max_y - min_y)
            for y in y_list:
                # make series consistent length
                length = min(len(x), len(y))
                x = x[:length]
                y = y[:length]
                # normalize x- and y-data to plot dimensions
                norm_x = (x - min_x) / (max_x - min_x)
                norm_y = (y - min_y) / (max_y - min_y)
                # get relative distance to selected points
                dx = norm_x - x_pt
                dy = norm_y - y_pt
                # get nearest point by minimizing radius
                radii = dx * dx + dy * dy
                min_radius_temp = radii.min()
                if min_radius_temp < thresh and min_radius_temp < min_radius:
                    index = radii.argmin()
                    if index < length:
                        nearest_x = x[index]
                        nearest_y = y[index]
                        min_radius = min_radius_temp
        return nearest_x, nearest_y
