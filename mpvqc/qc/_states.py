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


from abc import abstractmethod, ABC
from typing import Optional, Tuple, List

from gi.repository import Gtk

import mpvqc.dialogs as d
import mpvqc.messagedialogs as md
import mpvqc.qc._handleimport as hi
import mpvqc.qc._handlesave as hs
import mpvqc.qc._statemessages as sm
from mpvqc import get_settings
from mpvqc.qc import Comment, _exporter
from mpvqc.qc._handleimport import HandleImportResultData as Data
from mpvqc.ui.contentmainmpv import ContentMainMpv as MpvContainer
from mpvqc.ui.contentmaintable import ContentMainTable as Table
from mpvqc.ui.window import MpvqcWindow as AppWindow
from mpvqc.utils import StatusbarMessageDuration as Duration


class State(ABC):

    def __init__(
            self,
            has_changes: bool,
            doc: Optional[str] = None,
            vid: Optional[str] = None,
            comments: Optional[Tuple[Comment]] = None,
            message: Optional[str] = None,
            duration: Optional[Duration] = Duration.LONG
    ):
        self.__has_changes = has_changes
        self.__doc: Optional[str] = doc
        self.__vid: Optional[str] = vid
        self.__comments: Optional[Tuple[Comment]] = tuple(comments) if comments else ()
        self.__message: Optional[str] = message or ""
        self.__duration: Optional[Duration] = duration or Duration.LONG

    def has_same_content_as(self, other) -> bool:
        return self.__doc == other.__doc \
               and self.__vid == other.__vid \
               and self.__comments == other.__comments

    @property
    def duration(self) -> Duration:
        return self.__duration

    @property
    def message(self) -> Optional[str]:
        return self.__message

    @property
    def has_changes(self) -> bool:
        return self.__has_changes

    @property
    def _doc(self):
        return self.__doc

    @property
    def _vid(self):
        return self.__vid

    @property
    def _comments(self):
        return self.__comments

    def copy(self) -> 'State':
        """
        Returns a copy with document, video and comments copied. Never copies a message and a message duration
        """

        doc = self.__doc
        vid = self.__vid
        comments = self.__comments

        if isinstance(self, _StateInitial):
            return self._state_initial(vid=vid, comments=comments)
        if isinstance(self, _StateSaved):
            return self._state_saved(doc, vid, comments)
        if isinstance(self, _StateUnsaved):
            return self._state_unsaved(doc, vid, comments)

        raise RuntimeError("State not allowed", self.__class__)

    def copy_with_message(self, message: Optional[str] = "", duration: Optional[Duration] = Duration.LONG) -> 'State':
        """
        Returns a copy with document, video and comments copied
        """

        doc = self.__doc
        vid = self.__vid
        comments = self.__comments

        if isinstance(self, _StateInitial):
            return self._state_initial(vid=vid, comments=comments, message=message, duration=duration)
        if isinstance(self, _StateSaved):
            return self._state_saved(doc, vid, comments, message=message, duration=duration)
        if isinstance(self, _StateUnsaved):
            return self._state_unsaved(doc, vid, comments, message=message, duration=duration)

        raise RuntimeError("State not allowed", self.__class__)

    @staticmethod
    def _state_initial(
            vid: Optional[str],
            comments: Optional[Tuple[Comment]],
            message: Optional[str] = "",
            duration: Optional[Duration] = Duration.LONG
    ) -> 'State':
        """
        Returns an initial state based on the current state.
        """

        return _StateInitial(vid=vid, comments=comments, message=message, duration=duration)

    @staticmethod
    def _state_saved(
            doc: Optional[str],
            vid: Optional[str],
            comments: Optional[Tuple[Comment]],
            message: Optional[str] = "",
            duration: Optional[Duration] = Duration.LONG
    ) -> 'State':
        """
        Returns a saved state based on the current state.
        """

        return _StateSaved(doc=doc, vid=vid, comments=comments, message=message, duration=duration)

    @staticmethod
    def _state_unsaved(
            doc: Optional[str],
            vid: Optional[str],
            comments: Optional[Tuple[Comment]],
            message: Optional[str] = "",
            duration: Optional[Duration] = Duration.LONG
    ) -> 'State':
        """
        Returns an unsaved state based on the current state.
        """

        return _StateUnsaved(doc=doc, vid=vid, comments=comments, message=message, duration=duration)

    def on_comments_modified(self, t: Table) -> 'State':
        """
        Called when the comments table was modified: added row, modified row or deleted row
        """

        return self._state_unsaved(doc=self.__doc, vid=self.__vid, comments=t.get_all_comments())

    def on_create_new_document(self, a: AppWindow, t: Table, _: MpvContainer) -> 'State':
        """
        Called when the user presses the 'New' button
        """

        if self.__has_changes:
            if bool(t.get_all_comments()):
                response = md.message_dialog_unsaved_qc_document_clear_comments(parent=a)
                if response == 0:  # Clear comments
                    pass
                elif response == 1:  # Abort
                    return self.copy()
            else:
                response = md.message_dialog_unsaved_qc_document_proceed(parent=a)
                if response == 0:  # Continue
                    pass
                elif response == 1:  # Abort
                    return self.copy()

        t.clear_all_comments()

        return self._state_initial(vid=self.__vid, comments=self.__comments,
                                   message=sm.get_new_doc_m(), duration=Duration.SHORT)

    def on_save_pressed(self, a: AppWindow, t: Table, m: MpvContainer) -> 'State':
        """
        Called when the user presses the 'Save' button
        """

        if self.__doc is None:
            return self.on_save_as_pressed(a, t, m)

        comments = t.get_all_comments()
        r = hs.do_save(self.__doc, self.__vid, comments)

        if r.save_error:
            md.message_dialog_document_save_failed(parent=a)
            return self.copy()

        return self._state_saved(doc=r.doc_new, vid=r.vid_new, comments=comments,
                                 message=sm.get_save_m(as_new_name=False), duration=Duration.SHORT)

    def on_save_as_pressed(self, a: AppWindow, t: Table, m: MpvContainer) -> 'State':
        """
        Called when the user presses the 'Save As...' button
        """

        m.player.pause()
        doc = d.dialog_save_qc_document(self.__vid, a)
        comments = t.get_all_comments()
        r = hs.do_save(doc, self.__vid, comments)

        if r.abort:
            return self.copy()
        elif r.save_error:
            md.message_dialog_document_save_failed(parent=a)
            return self.copy()

        get_settings().latest_paths_recent_files_add(doc)

        return self._state_saved(doc=r.doc_new, vid=r.vid_new, comments=comments,
                                 message=sm.get_save_m(as_new_name=True))

    def on_write_auto_save(self, _: AppWindow, __: Table, m: MpvContainer) -> None:
        """
        Auto saves the current state
        """

        if m.player.is_video_loaded():
            content = _exporter.get_file_content(self.__vid, self.__comments or [])
            _exporter.write_auto_save(video_path=self.__vid, file_content=content)

    def on_import(
            self,
            docs: Optional[List[str]],
            vids: Optional[List[str]],
            subs: Optional[List[str]],
            a: AppWindow,
            t: Table,
            m: MpvContainer
    ) -> 'State':
        """
        Called when the user imports something
        (no matter if it's by d&d or just by selecting something in the file manager).
        """

        if not docs and not vids and not subs:
            return self.copy()

        s = get_settings()

        def _handle_docs_valid(valid_docs: List[str]) -> None:
            for vd in valid_docs:
                s.latest_paths_recent_files_add(vd)

        def _handle_docs_invalid(invalid_docs: List[str]) -> None:
            if invalid_docs:
                md.message_dialog_imported_files_are_not_valid(not_valid_files=invalid_docs, parent=a)

        def _handle_comments(comments: Tuple[Comment]) -> bool:
            """
            Returns True if abort import, False else
            """

            if t.get_all_comments():
                response = md.message_dialog_what_to_do_with_existing_comments()
                if response == 0:  # Keep comments
                    pass
                elif response == 1:  # Delete comments
                    t.clear_all_comments()
                elif response == 2:
                    return True

            t.add_comments(comments)
            return False

        def _handle_vids(vid: str) -> bool:
            """
            Returns True, if video actually was opened
            """

            do_open = vid and (s.import_open_video_automatically
                               or Gtk.ResponseType.YES == md.message_dialog_video_found_ask_to_open(file=vid, parent=a))
            if do_open:
                __open_video(vid)
                return True
            return False

        def __open_video(vid: str) -> None:
            m.player.open_video(vid)
            s.latest_paths_recent_files_add(vid)

        hir, data = hi.do_import(self.__vid, docs, vids)
        vid_new = hir.vid_new

        if docs:
            abort_import = _handle_comments(hir.comments)
            if abort_import:
                return self.copy()

            _handle_docs_valid(hir.docs_valid)
            _handle_docs_invalid(hir.docs_invalid)

            if not vids and vid_new:
                opened = _handle_vids(vid_new)
                if not opened:
                    vid_new = None
                    data.vid_new = None

            if not vids and not subs and not hir.docs_valid:
                return self.copy()

        if vids:
            __open_video(vid_new)

        if subs:
            for sub in subs:
                m.player.add_sub_files(sub)

        return self.__on_import_handle_state(data=data, imp_docs=hir.docs_valid, imp_vid=vid_new, imp_subs=subs)

    def __on_import_handle_state(
            self,
            data: Data,
            imp_docs: Optional[List[str]],
            imp_vid: Optional[str],
            imp_subs: Optional[List[str]]
    ) -> 'State':
        """
        Delegates the import to the specific methods based on what was imported
        """

        docs, vid, subs = bool(imp_docs), bool(imp_vid), bool(imp_subs)
        message = sm.get_import_m(imp_docs, imp_vid, imp_subs)

        # One of: doc, vid or subs
        if docs and not vid and not subs:
            return self.on_import_docs(message, imp_docs, data)
        elif not docs and vid and not subs:
            return self.on_import_vid(message, imp_vid, data)
        elif not docs and not vid and subs:
            return self.on_import_subs(message, imp_subs, data)

        # Two of: doc, vid or subs
        elif docs and vid and not subs:
            return self.on_import_docs_vid(message, imp_docs, imp_vid, data)
        elif docs and not vid and subs:
            return self.on_import_docs_subs(message, imp_docs, imp_subs, data)
        elif not docs and vid and subs:
            return self.on_import_vid_subs(message, imp_vid, imp_subs, data)

        # All three: doc, vid, subs
        return self.on_import_docs_vids_subs(message, imp_docs, imp_vid, imp_subs, data)

    @abstractmethod
    def on_import_docs(self, message: str, docs: List[str], data: Data) -> 'State':
        """Called when only documents were imported and possibly linked videos were not imported"""
        pass

    @abstractmethod
    def on_import_vid(self, message: str, video: str, data: Data) -> 'State':
        """Called when only a video was imported"""
        pass

    @abstractmethod
    def on_import_subs(self, message: str, subtitles: List[str], data: Data) -> 'State':
        """Called when only subtitles were imported"""
        pass

    @abstractmethod
    def on_import_docs_vid(self, message: str, docs: List[str], video: str, data: Data) -> 'State':
        """
        Called when either only documents were imported and the linked video was imported
        or when documents and a video was opened via drag and drop.
        """
        pass

    @abstractmethod
    def on_import_docs_subs(self, message: str, docs: List[str], subs: List[str], data: Data) -> 'State':
        """
        Called when only documents were imported and possibly linked videos were not imported
        and when subtitles were imported, too.
        """
        pass

    @abstractmethod
    def on_import_vid_subs(self, message: str, video: str, subtitles: List[str], data: Data) -> 'State':
        """Called when videos and subtitles were imported by drag and drop"""
        pass

    @abstractmethod
    def on_import_docs_vids_subs(self, message: str, docs: List[str], vid: str, subs: List[str], data: Data) -> 'State':
        """
        Called when all three were imported via drag and drop
        or when documents were imported as well as their linked video and subtitles as well.
        """
        pass


