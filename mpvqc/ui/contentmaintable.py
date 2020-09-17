# mpvQC
#
# Copyright (C) 2020 mpvQC developers
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


import re
from typing import Tuple

from gi.repository import Gtk, Gdk, GObject, GLib

from mpvqc import template
from mpvqc.cellrenderer import CellRendererSeek, CellRendererTime, CellRendererType, CellRendererComment
from mpvqc.qc import Comment
from mpvqc.ui.popovertimeedit import PopoverTimeEdit
from mpvqc.ui.popovertypeedit import PopoverTypeEdit
from mpvqc.utils import keyboard, get_markup
from mpvqc.utils.input import MouseButton
from mpvqc.utils.signals import APPLY, CREATE_NEW_COMMENT, TABLE_CONTENT_CHANGED

PLAY_ICON = "media-playback-start-symbolic"

_REGEX_URLS = re.compile(r"((https?://|www\.).*?\..*?[^\s]+)")


def get_comment_markup_mode_default(raw_comment):
    """
    Returns the markup for a comment **if search mode is not active**.

    :param raw_comment: a string (no markup highlight applied yet) - the comment
    :return: a markup string
    """

    return _REGEX_URLS.sub(r"{}\1{}".format("<i>", "</i>"), raw_comment)


def get_comment_markup_mode_search(raw_comment, query):
    """
    Returns the markup for a comment **if search mode is active**.

    :param raw_comment: a string (no markup highlight applied yet) - the comment
    :param query: the string to highlight
    :return: a markup string
    """

    return get_markup(raw_comment, query, "<span weight='heavy'>", "</span>")[0]


