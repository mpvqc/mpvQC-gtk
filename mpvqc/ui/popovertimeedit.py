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


from gi.repository import Gtk, GObject, Gdk

from mpvqc import utils, template
from mpvqc.utils.signals import APPLY


@template.TemplateTrans(resource_path='/data/ui/popovertimeedit.ui')
class PopoverTimeEdit(Gtk.Popover):
    __gtype_name__ = 'PopoverTimeEdit'

    __gsignals__ = {
        APPLY: (GObject.SignalFlags.RUN_FIRST, None, (str,))
    }

    box = template.TemplateTrans.Child()
    label = template.TemplateTrans.Child()

    button_plus = template.TemplateTrans.Child()
    button_minus = template.TemplateTrans.Child()
    button_apply = template.TemplateTrans.Child()

    scale = template.TemplateTrans.Child()
    adjustment = template.TemplateTrans.Child()

    def __init__(self, table_widget, video_widget, current_time_str, **properties):
        super().__init__(**properties)
        self.__table_widget = table_widget
        self.__video_widget = video_widget
        self.init_template()

        max_value_float, __ = self.__video_widget.player.duration()
        current_time_int = utils.formatted_string_to_int(current_time_str)

        cur_value_int = min(current_time_int, max_value_float)
        cur_value_str = utils.seconds_float_to_formatted_string_hours(cur_value_int, short=False)

        self.adjustment.set_lower(0)
        self.adjustment.set_upper(max_value_float)
        self.adjustment.set_step_increment(1)
        self.adjustment.set_page_increment(1)

        self.scale.set_size_request(width=self.__table_widget.get_window().get_width() * 0.6, height=10)
        self.scale.set_draw_value(False)
        self.scale.show()

        self.label.set_text(cur_value_str)
        self.adjustment.set_value(cur_value_int)

    @template.TemplateTrans.Callback()
    def on_button_plus_clicked(self, *_):
        self.adjustment.set_value(self.adjustment.get_value() + 1)

    @template.TemplateTrans.Callback()
    def on_button_minus_clicked(self, *_):
        self.adjustment.set_value(self.adjustment.get_value() - 1)

    @template.TemplateTrans.Callback()
    def on_button_apply_clicked(self, *_):
        self.emit(APPLY, self.label.get_text())
        self.popdown()

    @template.TemplateTrans.Callback()
    def on_adjustment_value_changed(self, widget):
        formatted = utils.seconds_float_to_formatted_string_hours(widget.get_value(), short=False)
        self.label.set_text(formatted)
        self.__video_widget.player.position_jump(formatted)

    @template.TemplateTrans.Callback()
    def on_key_press_event(self, _: Gtk.Widget, event: Gdk.EventKey) -> bool:
        key = event.keyval

        if key == Gdk.KEY_Up:
            self.on_button_plus_clicked()
            return True
        elif key == Gdk.KEY_Down:
            self.on_button_minus_clicked()
            return True
        elif key == Gdk.KEY_Return:
            self.on_button_apply_clicked()
            return True

    @template.TemplateTrans.Callback()
    def on_scroll_event(self, _, event):
        direction = event.direction

        if direction == Gdk.ScrollDirection.UP:
            self.on_button_plus_clicked()
            return True
        elif direction == Gdk.ScrollDirection.DOWN:
            self.on_button_minus_clicked()
            return True
        return False
