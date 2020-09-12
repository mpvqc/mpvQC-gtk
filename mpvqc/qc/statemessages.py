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


from gettext import gettext as _
from os import path
from typing import Optional, List


def get_import_m(documents: Optional[List[str]] = None,
                 video: Optional[str] = None,
                 subtitles: Optional[List[str]] = None) -> str:
    """Returns a localized message to summarize the import in the statusbar"""
    docs, vid, subs = bool(documents), bool(video), bool(subtitles)
    l_docs = 0 if not docs else len(documents)
    l_subs = 0 if not subs else len(subtitles)
    message = ""

    if not docs and not vid and subs:
        if l_subs == 1:
            message = _("Imported subtitle file {}").format(path.basename(subtitles[0]))
        else:
            message = _("Imported {} subtitle files").format(l_subs)
    elif not docs and vid and not subs:
        message = _("Imported video file {}").format(path.basename(video))
    elif not docs and vid and subs:
        if l_subs == 1:
            message = _("Imported a video and a subtitle file")
        else:
            message = _("Imported a video and {} subtitle files").format(l_subs)
    elif docs and not vid and not subs:
        if l_docs == 1:
            message = _("Imported document file {}").format(path.basename(documents[0]))
        else:
            message = _("Imported {} document files").format(l_docs)
    elif docs and not vid and subs:
        if l_docs == 1 and l_subs == 1:
            message = _("Imported a document and a subtitle file")
        elif l_docs == 1 and l_subs > 1:
            message = _("Imported a document and {} subtitle files").format(l_subs)
        elif l_docs > 1 and l_subs == 1:
            message = _("Imported {} documents and a subtitle file").format(l_docs)
        else:
            message = _("Imported {} documents and {} subtitle files").format(l_docs, l_subs)
    elif docs and vid and not subs:
        if l_docs == 1:
            message = _("Imported a video and a document file")
        else:
            message = _("Imported a video and {} document files").format(l_docs)
    elif docs and vid and subs:
        if l_docs == 1 and l_subs == 1:
            message = _("Imported a video, a document and a subtitle file")
        elif l_docs == 1 and l_subs > 1:
            message = _("Imported a video, a document and {} subtitle files").format(l_subs)
        elif l_docs > 1 and l_subs == 1:
            message = _("Imported a video, {} documents and a subtitle file").format(l_docs)
        else:
            message = _("Imported a video, {} documents and {} subtitle files").format(l_docs, l_subs)

    return message


def get_save_m(as_new_name: bool = False):
    if as_new_name:
        return _("Saved document as new file")
    else:
        return _("Saved document")


def get_new_doc_m():
    return _("Created new document")
