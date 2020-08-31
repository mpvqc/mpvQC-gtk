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


"""
    This file contains only shortcuts/accelerators to display in the overlay. They may vary in future versions.

    Actual actions triggered by this accelerators are defined in other files.
"""

from collections import defaultdict
from locale import gettext as _

from gi.repository import Gtk

# Groups
_GROUP_DEFAULT = _("General")
_GROUP_VIDEO = _("Video")
_GROUP_COMMENTS = _("Comment types")
_GROUP_SEARCH = _("Search")

# Most used modifier
_CTRL = "<Control>"
_SHIFT = "<Shift>"
_ALT = "<Alt>"


class ShortcutWindow(Gtk.ShortcutsWindow):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        section = Gtk.ShortcutsSection()
        section.show()

        for shortcut_group, shortcut_list in ALL_SHORTCUTS.items():
            group = Gtk.ShortcutsGroup(title=shortcut_group)
            group.show()

            for shortcut in shortcut_list:
                cut = Gtk.ShortcutsShortcut(accelerator=shortcut.accelerator, title=shortcut.description)
                cut.show()
                group.add(cut)

            section.add(group)

        self.add(section)


""" Shortcut helpers are defined here"""


class Shortcut:

    def __init__(self, group, accelerator, description):
        self.group = group
        self.accelerator = " ".join([accelerator])
        self.description = description


def __grouped_by_group():
    """
    Groups accelerator by the 'group' attribute.

    :return: a dictionary with key:'group' and value:[Shortcut1, Shortcut2, Shortcut3, ...]
    """

    groups = defaultdict(list)
    for obj in __ALL_SHORTCUTS:
        groups[obj.group].append(obj)

    return groups


__ALL_SHORTCUTS = (
    #
    # Default
    #
    Shortcut(_GROUP_DEFAULT,
             accelerator=_CTRL + "n",
             description=_("Create a new document")),
    Shortcut(_GROUP_DEFAULT,
             accelerator=_CTRL + "o",
             description=_("Open document files")),
    Shortcut(_GROUP_DEFAULT,
             accelerator=_CTRL + _SHIFT + "o",
             description=_("Open video files")),
    Shortcut(_GROUP_DEFAULT,
             accelerator=_CTRL + "s",
             description=_("Save current document")),
    Shortcut(_GROUP_DEFAULT,
             accelerator=_CTRL + _SHIFT + "s",
             description=_("Save current document with a different name")),
    Shortcut(_GROUP_DEFAULT,
             accelerator=_CTRL + _ALT + "s",
             description=_("Open preferences")),
    Shortcut(_GROUP_DEFAULT,
             accelerator=_CTRL + "q",
             description=_("Quit the application")),
    Shortcut(_GROUP_DEFAULT,
             accelerator=_CTRL + "F1",
             description=_("Display shortcuts")),
    #
    # Video
    #
    Shortcut(_GROUP_VIDEO,
             accelerator="f",
             description=_("Enter/leave fullscreen mode")),
    Shortcut(_GROUP_VIDEO,
             accelerator="space",
             description=_("Play/pause")),
    Shortcut(_GROUP_VIDEO,
             accelerator="Left",
             description=_("Seek backward by 2 seconds")),
    Shortcut(_GROUP_VIDEO,
             accelerator="Right",
             description=_("Seek forward by 2 seconds")),
    Shortcut(_GROUP_VIDEO,
             accelerator=_SHIFT + "Left",
             description=_("Seek backward by 5 seconds to a keyframe")),
    Shortcut(_GROUP_VIDEO,
             accelerator=_SHIFT + "Right",
             description=_("Seek forward by 5 seconds to a keyframe")),
    Shortcut(_GROUP_VIDEO,
             accelerator="9",
             description=_("Increase volume")),
    Shortcut(_GROUP_VIDEO,
             accelerator="0",
             description=_("Decrease volume")),
    Shortcut(_GROUP_VIDEO,
             accelerator="m",
             description=_("Mute/unmute")),
    Shortcut(_GROUP_VIDEO,
             accelerator="comma",
             description=_("Go backward by one frame")),
    Shortcut(_GROUP_VIDEO,
             accelerator="period",
             description=_("Go forward by one frame")),
    Shortcut(_GROUP_VIDEO,
             accelerator="j",
             description=_("Cycle through subtitle tracks")),
    Shortcut(_GROUP_VIDEO,
             accelerator="#",  # todo find out this char
             description=_("Cycle through audio tracks")),
    Shortcut(_GROUP_VIDEO,
             accelerator="s",
             description=_("Screenshot of the unscaled video")),
    Shortcut(_GROUP_VIDEO,
             accelerator=_SHIFT + "s",
             description=_("Screenshot of the scaled video")),
    Shortcut(_GROUP_VIDEO,
             accelerator="b",
             description=_("Render subtitles at window/video resolution")),
    Shortcut(_GROUP_VIDEO,
             accelerator="i",
             description=_("Display statistics of the currently played video")),
    #
    # Comments
    #
    Shortcut(_GROUP_COMMENTS,
             accelerator="e",
             description=_("Open context menu")),
    Shortcut(_GROUP_COMMENTS,
             accelerator="BackSpace Return",
             description=_("Edit selected comment")),
    Shortcut(_GROUP_COMMENTS,
             accelerator="Delete",
             description=_("Delete selected comment")),
    #
    # Search
    #
    Shortcut(_GROUP_SEARCH,
             accelerator=_CTRL + "f",
             description=_("Toggle search")),
    Shortcut(_GROUP_SEARCH,
             accelerator=_CTRL + "g" + " " + "Return",
             description=_("Next result")),
    Shortcut(_GROUP_SEARCH,
             accelerator=_CTRL + _SHIFT + "g" + " " + _SHIFT + "Return",
             description=_("Previous result")),
    Shortcut(_GROUP_SEARCH,
             accelerator="Escape",
             description=_("Hide search")),
)

ALL_SHORTCUTS = __grouped_by_group()
