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


from gi.repository import Gtk, GObject, Gdk

from mpvqc import template_custom
from mpvqc.utils.signals import APPLY


@template_custom.TemplateTrans(resource_path='/data/ui/input.ui')
class InputPopover(Gtk.Popover):
    __gtype_name__ = 'InputPopover'

    __gsignals__ = {
        APPLY: (GObject.SignalFlags.RUN_FIRST, None, (str,))
    }

    label_input = Gtk.Template.Child()
    label_message = Gtk.Template.Child()

    entry = Gtk.Template.Child()
    button = Gtk.Template.Child()

    revealer = Gtk.Template.Child()

    def __init__(self, label, validator, current_text="", placeholder="", **kwargs):
        """
        A small popup window for retrieving user input.

        :param label: the text of the label
        :param validator: the validator to validate the input
        :param current_text: the current text of the popup entry
        :param placeholder: the text of the placeholder
        :param kwargs: template data
        """

        super().__init__(**kwargs)
        self.init_template()

        self.__validator = validator

        self.label_input.set_text(label)
        self.entry.set_placeholder_text(placeholder)
        self.entry.set_text(current_text)

        self.__update_message(*self.__validator.validate(current_text))
        self.revealer.show()

    @template_custom.TemplateTrans.Callback()
    def on_button_clicked(self, widget=None, *data):
        """
        Invoked, when apply clicked or enter pressed.

        :param widget: passed in by event
        :param data: passed in by event
        """

        self.emit(APPLY, self.entry.get_text())
        self.popdown()

    @template_custom.TemplateTrans.Callback()
    def on_entry_text_changed(self, widget, *data):
        """
        Called whenever the text of the entry changes.

        :param widget: the widget whose text has changed
        :param data: passed in by event
        """

        self.__update_message(*self.__validator.validate(widget.get_text()))

    @template_custom.TemplateTrans.Callback()
    def on_entry_key_press_event(self, widget, event):
        """
        Listen to 'Enter' presses.

        :param widget: passed in by event
        :param event: key press event
        """

        if event.keyval == Gdk.KEY_Return and self.button.get_sensitive():
            self.on_button_clicked()
            return True

    def __update_message(self, valid, message):
        """
        Updates the button state and displays a message in a Gtk.Revealer if not valid.

        :param valid: True, if valid, False else.
        :param message: the message to display if not valid
        """

        self.button.set_sensitive(valid)
        self.label_message.set_text(message if not valid else "")
        self.revealer.set_reveal_child(not valid)
