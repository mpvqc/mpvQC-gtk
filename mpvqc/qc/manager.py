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

from gi.repository import Gtk, GObject, GLib

from mpvqc import dialogs, get_settings
from mpvqc.messagedialogs import message_dialog_imported_files_are_not_valid, message_dialog_video_found_ask_to_open, \
    message_dialog_what_to_do_with_existing_comments, message_dialog_clear_unsaved_qc_document, \
    message_dialog_leave_with_unsaved_qc_document
from mpvqc.qc import exporter, importer
from mpvqc.utils import StatusbarMessageDuration
from mpvqc.utils.signals import TABLE_CONTENT_CHANGED, STATUSBAR_UPDATE, QC_STATE_CHANGED


class QcManager(GObject.GObject):
    __gtype_name__ = "QcManager"

    # todo rewrite this big mess

    __gsignals__ = {
        STATUSBAR_UPDATE: (GObject.SignalFlags.RUN_FIRST, None, (str, int)),
        QC_STATE_CHANGED: (GObject.SignalFlags.RUN_FIRST, None, (bool,))
    }

    def __init__(self, application, video_widget, table_widget):
        """
        The qc manager will take care of the state of the current video and qc documents.

        :param application: the application
        :param video_widget: a reference to the video widget (not the player!)
        :param table_widget: a reference to the table widget
        """

        super(QcManager, self).__init__()

        # Widgets
        self.__application = application
        self.__video_widget = video_widget
        self.__table_widget = table_widget

        # State
        self.__latest_saved_comments = self.__table_widget.get_all_comments()
        self.__up_to_date = True

        self.__table_widget.connect(TABLE_CONTENT_CHANGED, self.__update_qc_state)

        # The name of the current loaded video file (no path and without extension)
        self.__current_video_file = None

        # The path of the current loaded video file (with extension)
        self.__current_video_path = None

        # The path of the current qc file
        self.__current_qc_document_path = None

        # Auto save
        self.__auto_save_timer = None
        self.reset_auto_save()

    def request_new_document(self):
        """
        Invokes the corresponding action while also taking into account the current qc state.
        """

        if not self.__up_to_date and self.__table_widget.get_all_comments():
            response = message_dialog_clear_unsaved_qc_document()
            if response == 0:  # Delete existing comments
                self.__do_new_qc_document()
                self.__status_update_new_document()
            elif response == 1:  # Abort
                pass
        else:
            self.__do_new_qc_document()
            self.__status_update_new_document()

    def request_open_video(self, video_path=None):
        """
        Invokes the corresponding action while also taking into account the current qc state.

        :return: True if a video was actually loaded, False else
        """

        if video_path is None:
            video_path = dialogs.dialog_open_video(self.__application)

        if video_path:
            self.__do_open_video(video_path)
            if self.__video_widget.player.is_video_loaded():
                self.__status_update_open_video(video_path)

        return self.__video_widget.player.is_video_loaded()

    def request_open_subtitles(self):
        """
        Invokes the corresponding action while also taking into account the current qc state.

        :return: True if a video was actually loaded, False else
        """

        subtitles = dialogs.dialog_open_subtitle_files(self.__application)
        if subtitles:
            self.__do_open_subtitle_files(subtitles)
            self.__status_update_open_subtitles(subtitles)

    def request_open_qc_documents(self, qc_documents=None):
        """
        Invokes the corresponding action while also taking into account the current qc state.
        """

        if qc_documents is None:
            qc_documents = dialogs.dialog_open_qc_files(self.__application)

        if qc_documents:
            self.__do_open_qc_documents(qc_documents)
            self.__status_update_open_qc_documents(qc_documents)

    def request_save_qc_document(self):
        """
        Invokes the corresponding action while also taking into account the current qc state.
        """

        if self.__current_qc_document_path:
            self.__do_save_qc_document(self.__current_qc_document_path)
            self.__status_update_save_qc_document()
        else:
            self.request_save_qc_document_as()

    def request_save_qc_document_as(self):
        """
        Invokes the corresponding action while also taking into account the current qc state.
        """

        self.__video_widget.player.pause()

        file_path = dialogs.dialog_save_qc_document(self.__current_video_file, parent=self.__application)
        if file_path:
            self.__do_save_qc_document(file_path)
            self.__status_update_save_qc_document_as()

    def request_quit_application(self):
        """
        Asks the manager whether there are unsaved changes.

        :return: True if quit, False else
        """

        if self.__up_to_date:
            return True

        self.__video_widget.player.pause()

        response = message_dialog_leave_with_unsaved_qc_document()
        if response == 0:  # Still leave
            return True
        return False

    def do_open_drag_and_drop_data(self, videos, qc_documents, subtitle_documents):
        """
        Opens the given videos, text documents and subtitle documents.
        If a video is passed in, the passed in video will be preferred over videos found in qc documents.

        :param videos: a list with paths pointing to video files
        :param qc_documents: a list with paths pointing to qc documents files
        :param subtitle_documents: a list with paths pointing to subtitles
        """

        videos_found = bool(videos)

        if videos_found:
            self.__do_open_video(videos[0])

        if subtitle_documents:
            self.__do_open_subtitle_files(subtitle_documents)

        if qc_documents:
            self.__do_open_qc_documents(qc_documents, ask_to_open_videos=not videos_found)

        self.__status_update_open_drag_and_drop_data(videos, qc_documents, subtitle_documents)

    def reset_auto_save(self):
        """
        Sets up/resets auto save timer.
        """

        def __do_auto_save():
            """
            Function which triggers auto save.
            """

            if self.__video_widget.player.is_video_loaded():
                comments = self.__table_widget.get_all_comments()
                content = exporter.get_file_content(self.__current_video_path, comments)

                exporter.write_auto_save(video_file=self.__current_video_file, file_content=content)

            return True

        if self.__auto_save_timer is not None:
            GLib.source_remove(self.__auto_save_timer)

        s = get_settings()
        if s.auto_save_enabled and s.auto_save_interval >= 15:
            self.__auto_save_timer = GLib.timeout_add(s.auto_save_interval * 1000, __do_auto_save)

    def __do_new_qc_document(self):
        """
        Clears the comment table and resets the qc document state.
        """

        self.__table_widget.clear_all_comments()

        self.__current_qc_document_path = None
        self.__latest_saved_comments = self.__table_widget.get_all_comments()
        self.__update_qc_state()

    def __do_save_qc_document(self, document_path):
        """
        Saves the current qc document to disk.

        :param document_path: the document path to write to
        """

        # Write qc document to disk
        comments = self.__table_widget.get_all_comments()
        content = exporter.get_file_content(self.__current_video_path, comments)
        exporter.write_qc_document(document_path, content)

        # Add to recent files
        get_settings().latest_paths_recent_files_add(document_path)

        # Update document state and emit signal
        self.__current_qc_document_path = document_path
        self.__latest_saved_comments = comments
        self.__update_qc_state()

    def __do_open_video(self, video_path):
        """
        Opens the video using the given path.

        :param video_path: the path of a video to open
        """

        # Update video file state
        self.__current_video_path = video_path
        self.__current_video_file = path.splitext(path.basename(video_path))[0]

        # Open video file
        self.__video_widget.player.open_video(video_path, play=True)

        # Add video file to recent files
        get_settings().latest_paths_recent_files_add(video_path)

    def __do_open_subtitle_files(self, subtitles):
        """
        Opens all subtitles and adds them to the current video.

        :param subtitles: a list of subtitles (files must be present on disc)
        """

        for s in subtitles:
            self.__video_widget.player.add_sub_files(s)

    def __do_open_qc_documents(self, qc_documents, ask_to_open_videos=True):
        """
        Considers currently opened documents, comments and found videos. Asks the user how to proceed when needed.

        :param qc_documents: a list with paths pointing to existing qc document files
        :param ask_to_open_videos: If True and valid video was found, the user needs to confirm to open a video
            If False the video if found will not opened at all unless the user has adjusted it in the settings
        """

        video_paths, combined_comments, valid_files, not_valid_files = importer.get_qc_content(qc_documents)

        if not self.__do_open_qc_documents___handle_existing_comments():
            return

        self.__table_widget.add_comments(combined_comments)
        self.__latest_saved_comments = self.__table_widget.get_all_comments()
        self.__update_qc_state()

        if valid_files:
            self.__do_open_qc_documents___handle_found_video(video_paths, ask_to_open_videos)
            self.__do_open_qc_documents___handle_non_valid_files(not_valid_files)

            if not self.__current_qc_document_path and len(valid_files) == 1:
                self.__current_qc_document_path = valid_files[0]
            else:
                self.__current_qc_document_path = None

            for valid_file in valid_files:
                get_settings().latest_paths_recent_files_add(valid_file)
        else:
            self.__do_open_qc_documents___handle_non_valid_files(not_valid_files)

    def __do_open_qc_documents___handle_existing_comments(self):
        """
        Helper function. Used in the handling of opening new qc documents.

        :return: True if user wants to proceed opening files, False else
        """

        if bool(self.__table_widget.get_all_comments()):
            response = message_dialog_what_to_do_with_existing_comments()
            if response == 0:  # keep comments
                pass
            elif response == 1:  # delete existing comments
                self.__table_widget.clear_all_comments()
            elif response == 2:  # abort import
                return False
        return True

    def __do_open_qc_documents___handle_found_video(self, video_paths, ask_to_open_videos):
        """
        Helper function. Used in the handling of opening new qc documents.

        :param video_paths: valid video paths of currently existing video files found in imported qc documents
        :param ask_to_open_videos: If True and valid video was found, the user needs to confirm to open a video
            If False the video if found will not opened at all
        """

        opened = False

        new_v_path = video_paths[0] if video_paths else None
        if ask_to_open_videos and new_v_path and get_settings().import_open_video_automatically:
            self.__do_open_video(new_v_path)
            opened = True
        elif ask_to_open_videos and new_v_path:
            response = message_dialog_video_found_ask_to_open(file=new_v_path, parent=self.__application)
            if Gtk.ResponseType.YES == response:
                self.__do_open_video(new_v_path)
                opened = True

        if opened:
            self.__status_update_open_video(new_v_path)

    def __do_open_qc_documents___handle_non_valid_files(self, not_valid_files):
        """
        Helper function. Used in the handling of opening new qc documents.

        :param not_valid_files: all files which are considered not valid while importing
        """

        if not_valid_files:
            message_dialog_imported_files_are_not_valid(not_valid_files=not_valid_files, parent=self.__application)

    def __update_statusbar(self, message, duration=StatusbarMessageDuration.SHORT):
        """
        Emits a status bar update action updating the current status bar message.

        :param message: the message to display
        :param duration: the duration to keep the message visible
        """

        self.emit(STATUSBAR_UPDATE, message, duration.value)

    def __status_update_new_document(self):
        """
        Updates the message in the status bar.
        """

        self.__update_statusbar(_("Created new document"))

    def __status_update_open_video(self, video_path):
        """
        Updates the message in the status bar.

        :param video_path: the new video path
        """

        self.__update_statusbar(_("Imported video file {}").format(path.basename(video_path)),
                                StatusbarMessageDuration.LONG)

    def __status_update_open_subtitles(self, subtitles):
        """
        Updates the message in the status bar.

        :param subtitles: a list of subtitle file paths
        """

        if len(subtitles) == 1:
            message = _("Imported subtitle file {}").format(path.basename(subtitles[0]))
        else:
            message = _("Imported {} subtitle files").format(len(subtitles))

        self.__update_statusbar(message, StatusbarMessageDuration.LONG)

    def __status_update_open_qc_documents(self, qc_documents):
        """
        Updates the message in the status bar.

        :param qc_documents: a list of qc document file paths
        """

        if len(qc_documents) == 1:
            message = _("Imported document file {}").format(path.basename(qc_documents[0]))
        else:
            message = _("Imported {} document files").format(len(qc_documents))

        self.__update_statusbar(message, StatusbarMessageDuration.LONG)

    def __status_update_save_qc_document(self):
        """
        Updates the message in the status bar.
        """

        self.__update_statusbar(_("Saved document"))

    def __status_update_save_qc_document_as(self):
        """
        Updates the message in the status bar.
        """

        self.__update_statusbar(_("Saved document as new file"), StatusbarMessageDuration.LONG)

    def __status_update_open_drag_and_drop_data(self, videos, qc_documents, subtitle_documents):
        """
        Updates the message in the status bar.

        :param videos: a list of video file paths
        :param qc_documents: a list of qc document file paths
        :param subtitle_documents: a list of subtitle file paths
        """

        sub_documents_count = len(subtitle_documents)
        qc_documents_count = len(qc_documents)
        message = None

        if not videos and not qc_documents and subtitle_documents and self.__current_video_path:
            self.__status_update_open_subtitles(subtitle_documents)
        elif not videos and qc_documents and not subtitle_documents:
            self.__status_update_open_qc_documents(qc_documents)
        elif not videos and qc_documents and subtitle_documents:
            if self.__current_video_path:
                if qc_documents_count == 1 and sub_documents_count == 1:
                    message = _("Imported a document and a subtitle file")
                elif qc_documents_count == 1 and sub_documents_count > 1:
                    message = _("Imported a document and {} subtitle files").format(sub_documents_count)
                elif qc_documents_count > 1 and sub_documents_count == 1:
                    message = _("Imported {} documents and a subtitle file").format(qc_documents_count)
                else:
                    message = _("Imported {} documents and {} subtitle files") \
                        .format(qc_documents_count, sub_documents_count)
            else:
                self.__status_update_open_qc_documents(qc_documents)
        elif videos and not qc_documents and not subtitle_documents:
            self.__status_update_open_video(videos[0])
        elif videos and not qc_documents and subtitle_documents:
            if sub_documents_count == 1:
                message = _("Imported a video and a subtitle file")
            else:
                message = _("Imported a video and {} subtitle files").format(sub_documents_count)
        elif videos and qc_documents and not subtitle_documents:
            if qc_documents_count == 1:
                message = _("Imported a video and a document file")
            else:
                message = _("Imported a video and {} document files").format(qc_documents_count)
        elif videos and qc_documents and subtitle_documents:
            if qc_documents_count == 1 and sub_documents_count == 1:
                message = _("Imported a video, a document and a subtitle file")
            elif qc_documents_count == 1 and sub_documents_count > 1:
                message = _("Imported a video, a document and {} subtitle files").format(
                    sub_documents_count)
            elif qc_documents_count > 1 and sub_documents_count == 1:
                message = _("Imported a video, {} documents and a subtitle file").format(qc_documents_count)
            else:
                message = _("Imported a video, {} documents and {} subtitle files") \
                    .format(qc_documents_count, sub_documents_count)

        if message:
            self.__update_statusbar(message, StatusbarMessageDuration.LONG)

    def __update_qc_state(self, *data):
        """
        Updates the current qc state considering the latest saved state.
        Emits a signals.QC_STATE_CHANGED signal.

        It is important to set the `self.__latest_saved_comments` only using `self.__table_widget.get_all_comments()`.

        :param data: data passed in by event
        """

        self.__up_to_date = self.__latest_saved_comments == self.__table_widget.get_all_comments()
        self.emit(QC_STATE_CHANGED, self.__up_to_date)
