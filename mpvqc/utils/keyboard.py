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


import sys

from gi.repository import Gdk

__ALPHANUMERICS = "1234567890ABCDEFGHIJKLMNOPQRSTUVWXYZÄÖÜÀÁÂÃÇÉÈÊËÍÌÎÏÑÓÒÔÕÚÙÛÝŸ"

KEY_MAPPINGS = {
    Gdk.KEY_Page_Up: ("PGUP",),
    Gdk.KEY_Page_Down: ("PGDWN",),
    Gdk.KEY_AudioPlay: ("PLAY",),
    Gdk.KEY_AudioRandomPlay: ("PLAY",),
    Gdk.KEY_3270_Play: ("PLAY",),
    Gdk.KEY_Pause: ("PAUSE",),
    Gdk.KEY_AudioPause: ("PAUSE",),
    Gdk.KEY_Stop: ("STOP",),
    Gdk.KEY_AudioStop: ("STOP",),
    Gdk.KEY_Forward: ("FORWARD",),
    Gdk.KEY_AudioRewind: ("REWIND",),
    Gdk.KEY_BackForward: ("REWIND",),
    Gdk.KEY_Next: ("NEXT",),
    Gdk.KEY_AudioNext: ("NEXT",),
    Gdk.KEY_AudioPrev: ("PREV",),
    Gdk.KEY_Home: ("HOME",),
    Gdk.KEY_End: ("END",),
    Gdk.KEY_Escape: ("ESC",),
    Gdk.KEY_Left: ("LEFT",),
    Gdk.KEY_Right: ("RIGHT",),
    Gdk.KEY_Up: ("UP", True),
    Gdk.KEY_Down: ("DOWN", True),
    Gdk.KEY_Control_L: ("",),
    Gdk.KEY_Control_R: ("",),
    Gdk.KEY_Super_L: ("",),
    Gdk.KEY_Super_R: ("",),
    Gdk.KEY_Alt_L: ("",),
    Gdk.KEY_Alt_R: ("",),
    Gdk.KEY_ISO_Level3_Shift: ("",),
    Gdk.KEY_Shift_L: ("",),
    Gdk.KEY_Shift_R: ("",),
    Gdk.KEY_Caps_Lock: ("",),
    Gdk.KEY_Tab: ("",),
    Gdk.KEY_Menu: ("",),
}


def extract_modifiers(state):
    """
    Extracts modifiers from a key press event.
    Ctrl, alt and shift are True if they are pressed during the event of parameter state.

    :param state: event.state of a key press event
    :return: a list with values set to true as [no, ctrl, alt, shift]
    """

    ctrl = state & Gdk.ModifierType.CONTROL_MASK
    shift = state & Gdk.ModifierType.SHIFT_MASK
    # super = state & Gdk.ModifierType.SUPER_MASK
    alt = state & Gdk.ModifierType.MOD1_MASK
    no = not ctrl and not shift and not alt
    return no, bool(ctrl), bool(alt), bool(shift)


def command_generator(ctrl, alt, shift, key_str, mod_required=False, is_char=False):
    """
    Generates a command for the mpv player using the given commands.

    :param ctrl: True, if CTRL modifier, False else.
    :param alt: True, if ALT modifier, False else.
    :param shift: True, if SHIFT modifier, False else.
    :param key_str: The key string to delegate to mpv
    :param mod_required: True if modifier required, False else
    :param is_char: Whether key_str is explicitly a char
    :return: The key-string to delegate to mpv if allowed. None else.
    """

    if not key_str:
        return ""

    shift = "shift" if shift else ""
    ctrl = "ctrl" if ctrl else ""
    alt = "alt" if alt else ""

    if mod_required and not (shift or ctrl or alt):
        return None

    if is_char:
        if key_str not in __ALPHANUMERICS and sys.platform.startswith("win32"):
            ctrl = None
            alt = None
        if not shift and key_str in __ALPHANUMERICS:
            key_str = key_str.lower()
        shift = None

    return "+".join([x for x in [shift, ctrl, alt, key_str] if x])
