# file:   EmbeddedTable.py
# author: Alex Krosney
# date:   December 18, 2022
#
# description: handles table operations for the application.
# TODO: implement different display styles

import tkinter as tk
import tkinter.ttk as ttk

import pandas as pd
import numpy as np

from classes.TableColumn import TableColumn
import classes.config as config

class EmbeddedTable() :

    # font params
    _text_size = 13
    _text_round = 6 # digits to round to in table

    # table params
    _table_x = 0.00
    _table_y = 0.00
    _table_w = 1.00
    _table_h = 1.00

    # canvas frame params
    _canvas_frame_x = 0.00
    _canvas_frame_y = 0.00
    _canvas_frame_w = 0.98
    _canvas_frame_h = 0.80

    # canvas params
    _canvas_x = 0.01
    _canvas_y = 0.01
    _canvas_w = 0.98
    _canvas_h = 0.98

    # align to the right of the canvas with the same height
    _v_scrollbar_x = 0.985
    _v_scrollbar_y = 0.000
    _v_scrollbar_w = 0.015
    _v_scrollbar_h = 0.800

    # align beneath the table canvas with the same width
    _h_scrollbar_x = 0.000
    _h_scrollbar_y = 0.805
    _h_scrollbar_w = 0.980
    _h_scrollbar_h = 0.015

    # button text factors
    _frame_w_text_factor = 50.000
    _frame_h_text_factor = 28.125

    # x-data add button params
    _x_set_button_x = 0.14
    _x_set_button_y = 0.84
    _x_set_button_w = 0.10
    _x_set_button_h = 0.04
    _x_set_button_text = 'Set'

    # x-data remove button params
    _x_reset_button_x = 0.26
    _x_reset_button_y = 0.84
    _x_reset_button_w = 0.10
    _x_reset_button_h = 0.04
    _x_reset_button_text = 'Reset'

    # y-data add button params
    _y_add_button_x = 0.64
    _y_add_button_y = 0.84
    _y_add_button_w = 0.10
    _y_add_button_h = 0.04
    _y_add_button_text = 'Add'

    # y-data remove button params
    _y_delete_button_x = 0.76
    _y_delete_button_y = 0.84
    _y_delete_button_w = 0.10
    _y_delete_button_h = 0.04
    _y_delete_button_text = 'Delete'

    # x-listbox (data display) params
    _x_listbox_x = 0.25
    _x_listbox_y = 0.89
    _x_listbox_w = 0.30
    _x_listbox_rows = 3
    _x_listbox_default_string = 'no data'

    # y-listbox (data display) params
    _y_listbox_x = 0.75
    _y_listbox_y = 0.89
    _y_listbox_w = 0.30
    _y_listbox_rows = 3
    _y_listbox_default_string = 'no data'

    def __init__(self, parent, x, y, w, h):

        # create a container for the table and associated scrollbars
        self._frame = ttk.Frame(parent)
        self._frame.place(relx=x, rely=y, relwidth=w, relheight=h)

        # create the canvas frame
        self._canvas_frame = ttk.Frame(self._frame, style='Bordered.TFrame')
        self._canvas_frame.place(relx=self._canvas_frame_x, rely=self._canvas_frame_y, relwidth=self._canvas_frame_w, relheight=self._canvas_frame_h)
        self._canvas_frame.bind("<MouseWheel>", self._canvas_v_scroll)

        # set the font and measure for table spacing
        self._font = tk.font.Font(size=self._text_size)
        self._column_width = self._font.measure('00.000000', displayof=self._canvas_frame)
        self._column_max_char = 10

        # create a vertical scrollbar
        self._v_scrollbar = ttk.Scrollbar(self._frame, orient=tk.VERTICAL, command=self._scrollbar_v_scroll)
        self._v_scrollbar.place(relx=self._v_scrollbar_x, rely=self._v_scrollbar_y, relwidth=self._v_scrollbar_w, relheight=self._v_scrollbar_h)
        self._v_scrollbar.bind("<ButtonPress-1>", self._scrollbar_v_click)
        # create a horizontal scrollbar
        self._h_scrollbar = ttk.Scrollbar(self._frame, orient=tk.HORIZONTAL, command=self._scrollbar_h_scroll)
        self._h_scrollbar.place(relx=self._h_scrollbar_x, rely=self._h_scrollbar_y, relwidth=self._h_scrollbar_w, relheight=self._h_scrollbar_h)
        self._h_scrollbar.bind("<ButtonPress-1>", self._scrollbar_h_click)

        # listbox for showing active x-data
        self._x_listbox = tk.Listbox(self._frame, justify=tk.CENTER, selectmode=tk.SINGLE, height=self._x_listbox_rows, activestyle=tk.NONE, font=self._font)
        self._x_listbox.place(relx=self._x_listbox_x, rely=self._x_listbox_y, relwidth=self._x_listbox_w, anchor=tk.N)
        self._x_listbox.config(background=config.widget_bg_color, foreground=config.text_color, relief=config.relief, borderwidth=config.border_width)
        self._x_listbox.insert(0, self._x_listbox_default_string)
        # listbox for showing active y-data
        self._y_listbox = tk.Listbox(self._frame, justify=tk.CENTER, selectmode=tk.SINGLE, height=self._y_listbox_rows, activestyle=tk.NONE, font=self._font)
        self._y_listbox.place(relx=self._y_listbox_x, rely=self._y_listbox_y, relwidth=self._y_listbox_w, anchor=tk.N)
        self._y_listbox.config(background=config.widget_bg_color, foreground=config.text_color, relief=config.relief, borderwidth=config.border_width)
        self._y_listbox.insert(0, self._y_listbox_default_string)
        self._y_listbox.bind("<ButtonRelease-1>", self._set_active_y)
        self._y_listbox.bind("<Up>", self._listbox_key_up)
        self._y_listbox.bind("<Down>", self._listbox_key_down)

        # create a canvas for holding a number of TableColumns to form a table
        self._canvas = None
        self._table_columns = []

        # default references for data
        self._df = None
        self._indices = {}
        self._active_indices = []
        self._n_req_indices = 3
        self._active_y_index = -1

        # initialize all buttons
        self._x_set_button = ttk.Button(self._frame, text=self._x_set_button_text, command=self._set_x)
        self._x_set_button.place(relx=self._x_set_button_x, rely=self._x_set_button_y, relwidth=self._x_set_button_w, relheight=self._x_set_button_h)
        self._x_reset_button = ttk.Button(self._frame, text=self._x_reset_button_text, command=self._reset_x)
        self._x_reset_button.place(relx=self._x_reset_button_x, rely=self._x_reset_button_y, relwidth=self._x_reset_button_w, relheight=self._x_reset_button_h)
        self._y_add_button = ttk.Button(self._frame, text=self._y_add_button_text, command=self._add_y)
        self._y_add_button.place(relx=self._y_add_button_x, rely=self._y_add_button_y, relwidth=self._y_add_button_w, relheight=self._y_add_button_h)
        self._y_delete_button = ttk.Button(self._frame, text=self._y_delete_button_text, command=self._delete_y)
        self._y_delete_button.place(relx=self._y_delete_button_x, rely=self._y_delete_button_y, relwidth=self._y_delete_button_w, relheight=self._y_delete_button_h) 

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

    def save(self, filename: str) -> None:
        """Saves the existing data."""
        self._data.save(filename)

    def clear(self, clear_df=False) -> None:
        """Clear all table and selection data."""
        if self._canvas is not None:
            self._canvas = self._canvas.destroy()
        self._table_columns = []
        self._reset_x()
        self._delete_y()
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

    def _scrollbar_h_scroll(self, *args) -> None:
        """Callback for horizontal scrollbar.
        Moves the canvas with the scrollbar."""
        if self._canvas is not None:
            self._canvas.xview_moveto(args[1])

    def _scrollbar_v_scroll(self, *args) :
        """Callback for vertical scrollbar.
        Moves the canvas with the scrollbar."""
        if self._canvas is not None:
            self._canvas.yview_moveto(args[1])

    def _scrollbar_h_click(self, event) :
        """Callback for horizontal scrollbar click.
        Moves the scrollbar and canvas according to cursor position."""
        if self._canvas is not None:
            # get scrollbar thumb position and width relative to canvas
            thumb_width = event.widget.winfo_width() * self._canvas.winfo_width() / self._canvas.bbox(tk.ALL)[2]
            thumb_pos = (event.x - 0.5 * thumb_width) / event.widget.winfo_width()
            # set canvas position, force update for scrollbar
            self._canvas.xview_moveto(thumb_pos)
            self._canvas.update_idletasks()

    def _scrollbar_v_click(self, event) :
        """Callback for vertical scrollbar click.
        Moves the scrollbar and canvas according to cursor position."""
        if self._canvas is not None:
            # get scrollbar bar position and height relative to canvas
            thumb_height = event.widget.winfo_height() * self._canvas.winfo_height() / self._canvas.bbox(tk.ALL)[3]
            thumb_pos = (event.y - 0.5 * thumb_height) / event.widget.winfo_height()
            # set canvas position, force update for scrollbar
            self._canvas.yview_moveto(thumb_pos)
            self._canvas.update_idletasks()

    def _canvas_v_scroll(self, event) -> None:
        """Callback for scrolling on the canvas containing tabular data."""
        if self._canvas is not None:
            self._canvas.yview_scroll(int(-event.delta/120), tk.UNITS)

    def _listbox_key_up(self, event) -> None:
        """Callback for listbox parsing with the up arrow key."""
        listbox_size = self._y_listbox.size()
        if listbox_size > 0:
            if self._active_y_index == -1:
                self._active_y_index = 0
            elif self._active_y_index > 0:
                self._active_y_index -= 1
            for i in range(listbox_size):
                event.widget.select_clear(i)
            event.widget.select_set(self._active_y_index)
            
    def _listbox_key_down(self, event) -> None:
        """Callback for listbox parsing with the down arrow key."""
        listbox_size = self._y_listbox.size()
        if listbox_size > 0:
            if self._active_y_index == -1:
                self._active_y_index = 0
            elif self._active_y_index < listbox_size - 1:
                self._active_y_index += 1
            for i in range(listbox_size):
                event.widget.select_clear(i)
            event.widget.select_set(self._active_y_index)

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
            self._canvas.bind("<MouseWheel>", self._canvas_v_scroll)
            # create all columns
            self._table_columns = []
            n_cols = len(df.columns)
            for i in range(n_cols):
                column = TableColumn(self._canvas, i, justify=tk.LEFT, selectmode=tk.EXTENDED,
                                     height=n_rows, activestyle=tk.NONE, font=self._font, width=self._column_max_char)
                column.bind("<MouseWheel>", self._canvas_v_scroll)
                column.bind("<ButtonRelease-1>", self._get_table_selection)
                for j in range(n_rows):
                    try:
                        val = str(round(float(self._df.iloc[j, i]), self._text_round))
                    except ValueError as e:
                        val = self._df.iloc[j, i]
                    val = val[:self._column_max_char]
                    column.insert(j, val)
                # add column to canvas
                self._canvas.create_window(i*(self._column_width+config.text_pad), 0, window=column, anchor=tk.NW)
                self._table_columns.append(column)
            # configure the canvas
            self._canvas.place(relx=self._canvas_x, rely=self._canvas_y, relwidth=self._canvas_w, relheight=self._canvas_h)
            self._canvas.config(yscrollcommand=self._v_scrollbar.set, xscrollcommand=self._h_scrollbar.set, scrollregion=self._canvas.bbox(tk.ALL))
            self._canvas.xview_moveto(0.0)
            self._canvas.yview_moveto(0.0)
            # force UI update
            self._frame.update_idletasks()
            # convert strings to numbers for internal data
            for i in range(len(self._df.columns)):
                self._df.iloc[:, i] = pd.to_numeric(self._df.iloc[:, i], errors='coerce')

    def _get_table_selection(self, event) -> None:
        """Get the actively selected column and column indices from the table.
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

    def _set_active_y(self, event) -> None:
        """Set the active y-index for data clearing."""
        self._active_y_index = list(event.widget.curselection())[0]

    def _set_x(self, event=None) -> None:
        """
        Get the active table selections and assign to the active x-data.
        """
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

    def _add_y(self, event=None) -> None:
        """
        Get the active table selections and append to the active y-data.
        """
        if self._validate_active_data():
            # update the stored y-indices
            if 'y' in self._indices.keys():
                self._indices['y'].append(self._active_indices.copy())
            else:
                self._indices['y'] = [self._active_indices.copy()]
            y0 = self._indices['y'][-1][0]
            y1 = self._indices['y'][-1][1]
            col = self._indices['y'][-1][2]
            # delete existing text and overwrite
            s = f'col:{col+1}; row:{y0+1}-{y1}'
            if len(self._indices['y']) == 1: # delete default text if the new index entry is the only entry
                self._y_listbox.delete(0)
            self._y_listbox.insert(0, s)

    def _reset_x(self, event=None) -> None:
        """Clear the currently selected x-data."""
        if 'x' in self._indices.keys():
            self._indices.pop('x')
        self._x_listbox.delete(0)
        self._x_listbox.insert(0, self._x_listbox_default_string)

    def _delete_y(self, event=None) -> None:
        """Clear the most recent selected y-data."""
        # clear the active/top entry in the internal data
        if 'y' in self._indices.keys() and len(self._indices['y']) > 0: 
            if self._active_y_index == -1:
                self._indices['y'].pop()
            else:
                y_len = len(self._indices['y'])
                self._indices['y'].pop(y_len - self._active_y_index - 1) # listbox uses reverse order of indices than internal list
        # clear the active/top entry in the listbox
        if self._active_y_index == -1:
            self._y_listbox.delete(0)
        else:
            self._y_listbox.delete(self._active_y_index)
        # insert default text if listbox is empty
        if self._y_listbox.size() == 0:
            self._y_listbox.insert(0, self._y_listbox_default_string)
        # reset active index
        self._active_y_index = -1
