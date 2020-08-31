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


from gi.repository import Gtk, GLib

from mpvqc.utils import StatusbarMessageDuration


@Gtk.Template(resource_path='/data/ui/messagestack.ui')
class MessageStack(Gtk.Stack):
    __gtype_name__ = 'MessageStack'

    label1 = Gtk.Template.Child()
    label2 = Gtk.Template.Child()
    label_empty = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.init_template()

        self.__timeout_handler = None

    def display_message(self, message, m_duration):
        """
        Displays a message for the given amount of time or updates the current message.

        :param message: a string to display at the stack
        :param m_duration: time of the duration to display the message
        """

        duration = m_duration.value if isinstance(m_duration, StatusbarMessageDuration) else m_duration

        visible_child = self.get_visible_child()

        if visible_child != self.label_empty:
            label1_displayed = visible_child == self.label1
            current = self.label1 if label1_displayed else self.label2
            upcoming = self.label1 if not label1_displayed else self.label2

            upcoming.set_text(message)
            self.set_visible_child(upcoming)
            self.__attach_timeout_handler(duration)
            current.set_text("")
        else:
            self.label1.set_text(message)
            self.set_visible_child(self.label1)
            self.__attach_timeout_handler(duration)

    def __attach_timeout_handler(self, duration):
        """
        Attaches a new timeout handler to clear the message stack after a certain amount of time.

        :param duration: time in ms, after that the current message will be cleared
        """

        self.__remove_timeout_handler()

        def __clear_message():
            self.set_visible_child(self.label_empty)
            self.__remove_timeout_handler()
            return False

        self.__timeout_handler = GLib.timeout_add(duration, __clear_message)

    def __remove_timeout_handler(self):
        """
        Removes the current timeout handler (and cancels the timeout by doing so).
        """

        if self.__timeout_handler:
            GLib.source_remove(self.__timeout_handler)
            self.__timeout_handler = None
