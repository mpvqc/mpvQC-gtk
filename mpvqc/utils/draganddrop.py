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


import platform
import urllib.parse
from os import path
from sys import getfilesystemencoding

from gi.repository import Gio

# Supported subtitle file extensions for drag and drop and for opening via dialog
SUPPORTED_SUB_FILES = (".ass", ".ssa", ".srt", ".sup", ".idx", ".utf", ".utf8", ".utf-8", ".smi",
                       ".rt", ".aqt", ".jss", ".js", ".mks", ".vtt", ".sub", ".scc")


def __uris_to_path(uri: str) -> str:
    """Transforms a uri to a valid path"""
    file = urllib.parse.urlparse(uri).path
    file = urllib.parse.unquote_plus(file)
    if platform.system() == "Windows":
        # /C:/blub/blub.mp4
        return file[1:]
    else:
        return file


def parse_dropped_data(data):
    """
    Parses the data from a "drag-data-received" event.
    Uses mime type and extensions to determine which type of data was dropped.

    :param data: the data from a "drag-data-received" event
    :return: three lists:<br>
        - videos: dropped videos<br>
        - text_documents: dropped qcs<br>
        - subtitle_documents: dropped subtitle_documents
    """

    videos, qc_documents, subtitle_documents = [], [], []

    fs_enc = getfilesystemencoding()
    uris = data.get_data().decode(fs_enc).split()

    for uri in uris:
        file = __uris_to_path(uri)

        if is_qc_document(file):
            qc_documents.append(file)
        elif is_subtitle_file(file):
            subtitle_documents.append(file)
        elif is_video_file(file):
            videos.append(file)

    return videos, qc_documents, subtitle_documents


def is_qc_document(file_path):
    return path.splitext(file_path)[-1] == ".txt"


def is_video_file(file_path):
    if platform.system() == "Linux":
        # Mime types are not supported on Windows, so we only filter on Linux
        return Gio.content_type_guess(file_path, data=None)[0].startswith("video")
    # Don't filter on Windows
    return True


def is_subtitle_file(file_path):
    return path.splitext(file_path)[-1] in SUPPORTED_SUB_FILES
