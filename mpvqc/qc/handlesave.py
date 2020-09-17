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


from typing import Optional, NamedTuple, Tuple

from mpvqc.qc import Comment, exporter


class HandleSaveResult(NamedTuple):
    abort: bool = False
    doc_new: Optional[str] = None
    vid_new: Optional[str] = None


def do_save(
        doc: Optional[str],
        vid: Optional[str],
        comments: Tuple[Comment]
) -> HandleSaveResult:
    if not doc:
        return HandleSaveResult(abort=True)

    content = exporter.get_file_content(vid, comments)
    exporter.write_qc_document(doc, content)

    return HandleSaveResult(doc_new=doc, vid_new=vid)
