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
from gettext import gettext as _

from gi.repository import Gtk

import mpvqc.utils.signals as signals
from mpvqc import get_settings, get_app_paths, template
from mpvqc.ui.input import InputPopover
from mpvqc.utils import list_header_func, list_header_nested_func
from mpvqc.utils.validators import NicknameValidator


@template.TemplateTrans(resource_path='/data/ui/prefpageimexport.ui')
class PreferencePageExport(Gtk.ScrolledWindow):
    __gtype_name__ = 'PreferencePageExport'

    list_export_settings = template.TemplateTrans.Child()
    list_export_settings_header = template.TemplateTrans.Child()
    list_auto_save_interval = template.TemplateTrans.Child()
    list_open_back_directory = template.TemplateTrans.Child()

    row_nick = template.TemplateTrans.Child()
    label_nick = template.TemplateTrans.Child()
    label_backup_directory_path: Gtk.Label = template.TemplateTrans.Child()

    revealer_header_section: Gtk.Revealer = template.TemplateTrans.Child()
    revealer_auto_save: Gtk.Revealer = template.TemplateTrans.Child()

    switch_append_nick: Gtk.Switch = template.TemplateTrans.Child()
    switch_write_header: Gtk.Switch = template.TemplateTrans.Child()
    switch_write_date: Gtk.Switch = template.TemplateTrans.Child()
    switch_write_generator: Gtk.Switch = template.TemplateTrans.Child()
    switch_write_nick: Gtk.Switch = template.TemplateTrans.Child()
    switch_write_path: Gtk.Switch = template.TemplateTrans.Child()
    switch_load_video_automatically: Gtk.Switch = template.TemplateTrans.Child()
    switch_auto_save: Gtk.Switch = template.TemplateTrans.Child()

    spin_btn_auto_save_interval: Gtk.SpinButton = template.TemplateTrans.Child()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.init_template()

        self.label_backup_directory_path.set_text(str(get_app_paths().dir_backup))

        self.list_export_settings_header.set_header_func(list_header_nested_func, None)
        self.list_export_settings.set_header_func(list_header_func, None)
        self.list_auto_save_interval.set_header_func(list_header_nested_func, None)
        self.list_open_back_directory.set_header_func(list_header_nested_func, None)

        # Bind settings to widgets
        s = get_settings()
        s.bind_import_open_video_automatically(self.switch_load_video_automatically, "active")
        s.bind_export_qc_document_nick(self.label_nick, "label")
        s.bind_export_append_nick(self.switch_append_nick, "active")
        s.bind_export_write_header(self.switch_write_header, "active")
        s.bind_export_write_header(self.revealer_header_section, "reveal-child")
        s.bind_export_write_date(self.switch_write_date, "active")
        s.bind_export_write_generator(self.switch_write_generator, "active")
        s.bind_export_write_nick(self.switch_write_nick, "active")
        s.bind_export_write_path(self.switch_write_path, "active")
        s.bind_auto_save_enabled(self.switch_auto_save, "active")
        s.bind_auto_save_enabled(self.revealer_auto_save, "reveal-child")
        s.bind_auto_save_interval(self.spin_btn_auto_save_interval, "value")

    # noinspection PyMethodMayBeStatic
    def on_restore_default_clicked(self):
        """
        Called whenever the user presses restore and this preference page is visible.
        """

        s = get_settings()
        s.reset_qc_document_nick()
        s.reset_export_append_nick()
        s.reset_export_write_header()
        s.reset_export_write_date()
        s.reset_export_write_generator()
        s.reset_export_write_nick()
        s.reset_export_write_path()
        s.reset_import_open_video_automatically()
        s.reset_auto_save_enabled()
        s.reset_auto_save_interval()

    @template.TemplateTrans.Callback()
    def on_export_row_activated(self, __, row, *___):
        """
        Handles the editing of the nick.
        """

        if row == self.row_nick:
            def __apply(____, new_value):
                self.label_nick.set_text(new_value)

            pop = InputPopover(label=_("New nickname:"),
                               validator=NicknameValidator(),
                               placeholder=_("Enter nickname"),
                               current_text=get_settings().export_qc_document_nick)
            pop.set_relative_to(self.label_nick)
            pop.connect(signals.MPVQC_APPLY, __apply)
            pop.popup()
            return True

    @template.TemplateTrans.Callback()
    def on_button_open_backup_directory_clicked(self, _):
        directory = str(get_app_paths().dir_backup)
        plat = platform.system()

        if plat == "Windows":
            import os
            os.startfile(directory)
        else:
            from gi.repository import Gio
            # The following code should even work on Windows, but it doesn't
            Gio.app_info_launch_default_for_uri(uri="file:///" + directory)
