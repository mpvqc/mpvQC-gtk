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

import mpvqc.utils.signals as signals
from mpvqc import get_settings, template
from mpvqc.ui.messagestack import MessageStack
from mpvqc.utils import StatusbarMessageDuration, seconds_float_to_formatted_string_hours


@template.TemplateTrans(resource_path='/data/ui/statusbar.ui')
class StatusBar(Gtk.Box):
    __gtype_name__ = 'StatusBar'

    label_line = template.TemplateTrans.Child()
    label_button_time = template.TemplateTrans.Child()

    popover_time = template.TemplateTrans.Child()

    time_menu_default = template.TemplateTrans.Child()
    time_menu_current = template.TemplateTrans.Child()
    time_menu_remaining = template.TemplateTrans.Child()
    time_menu_no = template.TemplateTrans.Child()

    time_menu_percentage = template.TemplateTrans.Child()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.init_template()

        self.message_stack = MessageStack()
        self.pack_start(self.message_stack, expand=True, fill=True, padding=0)

        # Updated by player signals
        self.__time_duration = ""
        self.__time_remaining = ""
        self.__time_current = ""
        self.__percent = ""

        # State variables for formatting
        self.__duration = None
        self.__short = False

        # Updated by table model signals
        self.__comment_count = None
        self.__comment_selected = None

        # Set up radio selection
        self.__time_menu = {
            0: self.time_menu_default,
            1: self.time_menu_current,
            2: self.time_menu_remaining,
            3: self.time_menu_no,
        }
        self.__time_menu.get(get_settings().status_bar_time_format, 0).set_property("active", True)

        for idx, entry in self.__time_menu.items():
            entry.set_property("role", Gtk.ButtonRole.RADIO)
            entry.connect("clicked", lambda w, v=idx: self.__on_time_format_item_clicked(v))

        # Set up check selection
        self.time_menu_percentage.set_property("active", get_settings().status_bar_percentage)
        self.time_menu_percentage.set_property("role", Gtk.ButtonRole.CHECK)
        self.time_menu_percentage.connect("clicked", self.__on_percentage_item_clicked)

        # Set up timer
        self.connect("destroy", self.__on_destroy)
        self.__time_update_timer = None

    @template.TemplateTrans.Callback()
    def on_label_button_time_clicked(self, *_):
        self.popover_time.set_relative_to(self.label_button_time)
        self.popover_time.popup()

    def on_mpv_player_realized(self, widget, *_):
        """
        As soon as the player is ready, connect signals to obtain info about player time and state.

        :param widget: the mpv widget (not player!)
        """

        mpv = widget.player

        def __on_player_duration_changed(_, value):
            self.__duration = value
            self.__short = value < 3600.0
            self.__time_duration = seconds_float_to_formatted_string_hours(value, short=self.__short)

        def __on_player_time_pos_changed(_, value):
            if self.__duration:
                self.__time_current = seconds_float_to_formatted_string_hours(value, short=self.__short)

        def __on_player_percent_pos_changed(_, value):
            if self.__duration:
                self.__percent = "{0:3.0f}%".format(round(value))

        def __on_player_time_remaining_changed(_, value):
            if self.__duration:
                self.__time_remaining = seconds_float_to_formatted_string_hours(value, short=self.__short)

        mpv.connect(signals.MPVQC_DURATION, __on_player_duration_changed)
        mpv.connect(signals.MPVQC_TIME_POS, __on_player_time_pos_changed)
        mpv.connect(signals.MPVQC_PERCENT_POS, __on_player_percent_pos_changed)
        mpv.connect(signals.MPVQC_TIME_REMAINING, __on_player_time_remaining_changed)

        self.__time_update_timer = GLib.timeout_add(75, self.__on_video_timer_timeout)

    def on_comments_selection_change(self, widget):
        """
        Called whenever the selection of the table widget has changed.

        :param widget: passed in from event
        """

        rows = widget.get_selected_rows()[1]
        if rows:
            self.__comment_selected = str(int(rows[0].to_string()) + 1)
            self.__on_line_label_update()

    def on_comments_row_changed(self, model, idx, *_):
        """
        Called whenever a row of the table widget has changed.

        :param model: passed in from event
        :param idx: passed in from event
        """

        model_length = len(model)
        self.__comment_count = str(model_length)

        # If a row changes it must have been selected.
        # It is needed here, because after a time change the selection event is not fired.
        self.__comment_selected = str(min(int(idx.to_string()) + 1, model_length))

        self.__on_line_label_update()

    def update_statusbar_message(self, _, message: str, sb_message_duration=StatusbarMessageDuration.SHORT):
        """
        Updates the current statusbar message.
        """

        def __display():
            self.message_stack.display_message(message, sb_message_duration)

        # Delay status messages because timer on the bottom right might not have allocated its place.
        # Delay will avoid an ugly movement in the status bar
        if not self.__time_current:
            GLib.timeout_add(250, __display)
        else:
            __display()

    def __on_time_format_item_clicked(self, nr):
        """
        Updates the time format setting and manages the toggle group. With the next timeout the setting gets applied.

        :param nr: the new key of the time_menu to apply
        """

        get_settings().status_bar_time_format = nr

        for idx, entry in self.__time_menu.items():
            if idx == nr:
                entry.set_property("active", True)
            else:
                entry.set_property("active", False)

    def __on_percentage_item_clicked(self, *_):
        """
        Updates the percentage setting. With the next timeout the setting gets applied.

        :param nr: the new key of the time_menu to apply
        """

        new_value = not self.time_menu_percentage.get_property("active")

        get_settings().status_bar_percentage = new_value
        self.time_menu_percentage.set_property("active", new_value)

    def __on_video_timer_timeout(self, *_):
        """
        Updates the status bar periodically.
        Kick off in 'on_mpv_player_realized'

        :return: True if continue timer, False else
        """

        s = get_settings()
        p_value = s.status_bar_percentage
        tf_value = s.status_bar_time_format
        video_loaded = self.__time_current

        if tf_value == 0 and video_loaded:
            time = "{0}/{1}".format(self.__time_current, self.__time_duration)
        elif tf_value == 1 and video_loaded:
            time = self.__time_current
        elif tf_value == 2 and video_loaded:
            time = "-" + self.__time_remaining
        else:
            time = ""

        if p_value:
            percent = self.__percent
        else:
            percent = ""

        self.label_button_time.set_label(
            "{}      {}".format(percent, time).strip() + ("   " if video_loaded and (time or p_value) else "")
        )

        return True

    def __on_line_label_update(self):
        """
        Updates the line label. This is not called periodically from a timer.
        """

        if self.__comment_selected == '0' or self.__comment_count == '0':
            self.label_line.set_text("")
        elif self.__comment_selected and self.__comment_count:
            selected = self.__comment_selected.zfill(len(self.__comment_count))
            self.label_line.set_text("{}/{}".format(selected, self.__comment_count))

    def __on_destroy(self, *_):
        GLib.source_remove(self.__time_update_timer)
