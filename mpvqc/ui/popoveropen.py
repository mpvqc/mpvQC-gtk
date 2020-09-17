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
from os import path

from gi.repository import Gtk, Gdk, Pango

from mpvqc import get_settings, template
from mpvqc.utils import list_header_func, get_markup
from mpvqc.utils.draganddrop import is_qc_document

_RECENT_FILES_ROW_HEIGHT = 50


@template.TemplateTrans(resource_path='/data/ui/popoveropen.ui')
class PopoverOpen(Gtk.Popover):
    __gtype_name__ = 'PopoverOpen'

    button_subtitle = template.TemplateTrans.Child()
    button_clear_recent_files = template.TemplateTrans.Child()

    revealer_recent_files = template.TemplateTrans.Child()
    search_entry = template.TemplateTrans.Child()
    scrolled_container = template.TemplateTrans.Child()

    def __init__(self, parent, qc_manager, **kwargs):
        super().__init__(**kwargs)
        self.__parent = parent
        self.init_template()
        self.__qc_manager = qc_manager

        # List of recent files
        self.__list_recent_files = Gtk.ListBox()
        self.__list_recent_files.show_all()
        self.__list_recent_files.set_header_func(list_header_func, None)
        self.__list_recent_files.set_filter_func(self.__list_filter_func, None)
        self.__list_recent_files.set_placeholder(get_placeholder())
        self.__list_recent_files.connect("row-selected", self.on_recent_item_clicked)
        self.scrolled_container.add(self.__list_recent_files)

        # Search query
        self.__current_search_query = ""

        # Keyboard shortcuts
        self.__set_up_keyboard_shortcuts()

    def popup(self):
        self.__update_recent_files_list()
        super(PopoverOpen, self).popup()

    @template.TemplateTrans.Callback()
    def on_button_qc_clicked(self, widget, *data):
        self.popdown()
        self.__qc_manager.request_open_qc_documents()

    @template.TemplateTrans.Callback()
    def on_button_video_clicked(self, widget, *data):
        self.popdown()
        self.__qc_manager.request_open_video()

    @template.TemplateTrans.Callback()
    def on_button_subtitle_clicked(self, widget, *data):
        self.popdown()
        self.__qc_manager.request_open_subtitles()

    @template.TemplateTrans.Callback()
    def on_recent_files_search_changed(self, search_entry, *data):
        self.__current_search_query = search_entry.get_text()
        self.__list_recent_files.invalidate_filter()

    @template.TemplateTrans.Callback()
    def on_button_clear_recent_files_clicked(self, widget, *data):
        self.revealer_recent_files.set_reveal_child(False)
        get_settings().reset_latest_paths_recent_files()
        self.__update_recent_files_list()

    def on_recent_item_clicked(self, widget, row):
        """
        Invoked, when file in the recent file list was clicked.
        """

        if row:
            self.popdown()
            file_path = row.get_tooltip_text()

            if path.exists(file_path):
                if is_qc_document(file_path):
                    self.__qc_manager.request_open_qc_documents([file_path])
                else:
                    self.__qc_manager.request_open_video(file_path)

    def __list_filter_func(self, row, *second):
        """
        Methods gets called whenever 'invalidate_filter' got called.

        :return: True if matches query, False else
        """

        box = row.get_child()
        box_children = box.get_children()

        label = box_children[1]
        text = label.get_text()

        markup, count = get_markup(
            current_text=text,
            query=self.__current_search_query,
            highlight_prefix="<span weight='heavy'>",
            highlight_suffix="</span>"
        )
        label.set_markup(markup)

        return count > 0

    def __update_recent_files_list(self):
        """
        Updates the recent files list.
        """

        for child in self.__list_recent_files.get_children():
            self.__list_recent_files.remove(child)

        recent_files = get_settings().latest_paths_recent_files

        if recent_files:
            rows_displayed = min(5, len(recent_files))

            # Fit max 5 rows, add space for separators
            self.scrolled_container.set_min_content_height(_RECENT_FILES_ROW_HEIGHT * rows_displayed + rows_displayed)

            for recent_file in recent_files:
                row = create_row(
                    file_type=0 if is_qc_document(recent_file) else 1,
                    file_name=path.basename(recent_file),
                    path=recent_file
                )
                self.__list_recent_files.add(row)

            self.revealer_recent_files.set_reveal_child(True)
        else:
            self.revealer_recent_files.set_reveal_child(False)

    def __set_up_keyboard_shortcuts(self):
        """
        Sets up keyboard shortcuts relevant in this widget's context.
        """

        a = Gtk.AccelGroup()
        a.connect(
            accel_key=Gdk.KEY_o,
            accel_mods=Gdk.ModifierType.CONTROL_MASK,
            accel_flags=Gtk.AccelFlags.VISIBLE,
            closure=self.on_button_qc_clicked
        )
        a.connect(
            accel_key=Gdk.KEY_o,
            accel_mods=Gdk.ModifierType.CONTROL_MASK | Gdk.ModifierType.SHIFT_MASK,
            accel_flags=Gtk.AccelFlags.VISIBLE,
            closure=self.on_button_video_clicked
        )
        self.__parent.add_accel_group(accel_group=a)


def create_row(file_type, file_name, path: str):
    """
    This method is used to create a new row in the comment type list widget.

    :param file_name: the file name
    :param path: the path
    :param file_type: 0 if document, 1 if video
    :return: the new widget
    """

    icon = Gtk.Image()
    icon.set_from_icon_name("video-x-generic-symbolic" if file_type else "document-open-symbolic",
                            Gtk.IconSize.MENU)

    label = Gtk.Label(label=file_name)
    label.set_markup(file_name)
    label.set_halign(align=Gtk.Align.START)
    label.set_valign(align=Gtk.Align.CENTER)
    label.set_property("ellipsize", Pango.EllipsizeMode.END)
    label.set_margin_end(15)

    box = Gtk.Box()
    box.pack_start(child=icon, expand=False, fill=True, padding=15)
    box.pack_start(child=label, expand=True, fill=True, padding=0)

    row = Gtk.ListBoxRow()
    row.add(box)
    row.set_tooltip_text(str(path))
    row.set_size_request(width=-1, height=_RECENT_FILES_ROW_HEIGHT)
    row.set_can_focus(False)

    row.show_all()

    return row


def get_placeholder():
    """
    Return a placeholder widget if no entry is shown when searching recent files.
    """

    label = Gtk.Label(label=_("No files found"))
    label.set_sensitive(False)
    label.show_all()
    return label