class __StateSubtitleImportDelegate(State, ABC):
    """
    Currently importing subtitles does not change the state.
    So we delegate these methods to the ones without subtitles.
    """

    def on_import_subs(self, message: str, __: List[str], ___: hi.HandleImportResultData) -> 'State':
        return self.copy_with_message(message=message)

    def on_import_docs_subs(self, message: str, docs: List[str], _: List[str], data: Data) -> 'State':
        return self.on_import_docs(message, docs, data)

    def on_import_vid_subs(self, message: str, video: str, _: List[str], data: Data) -> 'State':
        return self.on_import_vid(message, video, data)

    def on_import_docs_vids_subs(self, message: str, docs: List[str], vid: str, _: List[str], data: Data) -> 'State':
        return self.on_import_docs_vid(message, docs, vid, data)


class _StateInitial(__StateSubtitleImportDelegate):

    def __init__(
            self,
            doc: Optional[str] = None,
            vid: Optional[str] = None,
            comments: Optional[Tuple[Comment]] = None,
            message: Optional[str] = None,
            duration: Optional[Duration] = Duration.LONG
    ):
        super().__init__(False, doc, vid, comments, message, duration)

    def on_import_docs(self, message: str, docs: List[str], data: Data) -> 'State':
        if len(docs) == 1:
            return self._state_saved(doc=data.doc_new, vid=self._vid, comments=data.comments, message=message)
        return self._state_unsaved(doc=None, vid=self._vid, comments=data.comments, message=message)

    def on_import_vid(self, message: str, video: str, data: Data) -> 'State':
        if data.is_cur_vid_is_imported_vid:
            return self.copy()
        return self._state_initial(vid=video, comments=data.comments, message=message)

    def on_import_docs_vid(self, message: str, docs: List[str], video: str, data: Data) -> 'State':
        if len(docs) == 1:
            # If video was linked in the document
            vid_linked_in_doc = data.is_new_vid_from_doc
            # If video was linked in the document and imported separately and both match
            vid_linked_in_doc_equals_vid_separately = data.is_vid_from_docs_equals_vid_from_user

            if vid_linked_in_doc or vid_linked_in_doc_equals_vid_separately:
                return self._state_saved(doc=data.doc_new, vid=video, comments=data.comments, message=message)
        return self._state_unsaved(doc=None, vid=video, comments=data.comments, message=message)


