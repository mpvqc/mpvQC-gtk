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


from gi.repository import Gtk, Gdk

from mpvqc import get_settings, template


@template.TemplateTrans(resource_path='/data/ui/window.ui')
class MpvqcWindow(Gtk.ApplicationWindow):
    __gtype_name__ = 'MpvqcWindow'

    _stack_header: Gtk.Stack = template.TemplateTrans.Child()
    _stack_content: Gtk.Stack = template.TemplateTrans.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.init_template()

        s = get_settings()

        self.set_default_size(s.app_window_width, s.app_window_height)

        from mpvqc.ui.contentmain import ContentMain
        content_main = ContentMain(mpvqc_window=self)
        from mpvqc.ui.contentpref import ContentPref
        content_pref = ContentPref()

        self._stack_header.add_named(content_main.header_bar, 'MainHeaderBar')
        self._stack_header.add_named(content_pref.header_bar, 'PrefHeaderBar')

        self._stack_content.add_named(content_main, 'MainStack')
        self._stack_content.add_named(content_pref, 'PrefStack')

        self._stack_header.set_visible_child(content_main.header_bar)
        self._stack_content.set_visible_child(content_main)

        self.__header_bar_main = content_main.header_bar
        self.__header_bar_pref = content_pref.header_bar

        self.__content_main = content_main
        self.__content_pref = content_pref

        self.__is_fullscreen = False

    @template.TemplateTrans.Callback()
    def on_key_press_event(self, widget: Gtk.Widget, event: Gdk.EventKey) -> bool:
        handled = self._stack_content.get_visible_child().on_key_press_event(widget, event)
        if handled:
            return True
        return False

    def do_delete_event(self, *args, **kwargs):
        """
        Invoked when user presses the close button or CTRL + Q.

        :return: True to stop other handlers from being invoked for the event. False to propagate the event further.
        """

        can_quit = self.__content_main.can_quit
        if not can_quit:
            return True

        s = get_settings()

        width, height = self.get_size()

        s.app_window_height = height
        s.app_window_width = width
        s.app_window_video_height = self.__content_main.allocated_table_height

        s.write_config_file_input_content()
        s.write_config_file_mpv_content()

        return False

    def show_pref(self) -> None:
        """Opens the preference view"""

        self._stack_header.set_visible_child(self.__header_bar_pref)
        self._stack_content.set_visible_child(self.__content_pref)

    def show_main(self) -> None:
        """Opens the main view"""

        self._stack_header.set_visible_child(self.__header_bar_main)
        self._stack_content.set_visible_child(self.__content_main)
        self.__content_main.after_preferences_closed()

    def toggle_fullscreen(self, *_):
        """
        Toggles fullscreen / unfullscreen.
        """

        if self.__is_fullscreen:
            self.unfullscreen()
        else:
            self.fullscreen()

    def fullscreen(self):
        """
        Action when "f" (fullscreen key) is pressed and app is not already fullscreen.
        """

        super(MpvqcWindow, self).fullscreen()
        self.__is_fullscreen = True
        self.__content_main.fullscreen()

    def unfullscreen(self):
        """
        Action when "f" (fullscreen key) is pressed and app is fullscreen.
        """

        if not self.__is_fullscreen:
            return

        super(MpvqcWindow, self).unfullscreen()
        self.__is_fullscreen = False
        self.__content_main.unfullscreen()
