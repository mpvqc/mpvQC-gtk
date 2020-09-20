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

from gi.repository import Gtk, Gdk

from mpvqc import template
from mpvqc.ui.prefpagegeneral import PreferencePageGeneral
from mpvqc.ui.prefpageimexport import PreferencePageExport
from mpvqc.ui.prefpageinput import PreferencePageInput
from mpvqc.ui.prefpagempv import PreferencePageMpv
from mpvqc.ui.window import MpvqcWindow
from mpvqc.utils import keyboard


@template.TemplateTrans(resource_path='/data/ui/contentpref.ui')
class ContentPref(Gtk.Box):
    __gtype_name__ = 'ContentPref'

    _header_bar: Gtk.HeaderBar = template.TemplateTrans.Child()
    _stack: Gtk.Stack = template.TemplateTrans.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.init_template()

        self.__page_general = PreferencePageGeneral()
        self.__page_export = PreferencePageExport()
        self.__page_input = PreferencePageInput()
        self.__page_mpv = PreferencePageMpv()

        self._stack.add_titled(self.__page_general, "General", _("General"))
        self._stack.add_titled(self.__page_export, "Import/Export", _("Im-/Export"))
        self._stack.add_titled(self.__page_input, "input.conf", _("Input"))
        self._stack.add_titled(self.__page_mpv, "mpv.conf", _("Video"))

        self._stack.set_visible_child(self.__page_general)

    @property
    def __parent(self) -> MpvqcWindow:
        return self.get_parent().get_parent()

    @property
    def header_bar(self) -> Gtk.HeaderBar:
        return self._header_bar

    @template.TemplateTrans.Callback()
    def _on_button_back_clicked(self, *_) -> None:
        self.__parent.show_main()
        self.__page_general.on_preferences_closed()
        self._stack.set_visible_child(self.__page_general)

    @template.TemplateTrans.Callback()
    def _on_button_restore_clicked(self, *_):
        self._stack.get_visible_child().on_restore_default_clicked()

    def on_key_press_event(self, _: Gtk.Widget, event: Gdk.EventKey) -> bool:
        """Returns True if handled, False else"""

        no_mod, ctrl, alt, shift = keyboard.extract_modifiers(event.state)
        key = event.keyval

        if key == Gdk.KEY_Escape and no_mod:
            self._on_button_back_clicked()
            return True

        return False
