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


from os import path
from sys import getfilesystemencoding
from urllib.parse import unquote

from gi.repository import Gio

# Supported subtitle file extensions for drag and drop and for opening via dialog
SUPPORTED_SUB_FILES = (".ass", ".ssa", ".srt", ".sup", ".idx", ".utf", ".utf8", ".utf-8", ".smi",
                       ".rt", ".aqt", ".jss", ".js", ".mks", ".vtt", ".sub", ".scc")


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

    fs_enc = getfilesystemencoding()
    uris = data.get_data().decode(fs_enc).split()

    files = [unquote(x) for x in uris if x]

    videos, qc_documents, subtitle_documents = [], [], []
    for f in files:
        file = f.replace("file://", "")

        if is_qc_document(file):
            qc_documents.append(file)
        elif is_video_file(file):
            videos.append(file)
        elif is_subtitle_file(file):
            subtitle_documents.append(file)

    return videos, qc_documents, subtitle_documents


def is_qc_document(file_path):
    return path.splitext(file_path)[-1] == ".txt"


def is_video_file(file_path):
    return Gio.content_type_guess(file_path, data=None)[0].startswith("video")


def is_subtitle_file(file_path):
    return path.splitext(file_path)[-1] in SUPPORTED_SUB_FILES
