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


from enum import Enum
from numbers import Number


class MouseButton(Enum):
    LEFT = 1
    MIDDLE = 2
    RIGHT = 3
    BACK = 8
    FORWARD = 9

    def __eq__(self, other):
        if isinstance(other, Number):
            return self.value == other
        return super(MouseButton, self).__eq__(other)


class ActionType(Enum):
    """
    Action types for the MpvPlayer.
    """

    PRESS = "keypress"
    DOWN = "keydown"
    UP = "keyup"
