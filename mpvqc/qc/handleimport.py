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


from typing import NamedTuple, Optional, List, Tuple

from mpvqc.qc import Comment, importer


class HandleImportResult(NamedTuple):
    doc_new: Optional[str] = None
    vid_new: Optional[str] = None
    comments: Optional[Tuple[Comment]] = None
    docs_valid: Optional[List[str]] = None
    docs_invalid: Optional[List[str]] = None


class HandleImportResultData:

    # todo: Replace with dataclass on Python 3.7+

    def __init__(
            self,
            cur_vid_is_imported_vid: bool = False,
            doc_new: Optional[str] = None,
            vid_new: Optional[str] = None,
            comments: Optional[Tuple[Comment]] = None
    ):
        self.cur_vid_is_imported_vid = cur_vid_is_imported_vid
        self.doc_new = doc_new
        self.vid_new = vid_new
        self.comments = comments


def do_import(
        cur_vid: Optional[str],
        imp_docs: Optional[List[str]],
        imp_vids: Optional[List[str]],
) -> Tuple[HandleImportResult, HandleImportResultData]:
    doc_new: Optional[str] = None
    vid_new: Optional[str] = None
    comments: Optional[Tuple[Comment]] = None
    docs_valid: Optional[List[str]] = None
    docs_invalid: Optional[List[str]] = None

    if imp_docs:
        videos, comments, docs_valid, docs_invalid = importer.get_qc_content(imp_docs)
        doc_new = docs_valid[0] if len(imp_docs) == len(docs_valid) == 1 else None
        if not imp_vids and videos:
            vid_new = videos[0]

    if imp_vids:
        vid_new = imp_vids[0]

    hir = HandleImportResult(
        doc_new=doc_new,
        vid_new=vid_new,
        comments=comments,
        docs_valid=docs_valid,
        docs_invalid=docs_invalid
    )

    data = HandleImportResultData(
        cur_vid_is_imported_vid=vid_new and cur_vid and vid_new == cur_vid,
        comments=comments,
        doc_new=doc_new,
        vid_new=vid_new
    )

    return hir, data
