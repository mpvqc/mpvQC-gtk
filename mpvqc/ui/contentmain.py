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


import time

from gi.repository import Gtk, Gdk, GObject, GLib

from mpvqc import template, get_settings
from mpvqc.qc.manager import QcManager
from mpvqc.ui.about import AboutDialog
from mpvqc.ui.contentmaintable import ContentMainTable
from mpvqc.ui.popoveropen import PopoverOpen
from mpvqc.ui.searchframe import SearchFrame
from mpvqc.ui.statusbar import StatusBar
from mpvqc.ui.window import MpvqcWindow
from mpvqc.utils import draganddrop, keyboard
from mpvqc.utils.shortcuts import ShortcutWindow
from mpvqc.utils.signals import MPVQC_FILENAME_NO_EXT, MPVQC_PATH, MPVQC_STATUSBAR_UPDATE, MPVQC_QC_STATE_CHANGED, MPVQC_NEW_VIDEO_LOADED


@template.TemplateTrans(resource_path='/data/ui/contentmain.ui')
class ContentMain(Gtk.Box):
    __gtype_name__ = 'ContentMain'

    __gsignals__ = {
        # Signals, that there was a new video loaded:  p1 'video width' ; p2 'video height'
        MPVQC_NEW_VIDEO_LOADED: (GObject.SignalFlags.RUN_FIRST, None, (int, int))
    }

    _header_bar: Gtk.HeaderBar = template.TemplateTrans.Child()
    _stack: Gtk.Stack = template.TemplateTrans.Child()

    _button_dark_theme: Gtk.Button = template.TemplateTrans.Child()

    _box: Gtk.Box = template.TemplateTrans.Child()
    _paned: Gtk.Paned = template.TemplateTrans.Child()
    _overlay: Gtk.Overlay = template.TemplateTrans.Child()
    _scrolled_window: Gtk.ScrolledWindow = template.TemplateTrans.Child()

    def __init__(self, mpvqc_window: MpvqcWindow, **kwargs):
        super().__init__(**kwargs)
        self.init_template()

        s = get_settings()

        # Dark theme
        self._button_dark_theme.set_property("role", Gtk.ButtonRole.CHECK)
        self._button_dark_theme.set_property("active", s.prefer_dark_theme)
        Gtk.Settings.get_default().set_property("gtk-application-prefer-dark-theme", s.prefer_dark_theme)

        # Widgets
        from mpvqc.ui.contentmainmpv import ContentMainMpv
        self.__video_widget = ContentMainMpv(self, mpvqc_window)
        self.__table_widget = ContentMainTable(self.__video_widget)
        self.__qc_manager = QcManager(mpvqc_window, self.__video_widget, self.__table_widget)
        self.__popover_open = PopoverOpen(self.__qc_manager)
        self.__status_bar = StatusBar()
        self.__search_frame = SearchFrame(self.__table_widget)

        # Widget composition of ui templates
        self._scrolled_window.add(self.__table_widget)
        self._overlay.add(self._scrolled_window)
        self._overlay.add_overlay(self.__search_frame)
        self._paned.pack1(self.__video_widget, resize=True, shrink=False)
        self._paned.pack2(self._overlay, resize=True, shrink=False)
        self._box.pack_start(self.__status_bar, expand=False, fill=True, padding=0)

        # Set up drag and drop
        target = Gtk.TargetEntry.new(target="text/uri-list", flags=Gtk.TargetFlags.OTHER_APP, info=0)
        self._paned.drag_dest_set(Gtk.DestDefaults.ALL, [target], Gdk.DragAction.COPY)
        self._paned.connect("drag-data-received", self.__on_drag_data_received)

        # Connect events: Player goes first
        self.__video_widget.connect("realize", self.__status_bar.on_mpv_player_realized)
        # Connect events: Key event order
        self.__table_widget.connect("key-press-event", self.__table_widget.on_key_press_event)
        self.__table_widget.connect("key-press-event", self.__video_widget.on_key_press_event)
        # Connect events: Statusbar
        self.__table_widget.get_selection().connect("changed", self.__status_bar.on_comments_selection_change)
        self.__table_widget.get_model().connect("row-changed", self.__status_bar.on_comments_row_changed)
        self.__table_widget.get_model().connect("row-deleted", self.__status_bar.on_comments_row_changed)
        self.__table_widget.get_model().connect("row-inserted", self.__status_bar.on_comments_row_changed)
        # Connect events: QC-Manager
        self.__qc_manager.connect(MPVQC_STATUSBAR_UPDATE, self.__status_bar.update_statusbar_message)
        self.__qc_manager.connect(MPVQC_QC_STATE_CHANGED, self.__update_title)
        self.__qc_manager.connect(MPVQC_QC_STATE_CHANGED, self.__search_frame.clear_current_matches)

        # Class variables
        self.__is_fullscreen = False
        self.__video_file_name = ""
        self.__video_file_path = ""

        self.__on_mpv_player_realized()

    @property
    def __parent(self) -> MpvqcWindow:
        return self.get_parent().get_parent()

    @property
    def header_bar(self) -> Gtk.HeaderBar:
        return self._header_bar

    @property
    def can_quit(self) -> bool:
        """Returns True, if can quit (state is saved), False else"""

        return self.__qc_manager.request_quit_application()

    @template.TemplateTrans.Callback()
    def _on_button_new_clicked(self, *_) -> None:
        self.__qc_manager.request_new_document()

    @template.TemplateTrans.Callback()
    def _on_button_open_clicked(self, button: Gtk.Button, *_) -> None:
        self.__popover_open.set_relative_to(button)
        self.__popover_open.popup()

    @template.TemplateTrans.Callback()
    def _on_button_save_clicked(self, *_) -> None:
        self.__qc_manager.request_save_qc_document()

    @template.TemplateTrans.Callback()
    def _on_button_save_as_clicked(self, *_) -> None:
        self.__qc_manager.request_save_qc_document_as()

    @template.TemplateTrans.Callback()
    def _on_button_dark_theme_clicked(self, *_) -> None:
        s = get_settings()
        s.prefer_dark_theme = not s.prefer_dark_theme

        self._button_dark_theme.set_property("active", s.prefer_dark_theme)
        Gtk.Settings.get_default().set_property("gtk-application-prefer-dark-theme", s.prefer_dark_theme)

    @template.TemplateTrans.Callback()
    def _on_button_preferences_clicked(self, *_) -> None:
        self.__video_widget.player.pause()
        self.__parent.show_pref()

    @template.TemplateTrans.Callback()
    def _on_button_shortcuts_clicked(self, *_) -> None:
        self.__video_widget.player.pause()
        overlay = ShortcutWindow()
        overlay.set_transient_for(self.__parent)
        overlay.show_all()

    @template.TemplateTrans.Callback()
    def _on_button_about_clicked(self, *_) -> None:
        self.__video_widget.player.pause()
        about = AboutDialog()
        about.set_transient_for(self.__parent)
        about.run()
        about.destroy()

    def on_key_press_event(self, widget: Gtk.Widget, event: Gdk.EventKey) -> bool:
        """Returns True if handled, False else"""

        no_mod, ctrl, alt, shift = keyboard.extract_modifiers(event.state)
        key = event.keyval

        if ctrl:
            if alt and key == Gdk.KEY_s:  # CTRL + ALT + s
                self._on_button_preferences_clicked()
                return True

            if key == Gdk.KEY_n:  # CTRL + n
                self._on_button_new_clicked()
                return True
            if key == Gdk.KEY_o:  # CTRL + o
                self.__popover_open.on_button_qc_clicked()
                return True
            if key == Gdk.KEY_O:  # CTRL + O (= CTRL + SHIFT + o)
                self.__popover_open.on_button_video_clicked()
                return True
            if key == Gdk.KEY_s:  # CTRL + s
                self._on_button_save_clicked()
                return True
            if key == Gdk.KEY_S:  # CTRL + S (= CTRL + SHIFT + s)
                self._on_button_save_as_clicked()
                return True
            if key == Gdk.KEY_q:  # CTRL + q
                self.__parent.close()
                return True
            if key == Gdk.KEY_F1:  # CTRL + F1
                self._on_button_shortcuts_clicked()
                return True
            if key == Gdk.KEY_f:  # CTRL + f
                self.__search_frame.toggle_search()
                return True

        if self.__is_fullscreen:
            self.__video_widget.on_key_press_event(widget, event, is_fullscreen=True)
            return True

        return False

    def fullscreen(self) -> None:
        self.__is_fullscreen = True
        self.__status_bar.hide()
        self.__table_widget.before_hide()
        self._overlay.hide()

    def unfullscreen(self) -> None:
        self.__is_fullscreen = False
        self._overlay.show()
        self.__table_widget.after_show()
        self.__status_bar.show()
        self.__table_widget.grab_focus()

    def after_preferences_closed(self) -> None:
        """
        Called after the user navigates back from the preferences
        """

        self.__qc_manager.reset_auto_save()
        self.__update_subtitle()
        self.focus_table_widget()

    def focus_table_widget(self) -> None:
        """
        Sets the focus manually to the table widget.
        """

        self.__table_widget.grab_focus()

    def set_paned_grabber_to(self, position: int) -> None:
        """
        Sets the grabber to position. 0 means top.
        """

        self._paned.set_position(position)

    def __on_drag_data_received(self, _, drag_context, __, ___, data, ____, time) -> None:
        """
        Handles the drag event which is received on video and table.
        """

        videos, qc_documents, subtitle_documents = draganddrop.parse_dropped_data(data=data)
        drag_context.finish(True, False, time)
        self.__qc_manager.do_open_drag_and_drop_data(videos, qc_documents, subtitle_documents)

    def __on_mpv_player_realized(self, *_) -> None:
        """
        As soon as the player is ready, connect signals to obtain info about video file and file path.

        :param widget: the mpv widget (not player!)
        """

        mpv = self.__video_widget.player

        def __on_file_name_changed(_, value: str) -> None:
            self.__video_file_name = value
            self.__update_subtitle()

        def __on_file_path_changed(_, value: str) -> None:
            self.__video_file_path = value
            self.__update_subtitle()
            GLib.idle_add(__on_new_file_was_loaded, None, GLib.PRIORITY_DEFAULT)

        def __on_new_file_was_loaded(*_):
            # Wait until new video information is available
            while not (mpv.video_width() and mpv.video_height()):
                time.sleep(0.05)
            self.__fire_event_new_video_loaded()

        mpv.connect(MPVQC_FILENAME_NO_EXT, __on_file_name_changed)
        mpv.connect(MPVQC_PATH, __on_file_path_changed)

    def __fire_event_new_video_loaded(self):
        player = self.__video_widget.player
        self.emit(
            MPVQC_NEW_VIDEO_LOADED,
            player.video_width(),
            player.video_height(),
        )

    def __update_title(self, _, has_changes) -> None:
        """
        Updates the title hinting to the current document state.
        """

        self._header_bar.set_title("{}mpvQC".format("*" if has_changes else ""))

    def __update_subtitle(self) -> None:
        value = get_settings().header_subtitle_format

        subtitle_enabled = value != 0 and self.__video_file_name and self.__video_file_path

        self._header_bar.set_property("has-subtitle", subtitle_enabled)

        if value == 0:
            self._header_bar.set_subtitle("")
        elif value == 1:
            self._header_bar.set_subtitle(self.__video_file_name)
        elif value == 2:
            self._header_bar.set_subtitle(self.__video_file_path)
