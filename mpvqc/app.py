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

from gi.repository import Gtk, Gio, GLib, Gdk


class Application(Gtk.Application):

    def __init__(self, app_id, app_name, app_resource_base_path):
        super().__init__(application_id=app_id, flags=Gio.ApplicationFlags.FLAGS_NONE)

        self.set_resource_base_path(app_resource_base_path)
        GLib.set_prgname(app_name)

        if platform.system() == "Windows":
            css_platform = app_resource_base_path + "/css/style-windows.css"
        else:
            css_platform = app_resource_base_path + "/css/style-linux.css"

        css_general = app_resource_base_path + "/css/style-general.css"

        Application.__apply_css(css_general)
        Application.__apply_css(css_platform)

    @staticmethod
    def __apply_css(resource_path: str):
        css_provider = Gtk.CssProvider()
        css_provider.load_from_resource(resource_path)
        Gtk.StyleContext().add_provider_for_screen(screen=Gdk.Screen.get_default(),
                                                   provider=css_provider,
                                                   priority=Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

    def do_activate(self):
        win = self.props.active_window

        if not win:
            from mpvqc.ui.window import MpvqcWindow
            win = MpvqcWindow(application=self)

        win.present()
