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

from mpvqc import get_settings, template


@template.TemplateTrans(resource_path='/data/ui/prefpagempv.ui')
class PreferencePageMpv(Gtk.ScrolledWindow):
    __gtype_name__ = 'PreferencePageMpv'

    # todo replace gtk text view with gtk source view

    mpv_text_buffer = template.TemplateTrans.Child()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.init_template()

        self.__set_initial_values()

    def on_restore_default_clicked(self):
        """
        Called whenever the user presses restore and this preference page is visible.
        """

        get_settings().reset_config_file_mpv_content()

        self.__set_initial_values()

    @template.TemplateTrans.Callback()
    def on_mpv_text_buffer_changed(self, widget, *data):
        start_iter = self.mpv_text_buffer.get_start_iter()
        end_iter = self.mpv_text_buffer.get_end_iter()
        get_settings().config_file_mpv_content = self.mpv_text_buffer.get_text(start_iter, end_iter, True)

    def __set_initial_values(self):
        """
        Set initial values from settings.
        """

        self.mpv_text_buffer.set_text(get_settings().config_file_mpv_content)
