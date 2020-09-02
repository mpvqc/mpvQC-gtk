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


from locale import gettext as _

from gi.repository import Gtk, Gdk

from mpvqc import get_settings, get_app
from mpvqc.qc.manager import QcManager
from mpvqc.ui.about import AboutDialog
from mpvqc.ui.contentmainmpv import ContentMainMpv
from mpvqc.ui.contentmaintable import ContentMainTable
from mpvqc.ui.popoveropen import PopoverOpen
from mpvqc.ui.prefpagegeneral import PreferencePageGeneral
from mpvqc.ui.prefpageimexport import PreferencePageExport
from mpvqc.ui.prefpageinput import PreferencePageInput
from mpvqc.ui.prefpagempv import PreferencePageMpv
from mpvqc.ui.searchframe import SearchFrame
from mpvqc.ui.statusbar import StatusBar
from mpvqc.utils import draganddrop, keyboard
from mpvqc.utils.shortcuts import ShortcutWindow
from mpvqc.utils.signals import FILENAME_NO_EXT, PATH, STATUSBAR_UPDATE, QC_STATE_CHANGED


@Gtk.Template(resource_path='/data/ui/window.ui')
class MpvqcWindow(Gtk.ApplicationWindow):
    __gtype_name__ = 'MpvqcWindow'

    stack_content = Gtk.Template.Child()  # Stack for content
    stack_header_bar = Gtk.Template.Child()  # Stack for header bar

    header_bar_main = Gtk.Template.Child()  # Header bar for main view
    header_bar_preferences = Gtk.Template.Child()  # Header bar for preferences view

    content_main = Gtk.Template.Child()  # Content for main view
    content_preferences = Gtk.Template.Child()  # Stack and content for preferences view

    preferences_stack_switcher = Gtk.Template.Child()

    content_main_pane = Gtk.Template.Child()  # Paned widget for video and table

    button_open = Gtk.Template.Child()
    button_preferences_restore = Gtk.Template.Child()

    button_dark_theme = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.init_template()
        s = get_settings()

        # Size and theme settings
        self.set_default_size(s.app_window_width, s.app_window_height)
        self.button_dark_theme.set_property("role", Gtk.ButtonRole.CHECK)
        self.button_dark_theme.set_property("active", s.prefer_dark_theme)
        Gtk.Settings.get_default().set_property("gtk-application-prefer-dark-theme", s.prefer_dark_theme)

        # Widgets loaded from UI templates
        self.__video_widget = ContentMainMpv(self)
        self.__table_widget = ContentMainTable(self.__video_widget)
        self.__qc_manager = QcManager(self, self.__video_widget, self.__table_widget)
        self.__popover_open = PopoverOpen(self, self.__qc_manager)
        self.__status_bar = StatusBar()
        self.__search_frame = SearchFrame(self.__table_widget)

        # Populate preferences stack from UI templates
        self.__preferences_page_general = PreferencePageGeneral()
        self.__preferences_page_export = PreferencePageExport()
        self.__preferences_page_input = PreferencePageInput()
        self.__preferences_page_mpv = PreferencePageMpv()

        self.__preferences_page_general.show_all()
        self.__preferences_page_export.show_all()
        self.__preferences_page_input.show_all()
        self.__preferences_page_mpv.show_all()

        self.content_preferences.add_titled(self.__preferences_page_general, "General", _("General"))
        self.content_preferences.add_titled(self.__preferences_page_export, "Import/Export", _("Im-/Export"))
        self.content_preferences.add_titled(self.__preferences_page_input, "input.conf", _("Input"))
        self.content_preferences.add_titled(self.__preferences_page_mpv, "mpv.conf", _("Video"))

        self.content_preferences.set_visible_child(self.__preferences_page_general)

        # Pack widgets -> Container for table
        self.table_container = Gtk.ScrolledWindow()
        self.table_container.add(self.__table_widget)
        self.table_container.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.table_container.show_all()

        # Pack widgets -> Overlay using container table as main child and search revealer as overlay
        self.table_container_overlay = Gtk.Overlay()
        self.table_container_overlay.add(self.table_container)
        self.table_container_overlay.add_overlay(self.__search_frame)
        self.table_container_overlay.show_all()

        # Pack1: EventBox { Label { "mpv drawing area" }}
        # Pack2: Overlay { ScrolledWindow { TreeView }}
        self.content_main_pane.pack1(self.__video_widget, resize=True, shrink=True)
        self.content_main_pane.pack2(self.table_container_overlay, resize=True, shrink=False)
        self.content_main.pack_start(self.__status_bar, expand=False, fill=True, padding=0)

        # Set up drag and drop
        target = Gtk.TargetEntry.new(target="text/uri-list", flags=Gtk.TargetFlags.OTHER_APP, info=0)
        self.content_main_pane.drag_dest_set(Gtk.DestDefaults.ALL, [target], Gdk.DragAction.COPY)
        self.content_main_pane.connect("drag-data-received", self.__on_drag_data_received)

        # Set video size
        self.content_main_pane.set_position(s.app_window_video_height)

        # Set up remaining connections
        # 1. Set up player as soon as possible
        self.__video_widget.connect("realize", self.__status_bar.on_mpv_player_realized)
        self.__video_widget.connect("realize", self.__on_mpv_player_realized)
        # 2. All key events are first handled in the mpv widget,
        # and then if not consumed they will be delegated to the table widget.
        self.__table_widget.connect("key-press-event", self.__video_widget.on_key_press_event)
        self.__table_widget.connect("key-press-event", self.__table_widget.on_key_press_event)
        self.__table_widget.connect("key-press-event", self.__search_frame.on_key_press_event)
        # 3. Selection change and model change events for status bar and qc manager
        self.__table_widget.get_selection().connect("changed", self.__status_bar.on_comments_selection_change)
        self.__table_widget.get_model().connect("row-changed", self.__status_bar.on_comments_row_changed)
        self.__table_widget.get_model().connect("row-deleted", self.__status_bar.on_comments_row_changed)
        self.__table_widget.get_model().connect("row-inserted", self.__status_bar.on_comments_row_changed)
        self.__qc_manager.connect(STATUSBAR_UPDATE, self.__status_bar.update_statusbar_message)
        self.__qc_manager.connect(QC_STATE_CHANGED, self.__update_title)
        self.__qc_manager.connect(QC_STATE_CHANGED, self.__search_frame.clear_current_matches)

        # Class variables
        self.__is_fullscreen = False
        self.__full_screen_handler = None
        self.__video_file_name = ""
        self.__video_file_path = ""

        # Shortcuts
        self.__set_up_keyboard_shortcuts()

        # Welcome message
        if s.export_qc_document_nick == "nickname":
            nickname = _("nickname")
        else:
            nickname = s.export_qc_document_nick
        self.__status_bar.update_statusbar_message(None, _("Welcome back {}!").format(nickname))

    @Gtk.Template.Callback()
    def on_button_new_clicked(self, *widget):
        self.__qc_manager.request_new_document()

    @Gtk.Template.Callback()
    def on_button_open_clicked(self, widget):
        self.__popover_open.set_relative_to(self.button_open)
        self.__popover_open.popup()

    @Gtk.Template.Callback()
    def on_button_save_clicked(self, *widget):
        self.__qc_manager.request_save_qc_document()

    @Gtk.Template.Callback()
    def on_button_save_as_clicked(self, *widget):
        self.__qc_manager.request_save_qc_document_as()

    @Gtk.Template.Callback()
    def on_button_dark_theme_toggle_clicked(self, *data):
        s = get_settings()
        s.prefer_dark_theme = not s.prefer_dark_theme

        self.button_dark_theme.set_property("active", s.prefer_dark_theme)
        Gtk.Settings.get_default().set_property("gtk-application-prefer-dark-theme", s.prefer_dark_theme)

    @Gtk.Template.Callback()
    def on_button_preferences_back_clicked(self, widget):
        self.stack_header_bar.set_visible_child(self.header_bar_main)
        self.stack_content.set_visible_child(self.content_main)
        self.content_preferences.set_visible_child(self.__preferences_page_general)
        self.__preferences_page_general.on_preferences_closed()
        self.__qc_manager.reset_auto_save()
        self.__update_subtitle()
        self.__table_widget.grab_focus()

    @Gtk.Template.Callback()
    def on_button_preferences_restore_default_clicked(self, widget, data=None):
        self.content_preferences.get_visible_child().on_restore_default_clicked()

    @Gtk.Template.Callback()
    def on_menu_shortcuts_clicked(self, *widget):
        self.__video_widget.player.pause()
        overlay = ShortcutWindow()
        overlay.set_transient_for(self)
        overlay.set_position(Gtk.WindowPosition.CENTER_ALWAYS)
        overlay.show_all()

    @Gtk.Template.Callback()
    def on_menu_preferences_clicked(self, *widget):
        self.__video_widget.player.pause()
        self.stack_header_bar.set_visible_child(self.header_bar_preferences)
        self.stack_content.set_visible_child(self.content_preferences)

    @Gtk.Template.Callback()
    def on_menu_about_clicked(self, *widget):
        self.__video_widget.player.pause()
        about = AboutDialog(application=self.get_application())
        about.set_transient_for(self)
        about.run()
        about.destroy()

    @Gtk.Template.Callback()
    def on_key_press_event(self, widget, event):
        no_mod, ctrl, alt, shift = keyboard.extract_modifiers(event.state)
        key = event.keyval

        if key == Gdk.KEY_Escape and no_mod and self.stack_content.get_visible_child() == self.content_preferences:
            self.on_button_preferences_back_clicked(None)
            return True

    def do_delete_event(self, *args, **kwargs):
        """
        Asks the qc manager whether all changes are saved and displays a dialog if required,
        otherwise quits immediately.
        """

        do_quit = self.__qc_manager.request_quit_application()
        if not do_quit:
            return True

        size = self.get_size()

        s = get_settings()
        s.app_window_height = size.height
        s.app_window_width = size.width
        s.app_window_video_height = self.__video_widget.get_allocated_height()
        s.write_config_file_input_content()
        s.write_config_file_mpv_content()

        return False

    def toggle_fullscreen(self, *data):
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

        self.__is_fullscreen = True

        def __on_fullscreen(widget, event):
            """
            Delegate key events to mpv widget
            """

            self.__video_widget.on_key_press_event(widget, event, is_fullscreen=True)
            self.__table_widget.grab_focus()
            return True

        self.__full_screen_handler = self.connect("key-press-event", __on_fullscreen)
        self.__status_bar.hide()
        self.__table_widget.before_hide()
        self.table_container_overlay.hide()
        super(MpvqcWindow, self).fullscreen()

    def unfullscreen(self):
        """
        Action when "f" (fullscreen key) is pressed and app is fullscreen.
        """

        if not self.__is_fullscreen:
            return

        super(MpvqcWindow, self).unfullscreen()
        self.__is_fullscreen = False

        if self.__full_screen_handler and self.handler_is_connected(self.__full_screen_handler):
            self.disconnect(self.__full_screen_handler)

        self.table_container_overlay.show()
        self.__table_widget.after_show()
        self.__status_bar.show()

    def focus_table_widget(self):
        """
        Sets the focus manually to the table widget.
        """

        self.__table_widget.grab_focus()

    def __on_drag_data_received(self, widget, drag_context, x, y, data, info, time):
        """
        Handles the drag event which is received on video and table.
        """

        videos, qc_documents, subtitle_documents = draganddrop.parse_dropped_data(data=data)
        drag_context.finish(True, False, time)
        self.__qc_manager.do_open_drag_and_drop_data(videos, qc_documents, subtitle_documents)

    def __on_mpv_player_realized(self, widget, *data):
        """
        As soon as the player is ready, connect signals to obtain info about video file and file path.

        :param widget: the mpv widget (not player!)
        :param data: not relevant, passed in by event
        """

        mpv = widget.player

        def __on_file_name_changed(widget, value):
            self.__video_file_name = value
            self.__update_subtitle()
            self.__popover_open.on_video_opened()

        def __on_file_path_changed(widget, value):
            self.__video_file_path = value
            self.__update_subtitle()

        mpv.connect(FILENAME_NO_EXT, __on_file_name_changed)
        mpv.connect(PATH, __on_file_path_changed)

    def __update_title(self, widget, status):
        """
        Updates the title hinting to the current document state.
        """

        self.header_bar_main.set_title("{}mpvQC".format("" if status else "*"))

    def __update_subtitle(self):
        value = get_settings().header_subtitle_format

        subtitle_enabled = value != 0 and self.__video_file_name and self.__video_file_path

        self.header_bar_main.set_property("has-subtitle", subtitle_enabled)

        if value == 0:
            self.header_bar_main.set_subtitle("")
        elif value == 1:
            self.header_bar_main.set_subtitle(self.__video_file_name)
        elif value == 2:
            self.header_bar_main.set_subtitle(self.__video_file_path)

    def __set_up_keyboard_shortcuts(self):
        """
        Sets up keyboard shortcuts relevant in this widget's context.
        """

        def __destroy(*data):
            quit = not self.do_delete_event()
            if quit:
                get_app().quit()

        a = Gtk.AccelGroup()
        a.connect(
            accel_key=Gdk.KEY_n,
            accel_mods=Gdk.ModifierType.CONTROL_MASK,
            accel_flags=Gtk.AccelFlags.VISIBLE,
            closure=self.on_button_new_clicked
        )
        a.connect(
            accel_key=Gdk.KEY_s,
            accel_mods=Gdk.ModifierType.CONTROL_MASK,
            accel_flags=Gtk.AccelFlags.VISIBLE,
            closure=self.on_button_save_clicked
        )
        a.connect(
            accel_key=Gdk.KEY_s,
            accel_mods=Gdk.ModifierType.CONTROL_MASK | Gdk.ModifierType.SHIFT_MASK,
            accel_flags=Gtk.AccelFlags.VISIBLE,
            closure=self.on_button_save_as_clicked
        )
        a.connect(
            accel_key=Gdk.KEY_q,
            accel_mods=Gdk.ModifierType.CONTROL_MASK,
            accel_flags=Gtk.AccelFlags.VISIBLE,
            closure=__destroy
        )
        a.connect(
            accel_key=Gdk.KEY_s,
            accel_mods=Gdk.ModifierType.CONTROL_MASK | Gdk.ModifierType.MOD1_MASK,
            accel_flags=Gtk.AccelFlags.VISIBLE,
            closure=self.on_menu_preferences_clicked
        )
        a.connect(
            accel_key=Gdk.KEY_F1,
            accel_mods=Gdk.ModifierType.CONTROL_MASK,
            accel_flags=Gtk.AccelFlags.VISIBLE,
            closure=self.on_menu_shortcuts_clicked
        )
        self.add_accel_group(a)
