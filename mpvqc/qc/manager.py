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


from typing import Optional, List

from gi.repository import GObject, GLib

import mpvqc.messagedialogs as md
from mpvqc import get_settings, dialogs
from mpvqc.utils.signals import TABLE_CONTENT_CHANGED, STATUSBAR_UPDATE, QC_STATE_CHANGED


class QcManager(GObject.GObject):
    __gtype_name__ = "QcManager"

    __gsignals__ = {
        STATUSBAR_UPDATE: (GObject.SignalFlags.RUN_FIRST, None, (str, int)),
        QC_STATE_CHANGED: (GObject.SignalFlags.RUN_FIRST, None, (bool,))
    }

    def __init__(self, window, video_widget, table_widget):
        """
        The qc manager will take care of the state of the current video and documents.

        :param window: the application window
        :param video_widget: a reference to the video widget (not the player!)
        :param table_widget: a reference to the table widget
        """

        super(QcManager, self).__init__()

        # Widgets
        self.__a = window
        self.__t = table_widget
        self.__m = video_widget

        # State
        from mpvqc.qc.states import get_initial_state
        self.__state = get_initial_state()
        self.__state_last_saved = None
        self.__during_state_change = False

        self.__t.connect(TABLE_CONTENT_CHANGED, self.on_table_content_modified)

        # Auto save
        self.__auto_save_timer = None
        self.reset_auto_save()

    def on_table_content_modified(self, *_):
        """Called after the table content changed"""

        if not self.__during_state_change:
            # Filling the table during a state change causes this method (event) being fired
            # So we block it to avoid multiple state change events
            self.__before_stage_change()
            self.__state = self.__state.on_comments_modified(self.__t)
            self.__after_state_change()

    def request_new_document(self):
        """Called when the user presses the 'New' button"""

        self.__before_stage_change()
        self.__state = self.__state.on_create_new_document(self.__a, self.__t, self.__m)
        self.__after_state_change()

    def request_open_qc_documents(self, paths: Optional[List[str]] = None):
        """Called when the user presses the 'Open' button and then selects the documents to import"""

        if paths is None:
            paths = dialogs.dialog_open_qc_files(self.__a)

        self.__before_stage_change()
        self.__state = self.__state.on_import(docs=paths, vids=None, subs=None, a=self.__a, t=self.__t, m=self.__m)
        self.__after_state_change()

    def request_open_video(self, vid=None):
        """Called when the user presses the 'Open' button and then selects the videos to import"""

        if vid is None:
            vid = dialogs.dialog_open_video(self.__a)
        vids = [vid] if vid else None

        self.__before_stage_change()
        self.__state = self.__state.on_import(docs=None, vids=vids, subs=None, a=self.__a, t=self.__t, m=self.__m)
        self.__after_state_change()

    def request_open_subtitles(self):
        """Called when the user presses the 'Open' button and then selects the subtitles to import"""

        subs = dialogs.dialog_open_subtitle_files(self.__a)

        self.__before_stage_change()
        self.__state = self.__state.on_import(docs=None, vids=None, subs=subs, a=self.__a, t=self.__t, m=self.__m)
        self.__after_state_change()

    def request_save_qc_document(self):
        """Called when the user presses the 'Save' button"""

        self.__before_stage_change()
        self.__state = self.__state.on_save_pressed(self.__a, self.__t, self.__m)
        self.__after_state_change()

    def request_save_qc_document_as(self):
        """Called when the user presses the 'Save As...' button"""

        self.__before_stage_change()
        self.__state = self.__state.on_save_as_pressed(self.__a, self.__t, self.__m)
        self.__after_state_change()

    def request_quit_application(self):
        """
        Asks the manager whether there are unsaved changes.

        :return: True if quit, False else
        """

        if not self.__state.has_changes:
            return True

        self.__m.player.pause()

        response = md.message_dialog_leave_with_unsaved_qc_document()
        if response == 0:  # Still leave
            return True
        return False

    def do_open_drag_and_drop_data(self, vids, docs, subs):
        """
        Opens the given videos, text documents and subtitle documents.
        If a video is passed in, the passed in video will be preferred over videos found in documents.

        :param vids: a list with paths pointing to video files
        :param docs: a list with paths pointing to qc documents files
        :param subs: a list with paths pointing to subtitles
        """

        self.__before_stage_change()
        self.__state = self.__state.on_import(docs, vids, subs, self.__a, self.__t, self.__m)
        self.__after_state_change()

    def reset_auto_save(self):
        """Sets up/resets auto save timer"""

        def __do_auto_save():
            """Function which triggers auto save"""

            self.__state.on_write_auto_save(self.__a, self.__t, self.__m)
            return True

        if self.__auto_save_timer is not None:
            GLib.source_remove(self.__auto_save_timer)

        s = get_settings()
        if s.auto_save_enabled and s.auto_save_interval >= 15:
            self.__auto_save_timer = GLib.timeout_add(s.auto_save_interval * 1000, __do_auto_save)

    def __before_stage_change(self):
        """Requires to be called before any state change originated from a user action except table changes"""
        self.__during_state_change = True

    def __after_state_change(self):
        """Called after the state has changed"""

        if not self.__state.has_changes:
            self.__state_last_saved = self.__state.copy()
        else:
            matches_last_save = self.__state_last_saved is not None \
                                and self.__state_last_saved.has_same_content_as(self.__state)

            if matches_last_save:
                self.__state = self.__state_last_saved

        s = self.__state

        if s.message:
            self.emit(STATUSBAR_UPDATE, s.message, s.duration.value)

        changes = s.has_changes
        self.emit(QC_STATE_CHANGED, changes)

        self.__during_state_change = False
