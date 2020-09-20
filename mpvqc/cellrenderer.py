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

import platform
from gi.repository import Gtk, Pango, Gdk

from mpvqc import get_settings
from mpvqc.utils import get_longest_string_from, validate_text_insertion

_PADDING = (6, 6)


class CellRendererSeek(Gtk.CellRendererPixbuf):
    def __init__(self, **properties):
        super().__init__(**properties)
        self.set_padding(*_PADDING)


class CellRendererTime(Gtk.CellRendererText):

    def __init__(self, **properties):
        super().__init__(**properties)
        self.set_padding(*_PADDING)


class CellRendererType(Gtk.CellRendererText):

    def __init__(self, model_reference, **properties):
        super().__init__(**properties)
        self.__model = model_reference
        self.set_padding(*_PADDING)
        self.set_property("editable", False)
        self.set_property("ellipsize", Pango.EllipsizeMode.END)
        self.__preferred_width = None

    def do_get_preferred_width(self, *args, **kwargs):
        if self.__preferred_width is None:
            self.recalculate_preferred_width()
        return self.__preferred_width

    def recalculate_preferred_width(self):
        """
        Recalculate preferred width based on current model and on comment types (from settings entry) width.

        :return: a tuple (width, width)
        """

        layout = Gtk.Label().get_layout()
        layout.set_markup(max(get_longest_string_from(self.__model, 2), get_settings().comment_types_longest, key=len))
        pixel_size = layout.get_pixel_size()
        size = pixel_size.width + (self.get_padding()[0] * 4)
        self.__preferred_width = size, size


class CellRendererComment(Gtk.CellRendererText):

    # https://stackoverflow.com/a/40163816/8596346
    # https://lazka.github.io/pgi-docs/Gtk-3.0/classes/Entry.html#Gtk.Entry.signals.insert_at_cursor

    def __init__(self, model_reference, **properties):
        super().__init__(**properties)
        self.__model = model_reference
        self.__commit_changes = True
        self.set_property("editable", True)
        self.set_property("ellipsize", Pango.EllipsizeMode.END)
        self.connect("editing-started", self.__on_editing_started)

    def __on_editing_started(self, cell_renderer, entry, path):
        self.__commit_changes = True

        def on_key_press_event(editable, event, data=None):
            if event.keyval == Gdk.KEY_Escape:
                self.__commit_changes = False
            return False

        def on_entry_destroyed(editable):
            if self.__commit_changes:
                self.__model[path][3] = editable.get_text()
            return False

        entry.connect("key-press-event", on_key_press_event)
        entry.connect("unrealize", on_entry_destroyed)
        entry.connect("insert-text", validate_text_insertion)