# noinspection DuplicatedCode
class _StateSaved(__StateSubtitleImportDelegate):

    def __init__(
            self,
            doc: Optional[str] = None,
            vid: Optional[str] = None,
            comments: Optional[Tuple[Comment]] = None,
            message: Optional[str] = None,
            duration: Optional[Duration] = Duration.LONG
    ):
        super().__init__(False, doc, vid, comments, message, duration)

    def on_import_docs(self, message: str, docs: List[str], data: Data) -> 'State':
        return self._state_unsaved(doc=None, vid=self._vid, comments=data.comments, message=message)

    def on_import_vid(self, message: str, video: str, data: Data) -> 'State':
        if data.is_cur_vid_is_imported_vid:
            return self.copy()
        return self._state_unsaved(doc=None, vid=video, comments=data.comments, message=message)

    def on_import_docs_vid(self, message: str, docs: List[str], video: str, data: Data) -> 'State':
        return self._state_unsaved(doc=None, vid=video, comments=data.comments, message=message)


# noinspection DuplicatedCode
class _StateUnsaved(__StateSubtitleImportDelegate):

    def __init__(
            self,
            doc: Optional[str] = None,
            vid: Optional[str] = None,
            comments: Optional[Tuple[Comment]] = None,
            message: Optional[str] = None,
            duration: Optional[Duration] = Duration.LONG
    ):
        super().__init__(True, doc, vid, comments, message, duration)

    def on_import_docs(self, message: str, docs: List[str], data: Data) -> 'State':
        return self._state_unsaved(doc=None, vid=self._vid, comments=data.comments, message=message)

    def on_import_vid(self, message: str, video: str, data: Data) -> 'State':
        if data.is_cur_vid_is_imported_vid:
            return self.copy()
        return self._state_unsaved(doc=None, vid=video, comments=data.comments, message=message)

    def on_import_docs_vid(self, message: str, docs: List[str], video: str, data: Data) -> 'State':
        return self._state_unsaved(doc=None, vid=video, comments=data.comments, message=message)


def get_initial_state() -> State:
    return _StateInitial()
