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

import mpvqc.utils.signals as signals
from mpvqc import template


@template.TemplateTrans(resource_path='/data/ui/input.ui')
class InputPopover(Gtk.Popover):
    __gtype_name__ = 'InputPopover'

    __gsignals__ = {
        signals.MPVQC_APPLY: (GObject.SignalFlags.RUN_FIRST, None, (str,))
    }

    label_input = template.TemplateTrans.Child()
    label_message = template.TemplateTrans.Child()

    entry = template.TemplateTrans.Child()
    button = template.TemplateTrans.Child()

    revealer = template.TemplateTrans.Child()

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

    @template.TemplateTrans.Callback()
    def on_button_clicked(self, *_):
        """
        Invoked, when apply clicked or enter pressed.
        """

        self.emit(signals.MPVQC_APPLY, self.entry.get_text())
        self.popdown()

    @template.TemplateTrans.Callback()
    def on_entry_text_changed(self, widget, *_):
        """
        Called whenever the text of the entry changes.

        :param widget: the widget whose text has changed
        """

        self.__update_message(*self.__validator.validate(widget.get_text()))

    @template.TemplateTrans.Callback()
    def on_entry_key_press_event(self, _, event):
        """
        Listen to 'Enter' presses.
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
