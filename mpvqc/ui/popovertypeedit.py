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


from gi.repository import Gtk, GObject

from mpvqc import get_settings
from mpvqc.utils.signals import APPLY


@Gtk.Template(resource_path='/data/ui/popovertypeedit.ui')
class PopoverTypeEdit(Gtk.Popover):
    __gtype_name__ = 'PopoverTypeEdit'

    __gsignals__ = {
        APPLY: (GObject.SignalFlags.RUN_FIRST, None, (str,))
    }

    box = Gtk.Template.Child()

    def __init__(self, current_text, **properties):
        super().__init__(**properties)
        self.init_template()

        text_unknown = True
        for item in get_settings().comment_types:
            lbl = str(item)
            btn = self.__create_new_button(lbl)
            btn.show()

            if lbl == current_text:
                btn.set_property("active", True)
                text_unknown = False

            self.box.pack_start(btn, expand=False, fill=True, padding=0)

        if text_unknown:
            self.__create_additional_entry(current_text)

    def __on_item_clicked(self, widget, data=None):
        self.emit(APPLY, widget.get_property("text"))
        self.popdown()

    def __create_new_button(self, label):
        btn = Gtk.ModelButton()
        btn.set_property("text", label)
        btn.set_property("centered", False)
        btn.set_property("role", Gtk.ButtonRole.RADIO)
        btn.connect("clicked", self.__on_item_clicked)
        return btn

    def __create_additional_entry(self, current_text):
        btn = self.__create_new_button(current_text)
        btn.set_property("active", True)
        btn.show()

        sep = Gtk.Separator()
        sep.set_orientation(Gtk.Orientation.HORIZONTAL)
        sep.show()

        self.box.pack_start(sep, expand=False, fill=True, padding=0)
        self.box.pack_start(btn, expand=False, fill=True, padding=0)
