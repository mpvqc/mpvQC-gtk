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


from gi.repository import Gtk

from mpvqc import get_settings


@Gtk.Template(resource_path='/data/ui/prefpageinput.ui')
class PreferencePageInput(Gtk.ScrolledWindow):
    __gtype_name__ = 'PreferencePageInput'

    # todo replace gtk text view with gtk source view

    input_text_buffer = Gtk.Template.Child()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.init_template()

        self.__set_initial_values()

    def on_restore_default_clicked(self):
        """
        Called whenever the user presses restore and this preference page is visible.
        """

        get_settings().reset_config_file_input_content()

        self.__set_initial_values()

    @Gtk.Template.Callback()
    def on_input_text_buffer_changed(self, widget, *data):
        start_iter = self.input_text_buffer.get_start_iter()
        end_iter = self.input_text_buffer.get_end_iter()
        get_settings().config_file_input_content = self.input_text_buffer.get_text(start_iter, end_iter, True)

    def __set_initial_values(self):
        """
        Set initial values from settings.
        """

        self.input_text_buffer.set_text(get_settings().config_file_input_content)
