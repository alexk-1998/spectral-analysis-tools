# file:   EmbeddedTable.py
# author: Alex Krosney
# date:   December 18, 2022
#
# description: handles table operations for the application.
# TODO: implement different display styles

import platform

import tkinter as tk
import tkinter.ttk as ttk

import pandas as pd
import numpy as np

from classes.TableColumn import TableColumn
import classes.config as config

class EmbeddedTable() :

    # font params
    _text_size  = 10
    _text_round = 6 # digits to round to in table

    # x-data add button params
    _listbox_default_string = 'no data'

    def __init__(self, parent, x, y, w, h):

        # determine OS for proper scrolling on MacOS
        self._scroll_div = 120
        if platform.system() == 'Darwin':
            self._scroll_div = 1

        # create a container for the table and associated scrollbars
        self._frame = ttk.Frame(parent)
        self._frame.place(relx=x, rely=y, relwidth=w, relheight=h)

        # create the canvas frame
        canvas_frame_x, canvas_frame_y, canvas_frame_w, canvas_frame_h = 0.00, 0.00, 0.98, 0.80
        self._canvas_frame = ttk.Frame(self._frame, style='Bordered.TFrame')
        self._canvas_frame.place(relx=canvas_frame_x, rely=canvas_frame_y, relwidth=canvas_frame_w, relheight=canvas_frame_h)
        self._canvas_frame.bind("<MouseWheel>",
            lambda e: "break" if self._canvas is None else self._canvas.yview_scroll(int(-e.delta/self._scroll_div), tk.UNITS))

        # set the font and measure for table spacing
        self._font = tk.font.Font(size=self._text_size)
        self._column_width = self._font.measure('00.000000', displayof=self._canvas_frame)
        self._column_max_char = 10

        # create a vertical scrollbar
        # align to the right of the canvas with the same height
        v_scrollbar_x, v_scrollbar_y, v_scrollbar_w, v_scrollbar_h = 0.985, 0.000, 0.015, 0.800
        self._v_scrollbar = ttk.Scrollbar(self._frame, orient=tk.VERTICAL, 
                                          command=lambda *args: "break" if self._canvas is None else self._canvas.yview(*args))
        self._v_scrollbar.place(relx=v_scrollbar_x, rely=v_scrollbar_y, relwidth=v_scrollbar_w, relheight=v_scrollbar_h)
        self._v_scrollbar.bind("<ButtonPress-1>", self._scrollbar_v_click)

        # create a horizontal scrollbar
        # align beneath the table canvas with the same width
        h_scrollbar_x, h_scrollbar_y, h_scrollbar_w, h_scrollbar_h = 0.000, 0.805, 0.980, 0.015
        self._h_scrollbar = ttk.Scrollbar(self._frame, orient=tk.HORIZONTAL,
                                          command=lambda *args: "break" if self._canvas is None else self._canvas.xview(*args))
        self._h_scrollbar.place(relx=h_scrollbar_x, rely=h_scrollbar_y, relwidth=h_scrollbar_w, relheight=h_scrollbar_h)
        self._h_scrollbar.bind("<ButtonPress-1>", self._scrollbar_h_click)

        # listbox for showing active x-data
        x_listbox_x, x_listbox_y, x_listbox_w = 0.25, 0.89, 0.30
        x_listbox_rows = 3
        self._x_listbox = tk.Listbox(self._frame, justify=tk.CENTER, 
                                     selectmode=tk.SINGLE, height=x_listbox_rows, 
                                     activestyle=tk.NONE, font=self._font)
        self._x_listbox.place(relx=x_listbox_x, rely=x_listbox_y, relwidth=x_listbox_w, anchor=tk.N)
        self._x_listbox.config(background=config.widget_bg_color, foreground=config.text_color, 
                               relief=config.relief, borderwidth=config.border_width)
        self._x_listbox.insert(0, self._listbox_default_string)
        
        # listbox for showing active y-data
        y_listbox_x, y_listbox_y, y_listbox_w = 0.75, 0.89, 0.30
        y_listbox_rows = 3
        self._y_listbox = tk.Listbox(self._frame, justify=tk.CENTER, 
                                     selectmode=tk.SINGLE, height=y_listbox_rows, 
                                     activestyle=tk.NONE, font=self._font)
        self._y_listbox.place(relx=y_listbox_x, rely=y_listbox_y, relwidth=y_listbox_w, anchor=tk.N)
        self._y_listbox.config(background=config.widget_bg_color, foreground=config.text_color, 
                               relief=config.relief, borderwidth=config.border_width)
        self._y_listbox.insert(0, self._listbox_default_string)
        self._y_listbox.bind("<Up>", self._listbox_key_up)
        self._y_listbox.bind("<Down>", self._listbox_key_down)

        # initialize set x-data button
        x_set_button_x, x_set_button_y, x_set_button_w, x_set_button_h = 0.09, 0.84, 0.10, 0.04
        self._x_set_button = ttk.Button(self._frame, text="Set", command=self._set_x)
        self._x_set_button.place(relx=x_set_button_x, rely=x_set_button_y, relwidth=x_set_button_w, relheight=x_set_button_h)

        # initialize x-enter button
        x_enter_button_x, x_enter_button_y, x_enter_button_w, x_enter_button_h = 0.20, 0.84, 0.10, 0.04
        self._x_enter_button = ttk.Button(self._frame, text="Enter", command=self._enter_x)
        self._x_enter_button.place(relx=x_enter_button_x, rely=x_enter_button_y, relwidth=x_enter_button_w, relheight=x_enter_button_h)

        # initialize reset x-data button
        x_reset_button_x, x_reset_button_y, x_reset_button_w, x_reset_button_h = 0.31, 0.84, 0.10, 0.04
        self._x_reset_button = ttk.Button(self._frame, text="Reset", command=self._reset_x)
        self._x_reset_button.place(relx=x_reset_button_x, rely=x_reset_button_y, relwidth=x_reset_button_w, relheight=x_reset_button_h)
        
        # initialize set y-data button
        y_add_button_x, y_add_button_y, y_add_button_w, y_add_button_h = 0.59, 0.84, 0.10, 0.04
        self._y_add_button = ttk.Button(self._frame, text="Add", command=self._add_y)
        self._y_add_button.place(relx=y_add_button_x, rely=y_add_button_y, relwidth=y_add_button_w, relheight=y_add_button_h)

        # initialize y-enter button
        y_enter_button_x, y_enter_button_y, y_enter_button_w, y_enter_button_h = 0.70, 0.84, 0.10, 0.04
        self._y_enter_button = ttk.Button(self._frame, text="Enter", command=self._enter_y)
        self._y_enter_button.place(relx=y_enter_button_x, rely=y_enter_button_y, relwidth=y_enter_button_w, relheight=y_enter_button_h)
        
        # initialize reset y-data button
        y_delete_button_x, y_delete_button_y, y_delete_button_w, y_delete_button_h = 0.81, 0.84, 0.10, 0.04
        self._y_delete_button = ttk.Button(self._frame, text="Delete", command=self._delete_y)
        self._y_delete_button.place(relx=y_delete_button_x, rely=y_delete_button_y, relwidth=y_delete_button_w, relheight=y_delete_button_h) 

        # create a canvas for holding a number of TableColumns to form a table
        self._canvas = None
        self._table_columns = []

        # default references for data
        self._df = None
        self._indices = {}
        self._active_indices = []
        self._n_req_indices = 3

    def open(self, filename: str) -> None:
        """Open the file at the passed file path."""
        df = None
        # excel file reading
        if 'xlsx' in filename.lower():
            df = pd.read_excel(filename, header=None) 
        # csv file reading
        elif 'csv' in filename.lower():
            df = pd.read_csv(filename, sep=',', header=None)
        # txt file reading, use sep=None to infer text delimeter
        elif 'txt' in filename.lower():
            df = pd.read_csv(filename, sep=None, header=None)
        # update our existing data
        if df is not None:
            self._populate(df)

    def clear(self) -> None:
        """Clear all table and selection data."""
        if self._canvas is not None:
            self._canvas = self._canvas.destroy()
        self._table_columns = []
        self._x_listbox.delete(0, tk.END)
        self._x_listbox.insert(0, self._listbox_default_string)
        self._y_listbox.delete(0, tk.END)
        self._y_listbox.insert(0, self._listbox_default_string)
        self._df = None
        self._frame.update_idletasks()

    def get_x(self) -> np.array:
        """Return the currently selected x-data."""
        x_vals = None
        if self._df is not None and 'x' in self._indices.keys():
            x0 = self._indices['x'][0]
            x1 = self._indices['x'][1]
            col = self._indices['x'][2]
            x_vals = self._df.iloc[x0:x1, col].to_numpy()
        return x_vals

    def get_y(self) -> list:
        """Return the currently selected y-data."""
        y_vals = []
        if self._df is not None and 'y' in self._indices.keys():
            for y_index in self._indices['y']:
                y0 = y_index[0]
                y1 = y_index[1]
                col = y_index[2]
                y_vals.append(self._df.iloc[y0:y1, col].to_numpy())
        return y_vals
    
    def _validate_active_data(self) -> bool:
        """Verify the actively selected data to ensure it contains only numeric values."""
        valid = True
        # must have correct number of indices
        if len(self._active_indices) != self._n_req_indices:
            valid = False
        # verify numeric contents
        else:
            row_start = self._active_indices[0]
            row_end = self._active_indices[1]
            col = self._active_indices[2]
            if row_end <= row_start or self._df.iloc[row_start:row_end, col].isnull().any():
                valid = False
        # show warning message
        if not valid:
            s = "An invalid selection occurred. Please ensure the selected data contains only numeric values."
            tk.messagebox.showwarning(title=None, message=s)
            self._active_indices = []
        return valid

    def _set_x(self) -> None:
        """Get the active table selections and assign to the active x-data."""
        if self._validate_active_data():
            # update the stored x-indices
            self._indices['x'] = self._active_indices.copy()
            x0 = self._indices['x'][0]
            x1 = self._indices['x'][1]
            col = self._indices['x'][2]
            # delete existing text and overwrite
            s = f'col:{col+1}; row:{x0+1}-{x1}'
            self._x_listbox.delete(0)
            self._x_listbox.insert(0, s)

    def _enter_x(self) -> None:
        """Get the active table selections and assign to the active x-data."""
        return "break"

    def _add_y(self) -> None:
        """Get the active table selections and append to the active y-data."""
        if self._validate_active_data():
            # update the stored y-indices
            if 'y' in self._indices.keys():
                self._indices['y'].append(self._active_indices.copy())
            else:
                self._indices['y'] = [self._active_indices.copy()]
                self._y_listbox.delete(0) # delete default text
            y0 = self._indices['y'][-1][0]
            y1 = self._indices['y'][-1][1]
            col = self._indices['y'][-1][2]
            # delete existing text and overwrite
            s = f'col:{col+1}; row:{y0+1}-{y1}'
            self._y_listbox.insert(tk.END, s)

    def _reset_x(self) -> None:
        """Clear the currently selected x-data."""
        if 'x' in self._indices.keys():
            self._indices.pop('x')
        self._x_listbox.delete(0, tk.END)
        self._x_listbox.insert(0, self._listbox_default_string)

    def _enter_y(self) -> None:
        """Get the active table selections and assign to the active x-data."""
        return "break"

    def _delete_y(self) -> None:
        """Clear the most recent selected y-data."""
        # clear the active/bottom entry in the internal data
        if 'y' in self._indices.keys():
            y_indices = list(self._y_listbox.curselection())

            # clear selected data
            # listbox only allows one selection
            if len(y_indices) > 0:
                self._indices['y'].pop(y_indices[0])
                self._y_listbox.delete(y_indices[0])

            # clear bottom entry
            else:
                self._indices['y'].pop()
                self._y_listbox.delete(self._y_listbox.size()-1)

            # add default string back into table
            if self._y_listbox.size() == 0:
                self._y_listbox.insert(0, self._listbox_default_string)

    def _scrollbar_h_click(self, event) :
        """
        Callback for horizontal scrollbar click.
        Moves the scrollbar and canvas according to cursor position.
        """
        if self._canvas is not None:
            # get scrollbar thumb position and width relative to canvas
            thumb_width = event.widget.winfo_width() * self._canvas.winfo_width() / self._canvas.bbox(tk.ALL)[2]
            thumb_pos = (event.x - 0.5 * thumb_width) / event.widget.winfo_width()
            # set canvas position, force update for scrollbar
            self._canvas.xview_moveto(thumb_pos)
            self._canvas.update_idletasks()

    def _scrollbar_v_click(self, event) :
        """
        Callback for vertical scrollbar click.
        Moves the scrollbar and canvas according to cursor position.
        """
        if self._canvas is not None:
            # get scrollbar bar position and height relative to canvas
            thumb_height = event.widget.winfo_height() * self._canvas.winfo_height() / self._canvas.bbox(tk.ALL)[3]
            thumb_pos = (event.y - 0.5 * thumb_height) / event.widget.winfo_height()
            # set canvas position, force update for scrollbar
            self._canvas.yview_moveto(thumb_pos)
            self._canvas.update_idletasks()

    def _listbox_key_up(self, event) -> None:
        """Callback for listbox parsing with the up arrow key."""
        if event.widget.size() > 0:
            selected_indices = list(event.widget.curselection())
            if len(selected_indices) > 0 and selected_indices[0] - 1 >= 0:
                event.widget.select_clear(0, tk.END)
                event.widget.select_set(selected_indices[0] - 1)
            
    def _listbox_key_down(self, event) -> None:
        """Callback for listbox parsing with the down arrow key."""
        if event.widget.size() > 0:
            selected_indices = list(event.widget.curselection())
            if len(selected_indices) > 0 and selected_indices[0] + 1 < event.widget.size():
                event.widget.select_clear(0, tk.END)
                event.widget.select_set(selected_indices[0] + 1)

    def _populate(self, df: pd.DataFrame) -> None:
        """Populate the table with data given by the passed DataFrame"""
        if df is not None:
            self.clear()
            # replace NaNs with empty strings
            self._df = df.copy().fillna('')
            n_rows = len(df.index)
            # create canvas to display columns
            self._canvas = tk.Canvas(self._canvas_frame)
            self._canvas.config(background=config.widget_bg_color, highlightthickness=0, borderwidth=0)
            self._canvas.bind("<MouseWheel>",
                lambda e: "break" if self._canvas is None else self._canvas.yview_scroll(int(-e.delta/self._scroll_div), tk.UNITS))
            # create all columns
            self._table_columns = []
            n_cols = len(df.columns)
            for i in range(n_cols):
                column = TableColumn(self._canvas, i, justify=tk.LEFT, selectmode=tk.EXTENDED,
                                     height=0, width=0, activestyle=tk.NONE, font=self._font)
                column.bind("<MouseWheel>",
                    lambda e: "break" if self._canvas is None else self._canvas.yview_scroll(int(-e.delta/self._scroll_div), tk.UNITS))
                column.bind("<ButtonRelease-1>", self._get_table_selection)
                for j in range(n_rows):
                    try:
                        val = str(round(float(self._df.iloc[j, i]), self._text_round))
                    except ValueError as e:
                        val = self._df.iloc[j, i]
                    val = val[:self._column_max_char]
                    column.insert(j, val)
                # add column to canvas
                self._canvas.create_window(i*(self._column_width+config.text_pad), 0, height=0, width=0, window=column, anchor=tk.NW)
                self._table_columns.append(column)
            # configure the canvas
            canvas_x, canvas_y, canvas_w, canvas_h = 0.01, 0.01, 0.98, 0.98
            self._canvas.place(relx=canvas_x, rely=canvas_y, relwidth=canvas_w, relheight=canvas_h)
            self._canvas.config(yscrollcommand=self._v_scrollbar.set, 
                                xscrollcommand=self._h_scrollbar.set, 
                                scrollregion=self._canvas.bbox(tk.ALL))
            self._canvas.xview_moveto(0.0)
            self._canvas.yview_moveto(0.0)
            # force UI update
            self._frame.update_idletasks()
            # convert strings to numbers for internal data
            for i in range(len(self._df.columns)):
                self._df.iloc[:, i] = pd.to_numeric(self._df.iloc[:, i], errors='coerce')

    def _get_table_selection(self, event) -> None:
        """
        Get the actively selected column and column indices from the table.
        Returns a tuple where the first element is the column index and the second
        is a list of all active selections from within the column. The method will
        do nothing if the selected data contains non-numeric entries.
        """
        if self._df is not None:
            col = event.widget.get_index()
            rows = list(event.widget.curselection())
            # single-selection logic
            # selects all numeric values below until next non-numeric value
            if len(rows) == 1:
                row_start = rows[0]
                column = self._df.iloc[row_start:, col]
                row_end = column.isnull().idxmax()
                self._active_indices = [row_start, row_end, col]
                for i in range(row_start, row_end):
                    event.widget.select_set(i)
            # multiple-selection logic
            elif len(rows) > 1:
                self._active_indices = [rows[0], rows[-1]+1, col]