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


import re
from abc import ABCMeta, abstractmethod
from gettext import gettext as _

from mpvqc import get_settings

_REGEX_EMPTY = re.compile("\S+")
_REGEX_NICK = re.compile("^([a-zA-Z0-9-öäüÖÄÜ]|\s)*$")
_REGEX_COMMENT_TYPE = re.compile("^([a-zA-Z-öäüÖÄÜ]|\s)*$")


class Validator:
    __metaclass__ = ABCMeta

    @abstractmethod
    def validate(self, current_text):
        """
        Validates the current text and returns true if valid, or false and a message if not.

        :param current_text: the text to validate
        :return: a tuple(bool, str) with bool set to True if 'valid' and str the message to display if bool is False.
        """

        raise NotImplementedError


class NicknameValidator(Validator):
    """
    The validator for validating the nickname on change.
    """

    def validate(self, current_text):
        if not bool(_REGEX_EMPTY.match(current_text)):
            return False, _("The nickname must not be empty")

        if not bool(_REGEX_NICK.match(current_text)):
            return False, _("Allowed characters are letters, numbers, spaces and minus")

        return True, ""


class NewCommentTypeValidator(Validator):
    """
    The validator for validating new comments.
    """

    def validate(self, current_text):
        if not bool(_REGEX_EMPTY.match(current_text)):
            return False, _("A type must not be empty")

        if current_text in get_settings().comment_types:
            return False, _("A type with that name already exists")

        if not bool(_REGEX_COMMENT_TYPE.match(current_text)):
            return False, _("Allowed characters are letters, spaces and minus")

        return True, ""


class ExistingCommentTypeValidator(Validator):
    """
    The validator for validating existing comments.
    """

    def __init__(self, current_comment_type):
        self.__current_type = current_comment_type

    def validate(self, current_text):
        if not bool(_REGEX_EMPTY.match(current_text)):
            return False, _("A type must not be empty")

        if not current_text == self.__current_type and current_text in get_settings().comment_types:
            return False, _("A type with that name already exists")

        if not bool(_REGEX_COMMENT_TYPE.match(current_text)):
            return False, _("Allowed characters are letters, spaces and minus")

        return True, ""
