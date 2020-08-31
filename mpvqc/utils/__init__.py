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
from enum import Enum

from gi.repository import Gtk, GLib

formatted_string_pattern = re.compile(r"\d{2}:\d{2}:\d{2}")

# A dictionary of "query" -> pattern
_CACHED_PATTERNS = {}


def seconds_float_to_formatted_string_hours(seconds: float, short=True) -> str:
    """
    Transforms the seconds into a string of the following format **hh:mm:ss**.

    :param short: If True "mm:ss" will be returned, else "HH:mm:ss"
    :param seconds: The seconds to transform
    :return: string representing the time
    """

    m, s = divmod(int(seconds), 60)
    h, m = divmod(m, 60)
    h = "{:02d}:".format(h) if h else ("" if short else "00:")

    return "{}{:02d}:{:02d}".format(h, m, s)


def formatted_string_to_int(formatted_string):
    """
    Converts a valid formatted time string into the amount of seconds.

    :param formatted_string: A string matching pattern "\d{2}:\d{2}:\d{2}"
    :return: the amount of seconds
    """

    if not formatted_string_pattern.match(formatted_string):
        raise ValueError(formatted_string + " does match required pattern")
    split = formatted_string.split(":")
    return int(split[0]) * 60 * 60 + int(split[1]) * 60 + int(split[2])


def get_longest_string_from(model, column=0):
    """
    Returns the longest string (string with the most characters) of the given model.

    :param model: a model to extract the longest string
    :param column: the column to look into (as int type)
    :return: the longest string from the given model
    """

    items = []
    iterator = model.get_iter_first()
    while iterator:
        items.append(model.get_value(iterator, column))
        iterator = model.iter_next(iterator)
    return max(items, key=len)


def list_header_func(row, before, user_data):
    """
    Used to draw separators in a list widget by setting the function listbox.set_header_func(list_header_func, None)

    :param row: data from event
    :param before: data from event
    :param user_data: data from event
    """

    if before and not row.get_header():
        row.set_header(Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL))


def list_header_nested_func(row, before, user_data):
    """
    Used to draw separators in a list widget by setting the function listbox.set_header_func(list_header_func, None).
    This function is usefully only for nested lists.

    :param row: data from event
    :param before: data from event
    :param user_data: data from event
    """

    row.set_header(Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL))


class StatusbarMessageDuration(Enum):
    """
    Duration how long messages remain visible.
    """

    SHORT = 2500
    LONG = 5000


def replace_special_characters(string_to_replace):
    """
    Removes forbidden characters in a string.

    :param string_to_replace: the original string
    :return: the modified string
    """

    return string_to_replace \
        .replace(u'\xad', '')  # https://www.charbase.com/00ad-unicode-soft-hyphen


def validate_text_insertion(editable, new_inserted_text, *data):
    """
    Validate inserted text and removes forbidden characters.
    """

    pos = editable.get_position()

    new_txt = replace_special_characters(new_inserted_text)
    new_pos = pos + len(new_txt)

    if new_txt != new_inserted_text:
        editable.handler_block_by_func(validate_text_insertion)
        editable.insert_text(new_txt, pos)
        editable.handler_unblock_by_func(validate_text_insertion)

        GLib.timeout_add(0, editable.set_position, new_pos)

        editable.stop_emission("insert-text")

    return new_pos


def get_pattern(query):
    """
    Returns a case insensitive pattern of query.
    """

    pattern_q = _CACHED_PATTERNS.get(query, None)
    if pattern_q is None:
        pattern_q = re.compile(r"({})".format(re.escape(query)), re.IGNORECASE)
        _CACHED_PATTERNS.update({query: pattern_q})
    return pattern_q


def get_markup(current_text, query, highlight_prefix, highlight_suffix):
    """
    Returns the current text as markup highlighting all query occurrences case insensitive.
    Highlighting must be set by highlight_prefix and highlight_suffix.

    * highlight_prefix = '<b>' and highlight_suffix = '</b>' will return a markup with query substrings set to bold.

    :param query: the query to highlight
    :param current_text: the current text
    :param highlight_prefix: specify what to insert before query
    :param highlight_suffix: specify what to insert after query
    :return: markup with all query occurrences highlighted specified by highlight_prefix and highlight_suffix
    """

    return get_pattern(query=query).subn(r"{}\1{}".format(highlight_prefix, highlight_suffix), current_text)
