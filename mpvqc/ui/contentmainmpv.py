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


from gi.repository import Gtk, Gdk, GObject

import mpvqc.utils.signals as signals
from mpvqc import get_settings, template
from mpvqc.player.container import get_mpv_widget, MpvPlayer
from mpvqc.ui.contentmain import ContentMain
from mpvqc.ui.window import MpvqcWindow
from mpvqc.utils import keyboard
from mpvqc.utils.input import MouseButton, ActionType
from mpvqc.utils.keyboard import KEY_MAPPINGS


@template.TemplateTrans(resource_path='/data/ui/contentmainmpv.ui')
class ContentMainMpv(Gtk.EventBox):
    __gtype_name__ = 'ContentMainMpv'

    __gsignals__ = {
        signals.MPVQC_CREATE_NEW_COMMENT: (GObject.SignalFlags.RUN_FIRST, None, (str, str,)),
    }

    def __init__(self, content_main: ContentMain, mpvqc_window: MpvqcWindow, **kwargs):
        super().__init__(**kwargs)
        self.__content_main = content_main
        self.__mpvqc_window = mpvqc_window
        self.init_template()

        container = get_mpv_widget(self)
        container.show()
        self.add(container)

        self.__mpv = container.player

    @property
    def player(self) -> MpvPlayer:
        return self.__mpv

    @template.TemplateTrans.Callback()
    def on_mouse_move_event(self, _, event) -> bool:
        scale_factor = self.get_scale_factor()
        self.__mpv.mouse_move(int(event.x * scale_factor), int(event.y * scale_factor))
        return True

    @template.TemplateTrans.Callback()
    def on_scroll_event(self, _, event) -> bool:
        direction = event.direction

        if direction == Gdk.ScrollDirection.UP:
            self.__mpv.mouse_action(3, ActionType.PRESS)
        elif direction == Gdk.ScrollDirection.DOWN:
            self.__mpv.mouse_action(4, ActionType.PRESS)
        else:
            return False
        return True

    @template.TemplateTrans.Callback()
    def on_button_press_event(self, _, event) -> bool:
        btn = event.button
        typ = event.type

        self.__content_main.focus_table_widget()

        # todo in future: Double and triple-clicks result in a sequence of events being received.
        #  For double-clicks the order of events will be:
        # make this feel nice!
        # GDK_BUTTON_RELEASE
        # GDK_BUTTON_PRESS
        # GDK_2BUTTON_PRESS
        # GDK_BUTTON_RELEASE

        if typ == Gdk.EventType.DOUBLE_BUTTON_PRESS and btn == MouseButton.LEFT and self.player.is_video_loaded():
            self.__mpvqc_window.toggle_fullscreen()
            return True
        elif typ == Gdk.EventType.BUTTON_PRESS:
            if btn == MouseButton.LEFT:
                self.__mpv.mouse_action(0, ActionType.DOWN)
            elif btn == MouseButton.MIDDLE:
                self.__mpv.mouse_action(1, ActionType.PRESS)
            elif btn == MouseButton.RIGHT:
                self.__mpvqc_window.unfullscreen()
                self.__create_context_menu(btn, event.time)
            elif btn == MouseButton.BACK:
                self.__mpv.mouse_action(5, ActionType.PRESS)
            elif btn == MouseButton.FORWARD:
                self.__mpv.mouse_action(6, ActionType.PRESS)
            else:
                return False
            return True
        return False

    @template.TemplateTrans.Callback()
    def on_button_release_event(self, _: Gtk.Widget, event) -> bool:
        btn = event.button

        if btn == MouseButton.LEFT:
            self.__mpv.mouse_action(0, ActionType.UP)
            return True

        return False

    def on_key_press_event(self, _: Gtk.Widget, event: Gdk.EventKey, is_fullscreen: bool = False) -> bool:
        """Returns True if handled, False else"""

        no_mod, ctrl, alt, shift = keyboard.extract_modifiers(event.state)
        key = event.keyval
        cmd = ""

        # Handled by table
        if key == Gdk.KEY_Up \
                or key == Gdk.KEY_Down \
                or key == Gdk.KEY_Delete \
                or key == Gdk.KEY_Return \
                or key == Gdk.KEY_BackSpace \
                or no_mod and not is_fullscreen and key == Gdk.KEY_Escape:
            return False

        # Handled by this widget
        if no_mod and key == Gdk.KEY_f and self.player.is_video_loaded():
            self.__mpvqc_window.toggle_fullscreen()
            return True
        elif no_mod and key == Gdk.KEY_e and self.player.is_video_loaded():
            self.__mpvqc_window.unfullscreen()
            self.__create_context_menu(key, event.time)
            return True
        elif no_mod and key == Gdk.KEY_Escape:
            self.__mpvqc_window.unfullscreen()
            return True
        elif key in KEY_MAPPINGS:
            cmd = keyboard.command_generator(ctrl, alt, shift, *KEY_MAPPINGS[key])
        elif key != 0:
            try:
                ks = chr(key)
            except ValueError:
                pass
            else:
                cmd = keyboard.command_generator(ctrl, alt, shift, ks, is_char=True)

        if cmd and self.player.is_video_loaded():
            self.player.button_action(cmd, ActionType.PRESS)
            return True
        return False

    def __create_context_menu(self, button, time) -> None:
        """
        Creates a new context menu filled with all current comment types.

        :param button: The button which requested the event.
        :param time: The time of the event.
        """

        if not self.__mpv.is_video_loaded():
            return

        self.__mpv.pause()

        def __on_clicked(value) -> None:
            self.emit(signals.MPVQC_CREATE_NEW_COMMENT, self.__mpv.position_current()[1], value.get_label())

        menu = Gtk.Menu()
        menu.attach_to_widget(self, None)

        for item in get_settings().comment_types:
            menu_item = Gtk.MenuItem()
            menu_item.set_label(str(item))
            menu_item.connect("activate", __on_clicked)
            menu.add(menu_item)

        menu.show_all()
        menu.popup(None, None, None, data=None, button=button, activate_time=time)