@template.TemplateTrans(resource_path='/data/ui/contentmaintable.ui')
class ContentMainTable(Gtk.TreeView):
    __gtype_name__ = 'ContentMainTable'

    __gsignals__ = {
        TABLE_CONTENT_CHANGED: (GObject.SignalFlags.RUN_FIRST, None, (bool,)),
    }

    def __init__(self, video_widget, **kwargs):
        super().__init__(**kwargs)
        self.__video_widget = video_widget
        self.init_template()

        # Model
        self.__model = Gtk.ListStore(str, str, str, str)
        self.__model.set_sort_column_id(1, Gtk.SortType.ASCENDING)
        self.set_enable_search(False)
        self.set_model(self.__model)

        # Renderer
        self.__renderer_seek = CellRendererSeek()
        self.__renderer_time = CellRendererTime()
        self.__renderer_type = CellRendererType(self.__model)
        self.__renderer_comment = CellRendererComment(self.__model)

        # Columns
        self.__column_seek = Gtk.TreeViewColumn("Icon", self.__renderer_seek, icon_name=0)
        self.__column_time = Gtk.TreeViewColumn("Time", self.__renderer_time, text=1)
        self.__column_type = Gtk.TreeViewColumn("Type", self.__renderer_type, text=2)
        self.__column_type.set_sizing(Gtk.TreeViewColumnSizing.GROW_ONLY)
        self.__column_comment = Gtk.TreeViewColumn("Comment", self.__renderer_comment, markup=3)

        self.append_column(self.__column_seek)
        self.append_column(self.__column_time)
        self.append_column(self.__column_type)
        self.append_column(self.__column_comment)

        self.set_activate_on_single_click(True)

        # Connect signals
        self.get_selection().connect("changed", self.__on_selection_changed)
        self.__video_widget.connect(CREATE_NEW_COMMENT, self.__add_comment_from_context_menu)

        self.__model.connect("row-changed", self.__fire_signal_not_up_to_date)
        self.__model.connect("row-deleted", self.__fire_signal_not_up_to_date)
        self.__model.connect("row-inserted", self.__fire_signal_not_up_to_date)
        self.__fire_signal_blocked = False

        # Class variables
        self.__scrollbar_position = None

    def add_comments(self, comments: Tuple[Comment]):
        """
        Adds a list of comments to the table and scrolls to the last added comment.

        :param comments: list of comments to add
        """

        if comments:
            comments = list(comments)
            last = comments.pop(-1)

            self.__fire_signal_blocked = True
            for comment in comments:
                self.__model.append([PLAY_ICON, comment.comment_time, comment.comment_type, comment.comment_note])
            self.__fire_signal_blocked = False

            self.__add_comment(last.comment_time, last.comment_type, last.comment_note, start_editing=False)
            self.__renderer_type.recalculate_preferred_width()

    def get_all_comments(self):
        """
        Returns all the comments in the table.

        :return: all items of the given model
        """

        items = []
        iterator = self.__model.get_iter_first()
        while iterator:
            c_time = self.__model.get_value(iterator, 1)
            c_type = self.__model.get_value(iterator, 2)
            c_comm = self.__model.get_value(iterator, 3)
            items.append(Comment(c_time, c_type, c_comm))
            iterator = self.__model.iter_next(iterator)
        return tuple(items)

    def clear_all_comments(self):
        """
        Deletes all comments from the table.
        """

        self.__fire_signal_blocked = True
        self.__model.clear()
        self.__fire_signal_blocked = False
        self.__fire_signal_not_up_to_date()

    def highlight_row(self, tree_path):
        """
        Select row of tree_path.
        """

        self.set_cursor_on_cell(tree_path, self.__column_comment, self.__renderer_comment, start_editing=False)
        self.row_activated(tree_path, column=self.__column_comment)

    def set_comment_cell_data_func(self, func):
        """
        Specify the cell data func to use for the comments.
        """

        self.__column_comment.set_cell_data_func(self.__renderer_comment, func)

    def before_hide(self):
        self.__scrollbar_position = self.get_vadjustment().get_value()

    def after_show(self):
        # Workaround to restore the scroll bar position
        def __set_scrollbar_position():
            if self.__scrollbar_position:
                self.get_vadjustment().set_value(self.__scrollbar_position)

        GLib.timeout_add(90, __set_scrollbar_position)

    @template.TemplateTrans.Callback()
    def on_button_press_event(self, widget, event):
        path, path_iter, col = self.__get_path_at_position(event)
        btn = event.button

        if path_iter:
            row_selected = self.get_selection().iter_is_selected(path_iter)
            video_loaded = self.__video_widget.player.is_video_loaded()

            if btn == MouseButton.LEFT:
                if col == self.__column_seek and video_loaded:
                    self.__handle_seek(path, path_iter)
                    return True
                elif row_selected and col == self.__column_time and video_loaded:
                    self.__video_widget.player.pause()
                    self.__handle_seek(path, path_iter)
                    self.__handle_time_edit(col, path, path_iter)
                    return True
                elif row_selected and col == self.__column_type:
                    self.__handle_type_edit(col, path, path_iter)
                    return True
        return False

    def on_key_press_event(self, widget, event):
        no_mod, ctrl, alt, shift = keyboard.extract_modifiers(event.state)
        key = event.keyval

        if key == Gdk.KEY_Delete:
            self.__do_with_selected(self.__do_selected_delete_row)
            return True
        elif key == Gdk.KEY_Return or key == Gdk.KEY_BackSpace:
            self.__do_with_selected(self.__do_selected_start_edit)
            return True
        elif ctrl and key == Gdk.KEY_c:
            self.__do_with_selected(self.__do_selected_copy_to_clipboard)
            return True
        elif ctrl and key == Gdk.KEY_f:
            # Handled in search revealer
            return False
        elif no_mod and key == Gdk.KEY_Escape:
            return False
        return False

    def __add_comment(self, c_time, c_type, c_comm="", start_editing=True):
        """
        Adds a comment to the table. Then scrolls to the newly added comment and starts edit mode if set to True.

        :param start_editing: True, if start editing immediately, False else
        :param c_time: Comment time the time in the correct format (e.g. 00:00:00)
        :param c_type: Comment type the type of the comment to be added
        :param c_comm: Comment text the text of the comment to be added
        """

        c_comm = self.__model.append([PLAY_ICON, c_time, c_type, c_comm])
        path = self.__model.get_path(c_comm)
        self.set_cursor_on_cell(path, self.__column_comment, self.__renderer_comment, start_editing)

    def __add_comment_from_context_menu(self, widget, time, comment_type):
        """
        Adds a comment from the context menu.

        :param widget: not relevant, data from event
        :param time: the time of the video currently
        :param comment_type: the comment type to add
        """

        self.__add_comment(time, comment_type)

    def __on_selection_changed(self, __=None):
        """
        Called whenever the selection changes.

        :param __: not relevant, data from event
        """

        new_sel = self.get_selection().get_selected()[1]
        if new_sel:
            self.scroll_to_cell(self.__model.get_path(new_sel))

    def __handle_time_edit(self, col, path, path_iter):
        """
        Opens up a pop up to edit comment time.

        :param col: the column to obtain the clicked area
        :param path: the path to obtain the clicked area
        :param path_iter: the path iter object to get and set the value
        """

        def __set_value(__, v):
            self.__model.set_value(path_iter, 1, v)
            self.__on_selection_changed()

        pop = PopoverTimeEdit(self, self.__video_widget, self.__model.get_value(path_iter, 1))
        pop.connect(APPLY, __set_value)
        pop.set_pointing_to(self.get_cell_area(path, col))
        pop.set_relative_to(self)
        pop.popup()

    def __handle_type_edit(self, col, path, path_iter):
        """
        Opens up a pop up to edit comment type.

        :param col: the column to obtain the clicked area
        :param path: the path to obtain the clicked area
        :param path_iter: the path iter object to get and set the value
        """

        def __set_value(__, v):
            self.__model.set_value(path_iter, 2, v)
            self.__on_selection_changed()

        pop = PopoverTypeEdit(self.__model.get_value(path_iter, 2))
        pop.connect(APPLY, __set_value)
        pop.set_pointing_to(self.get_cell_area(path, col))
        pop.set_relative_to(self)
        pop.popup()

    def __handle_seek(self, path, path_iter):
        """
        Jumps to the time of the clicked comment.

        :param path: the path which was clicked
        :param path_iter: the path iter object to get the value
        """

        value = self.__model.get_value(path_iter, 1)
        self.__video_widget.player.position_jump(value)
        self.set_cursor_on_cell(path, self.__column_comment, self.__renderer_comment, start_editing=False)
        self.row_activated(path, column=self.__column_comment)

    def __get_path_at_position(self, event):
        """
        Returns the path at the event position.

        :param event: the event to obtain the path from
        :return: the path of the event
        """

        path_info = self.get_path_at_pos(event.x, event.y)
        if path_info:
            path, column, cell_x, cell_y = path_info
            path_iter = self.__model.get_iter(path)
            return path, path_iter, column,
        return None, None, None

    def __do_with_selected(self, do_func):
        """
        Helper function which does the action specified in the given 'do_func'
        passing in the current selection as argument.

        :param do_func: the action to invoke with the current selection
        """

        model, paths = self.get_selection().get_selected_rows()

        for path in paths:
            do_func(path)

    def __do_selected_delete_row(self, path):
        """
        Deletes the row of path.

        :param path: the cell to delete
        """

        self.__model.remove(self.__model.get_iter(path))

    def __do_selected_start_edit(self, path):
        """
        Starts editing cell of path.

        :param path: the cell to edit
        """

        self.set_cursor_on_cell(path, self.__column_comment, self.__renderer_comment, start_editing=True)
        self.row_activated(path, column=self.__column_comment)

    def __do_selected_copy_to_clipboard(self, path):
        """
        Copies the row to clipboard.

        :param path: the path of the row / the row index
        """

        row = self.__model[path]
        text = str(Comment(comment_time=row[1], comment_type=row[2], comment_note=row[3]))
        Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD).set_text(text, -1)

    def __fire_signal_not_up_to_date(self, *data):
        """
        Fires a signal that the table has changed

        :param data: not relevant, data from event
        """

        if not self.__fire_signal_blocked:
            self.emit(TABLE_CONTENT_CHANGED, False)
