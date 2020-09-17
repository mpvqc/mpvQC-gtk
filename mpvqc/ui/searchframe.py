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


from gettext import gettext as _

from gi.repository import Gtk, Gdk, GLib

from mpvqc import template
from mpvqc.ui.contentmaintable import get_comment_markup_mode_default, get_comment_markup_mode_search
from mpvqc.utils import keyboard, validate_text_insertion, get_pattern


@template.TemplateTrans(resource_path='/data/ui/searchframe.ui')
class SearchFrame(Gtk.Frame):
    __gtype_name__ = 'SearchFrame'

    revealer: Gtk.Revealer = template.TemplateTrans.Child()
    revealer_label_result: Gtk.Revealer = template.TemplateTrans.Child()

    entry_search = template.TemplateTrans.Child()

    button_up = template.TemplateTrans.Child()
    button_down = template.TemplateTrans.Child()

    label_result = template.TemplateTrans.Child()

    def __init__(self, table_widget, **kwargs):
        super().__init__(**kwargs)
        self.init_template()
        self.__table_widget = table_widget
        self.__model = table_widget.get_model()
        self.__selection_model = table_widget.get_selection()

        self.__table_widget.set_comment_cell_data_func(self.__comment_type_cell_data_func)

        self.set_property("valign", Gtk.Align.START)
        self.set_property("halign", Gtk.Align.END)
        self.revealer.set_reveal_child(False)

        self.entry_search.connect("key-press-event", self.on_key_press_event)
        self.entry_search.connect("focus-out-event", self.on_focus_out_event)
        self.entry_search.connect("insert-text", validate_text_insertion)

        self.__recent_query = ""
        self.__search_active = False
        self.__current_matches = None

    def do_show_all(self):
        self.revealer.hide()

    @template.TemplateTrans.Callback()
    def on_key_press_event(self, widget, event):
        no_mod, ctrl, alt, shift = keyboard.extract_modifiers(event.state)
        key = event.keyval

        if ctrl and key == Gdk.KEY_f:
            self.__toggle_search()
            return True
        elif no_mod and key == Gdk.KEY_Escape:
            self.__hide_search()
            return True
        elif no_mod and key == Gdk.KEY_Return:
            self.__highlight_next(top_to_bottom=True)
            return True
        elif shift and key == Gdk.KEY_Return:
            self.__highlight_next(top_to_bottom=False)
            return True
        elif self.__search_active and no_mod and (key == Gdk.KEY_Down or key == Gdk.KEY_Up):
            return True

    @template.TemplateTrans.Callback()
    def on_search_changed(self, search_entry, *data):
        self.__table_widget.queue_draw()
        self.on_next_match(None)

    @template.TemplateTrans.Callback()
    def on_previous_match(self, button, *data):
        """
        Either button up, CTRL + SHIFT + G or SHIFT + Enter is pressed.
        """

        self.__highlight_next(top_to_bottom=False)

    @template.TemplateTrans.Callback()
    def on_next_match(self, button, *data):
        """
        Either button down, CTRL + G or Enter is pressed.
        """

        self.__highlight_next(top_to_bottom=True)

    @template.TemplateTrans.Callback()
    def on_close_pressed(self, *_):
        self.__hide_search()

    def on_focus_out_event(self, *_):
        self.__hide_search()

    def clear_current_matches(self, *widget, has_changes):
        """
        Clears the current matches to force a complete research.
        """

        if has_changes:
            self.__current_matches = None

    def __hide_search(self):
        """
        Hides the the search if is revealed.
        """

        if self.revealer.get_child_revealed():
            def hide_completely():
                self.revealer.hide()
                return False

            self.revealer.set_reveal_child(False)
            GLib.timeout_add(self.revealer.get_transition_duration(), hide_completely)
            self.__table_widget.grab_focus()
            self.__search_active = False
            self.__table_widget.queue_draw()

    def __show_search(self):
        self.__search_active = True
        self.__table_widget.queue_draw()
        self.revealer.show()
        self.revealer.set_reveal_child(True)
        self.entry_search.grab_focus()

    def __toggle_search(self):
        """
        When the user presses CTRL + f.
        """

        if self.revealer.get_child_revealed():
            if self.entry_search.has_focus():
                self.__hide_search()
            else:
                self.entry_search.grab_focus()
        else:
            self.__show_search()

    def __update_all_matches(self, is_new_query):
        """
        Iterates over the model and adds all matches of the latest query.
        """

        if not self.__current_matches or is_new_query:

            pattern = get_pattern(self.__recent_query)

            matches = []
            iterator = self.__model.get_iter_first()
            while iterator:
                comment = self.__model.get_value(iterator, 3)
                if pattern.search(comment):
                    matches.append(self.__model.get_path(iterator))
                iterator = self.__model.iter_next(iterator)

            self.__current_matches = matches

    def __highlight_next(self, top_to_bottom):
        """
        Will highlight the next occurrence when found.

        :param top_to_bottom: True if should go down, False else.
        """

        new_query = self.entry_search.get_text()
        continue_previous_search = self.__recent_query == new_query
        self.__recent_query = new_query

        if self.__recent_query:
            self.__update_all_matches(is_new_query=not continue_previous_search)

            matches = self.__current_matches
            if matches:
                matches_size = len(matches)
                if continue_previous_search:
                    selected_iter = self.__selection_model.get_selected()[1]
                    selected_row = self.__model.get_path(selected_iter)

                    if top_to_bottom:
                        for idx, match in enumerate(matches):
                            if match > selected_row:
                                self.__table_widget.highlight_row(match)
                                self.__update_search_results_label(idx + 1, matches_size)
                                return
                    else:  # bottom -> top
                        for idx, match in enumerate(reversed(matches)):
                            if match < selected_row:
                                self.__table_widget.highlight_row(match)
                                self.__update_search_results_label(matches_size - idx, matches_size)
                                return

                        # when search started again from bottom
                        self.__table_widget.highlight_row(matches[-1])
                        self.__update_search_results_label(matches_size, matches_size)
                        return

                # when query is new or search started again from top
                self.__table_widget.highlight_row(matches[0])
                self.__update_search_results_label(1, matches_size)
                return

        self.__update_search_results_label(None, None)

    def __update_search_results_label(self, current, total):
        """
        Updates the label below the search entry. Reveals the label if label is not empty.
        """

        if current is not None and total is not None:
            self.label_result.set_text(_("{} of {}").format(current, total))
            self.revealer_label_result.set_reveal_child(True)
        else:
            if self.__recent_query:
                self.label_result.set_text(_("Phrase not found"))
                self.revealer_label_result.set_reveal_child(True)
            else:
                self.revealer_label_result.set_reveal_child(False)
                self.label_result.set_text("")

    def __comment_type_cell_data_func(self, tree_column, cell, tree_model, tree_iter, *data):
        """
        Specify how text in the tree view is highlighted.
        """

        text = tree_model.get_value(tree_iter, 3)
        query = self.__recent_query

        if self.__search_active and query:
            cell.set_property("markup", get_comment_markup_mode_search(text, query))
        else:
            cell.set_property("markup", get_comment_markup_mode_default(text))