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
from gettext import gettext as _
from os import path

from gi.repository import Gtk

from mpvqc import get_settings
from mpvqc.utils.draganddrop import SUPPORTED_SUB_FILES


class _FileFilters:

    @staticmethod
    def __filter_documents() -> Gtk.FileFilter:
        f = Gtk.FileFilter()
        f.set_name(_("Documents"))
        f.add_pattern("*.txt")
        return f

    @staticmethod
    def __filter_video() -> Gtk.FileFilter:
        f = Gtk.FileFilter()
        f.set_name(_("Videos"))
        if platform.system() == "Linux":
            # Mime types are not supported by the native file manager on Windows, so we only filter on Linux
            f.add_mime_type("video/*")
        return f

    @staticmethod
    def __filter_subtitles() -> Gtk.FileFilter:
        f = Gtk.FileFilter()
        f.set_name(_("Subtitles"))
        for ext in SUPPORTED_SUB_FILES:
            f.add_pattern("*{}".format(ext))
        return f

    def __init__(self):
        self.filter_docs = self.__filter_documents()
        self.filter_vids = self.__filter_video()
        self.filter_subs = self.__filter_subtitles()


_FILE_FILTERS = _FileFilters()


def generate_file_name_proposal(video_file):
    nick = "_" + get_settings().export_qc_document_nick if get_settings().export_append_nick else ""
    video = video_file if video_file else _("untitled")
    return "[QC]_{0}{1}.txt".format(video, nick)


def dialog_open_video(parent=None):
    """
    Dialog which is used to choose a video file.

    :param parent: the parent widget
    :return: the chosen video or None if user aborts
    """

    dialog = Gtk.FileChooserNative.new(title=_("Choose a video file"),
                                       parent=parent,
                                       action=Gtk.FileChooserAction.OPEN)
    dialog.add_filter(_FILE_FILTERS.filter_vids)
    dialog.set_select_multiple(False)

    latest_directory = get_settings().latest_paths_import_video_directory
    if path.isdir(latest_directory):
        dialog.set_current_folder(latest_directory)

    video = None
    if dialog.run() == Gtk.ResponseType.ACCEPT:
        video = dialog.get_filename()

        get_settings().latest_paths_import_video_directory = str(path.dirname(video))

    dialog.destroy()
    return video


def dialog_open_subtitle_files(parent=None):
    """
    Dialog which is used to choose multiple subtitle files.

    :param parent: the parent widget
    :return: the qc document paths or None if user aborts
    """

    dialog = Gtk.FileChooserNative.new(title=_("Choose subtitle files"),
                                       parent=parent,
                                       action=Gtk.FileChooserAction.OPEN)
    dialog.add_filter(_FILE_FILTERS.filter_subs)
    dialog.set_select_multiple(True)

    latest_directory = get_settings().latest_paths_import_subtitle_directory
    if path.isdir(latest_directory):
        dialog.set_current_folder(latest_directory)

    subtitles = None
    if dialog.run() == Gtk.ResponseType.ACCEPT:
        subtitles = dialog.get_filenames()

        if subtitles:
            get_settings().latest_paths_import_subtitle_directory = str(path.dirname(subtitles[0]))

    dialog.destroy()
    return subtitles


def dialog_open_qc_files(parent=None):
    """
    Dialog which is used to choose multiple qc files.

    :param parent: the parent widget
    :return: the qc document paths or None if user aborts
    """

    dialog = Gtk.FileChooserNative.new(title=_("Choose documents"),
                                       parent=parent,
                                       action=Gtk.FileChooserAction.OPEN)
    dialog.add_filter(_FILE_FILTERS.filter_docs)
    dialog.set_select_multiple(True)

    latest_directory = get_settings().latest_paths_import_qc_directory
    if path.isdir(latest_directory):
        dialog.set_current_folder(latest_directory)

    qc_documents = None
    if dialog.run() == Gtk.ResponseType.ACCEPT:
        qc_documents = dialog.get_filenames()

        if qc_documents:
            get_settings().latest_paths_import_qc_directory = str(path.dirname(qc_documents[0]))

    dialog.destroy()
    return qc_documents


def dialog_save_qc_document(video_file, parent=None):
    """
    Dialog which is used to save a qc document.

    :param video_file: the name of the video (no path and without extension)
    :param parent: the parent widget
    :return: the file path to save under or None if user aborts
    """

    dialog = Gtk.FileChooserNative.new(title=_("Choose a file name"),
                                       parent=parent,
                                       action=Gtk.FileChooserAction.SAVE)
    dialog.add_filter(_FILE_FILTERS.filter_docs)
    dialog.set_current_name(generate_file_name_proposal(video_file))
    dialog.set_select_multiple(False)
    dialog.set_do_overwrite_confirmation(True)

    latest_directory = get_settings().latest_paths_export_qc_directory
    if path.isdir(latest_directory):
        dialog.set_current_folder(latest_directory)

    file_name = None
    if dialog.run() == Gtk.ResponseType.ACCEPT:
        file_name = dialog.get_filename()
        file_name = file_name if file_name.endswith(".txt") else file_name + ".txt"

        get_settings().latest_paths_export_qc_directory = str(path.dirname(file_name))

    # todo escape specific file name characters

    dialog.destroy()
    return file_name
