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


from locale import gettext as _
from os import path

from gi.repository import Gtk

from mpvqc import get_settings
from mpvqc.utils.draganddrop import SUPPORTED_SUB_FILES

filter_video = Gtk.FileFilter()
filter_video.set_name(_("Videos"))
filter_video.add_mime_type("video/*")

filter_subtitles = Gtk.FileFilter()
filter_subtitles.set_name(_("Subtitles"))
for ext in SUPPORTED_SUB_FILES:
    filter_subtitles.add_pattern("*{}".format(ext))

filter_qc = Gtk.FileFilter()
filter_qc.set_name(_("Documents"))
filter_qc.add_pattern("*.txt")


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

    dialog = Gtk.FileChooserDialog(title=_("Choose a video file"),
                                   parent=parent,
                                   action=Gtk.FileChooserAction.OPEN)
    dialog.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL)
    dialog.add_buttons(Gtk.STOCK_OPEN, Gtk.ResponseType.OK)
    dialog.add_filter(filter_video)
    dialog.set_select_multiple(False)

    latest_directory = get_settings().latest_paths_import_video_directory
    if path.isdir(latest_directory):
        dialog.set_current_folder(latest_directory)

    video = None
    if dialog.run() == Gtk.ResponseType.OK:
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

    dialog = Gtk.FileChooserDialog(title=_("Choose subtitle files"),
                                   parent=parent,
                                   action=Gtk.FileChooserAction.OPEN)
    dialog.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL)
    dialog.add_buttons(Gtk.STOCK_OPEN, Gtk.ResponseType.OK)
    dialog.add_filter(filter_subtitles)
    dialog.set_select_multiple(True)

    latest_directory = get_settings().latest_paths_import_subtitle_directory
    if path.isdir(latest_directory):
        dialog.set_current_folder(latest_directory)

    subtitles = None
    if dialog.run() == Gtk.ResponseType.OK:
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

    dialog = Gtk.FileChooserDialog(title=_("Choose documents"),
                                   parent=parent,
                                   action=Gtk.FileChooserAction.OPEN)
    dialog.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL)
    dialog.add_buttons(Gtk.STOCK_OPEN, Gtk.ResponseType.OK)
    dialog.add_filter(filter_qc)
    dialog.set_select_multiple(True)

    latest_directory = get_settings().latest_paths_import_qc_directory
    if path.isdir(latest_directory):
        dialog.set_current_folder(latest_directory)

    qc_documents = None
    if dialog.run() == Gtk.ResponseType.OK:
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

    dialog = Gtk.FileChooserDialog(title=_("Choose a file name"),
                                   parent=parent,
                                   action=Gtk.FileChooserAction.SAVE)
    dialog.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL)
    dialog.add_buttons(Gtk.STOCK_SAVE, Gtk.ResponseType.ACCEPT)
    dialog.add_filter(filter_qc)
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
