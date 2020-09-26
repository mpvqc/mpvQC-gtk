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

from gi.repository import Gtk


def message_dialog_imported_files_are_not_valid(not_valid_files, parent=None):
    """
    Displays a message box to let the user know that he tries to import non valid qc document files.

    :param not_valid_files: the files which were not valid
    :param parent: the parent widget to attach to dialog to
    """

    not_valid = "\n".join(not_valid_files)
    title = _("Files not usable")
    message = _("The following files are not compatible with this application:") + "\n\n" + not_valid

    dialog = Gtk.MessageDialog(transient_for=parent,
                               destroy_with_parent=True,
                               modal=True,
                               buttons=Gtk.ButtonsType.OK,
                               text=message)
    dialog.set_title(title)
    dialog.show_all()

    dialog.run()
    dialog.destroy()


def message_dialog_video_found_ask_to_open(file, parent=None):
    """
    Displays a message box to ask the user if he wants to open a video found in the qc document files.

    :param file: the file path for the user to chose to open it
    :param parent: the parent widget to attach to dialog to
    """

    title = _("Video found")
    message = _("Open the following video?") + "\n\n" + file

    dialog = Gtk.MessageDialog(transient_for=parent,
                               destroy_with_parent=True,
                               buttons=Gtk.ButtonsType.YES_NO,
                               text=message)
    dialog.set_title(title)
    dialog.show_all()

    response = dialog.run()
    dialog.destroy()
    return response


def message_dialog_what_to_do_with_existing_comments(parent=None):
    """
    Displays a message box to ask the user if he wants to keep existing comments,
    delete existing comments or abort import.

    :param parent: the parent widget to attach to dialog to
    """

    title = _("Existing comments")
    message = _("What do you want to do with existing comments?")

    choice_keep = (_("Keep"), 0)
    choice_delete = (_("Delete"), 1)
    choice_abort = (_("Abort import"), 2)

    dialog = Gtk.MessageDialog(transient_for=parent,
                               destroy_with_parent=True,
                               text=message)
    dialog.add_button(*choice_keep)
    dialog.add_button(*choice_delete)
    dialog.add_button(*choice_abort)
    dialog.set_title(title)
    dialog.show_all()

    response = dialog.run()
    dialog.destroy()
    return response


def message_dialog_unsaved_qc_document_clear_comments(parent=None):
    """
    Displays a message box asking the user if he wants to really clear comments that are not saved.

    :param parent: the parent widget to attach to dialog to
    """

    title = _("Delete existing comments")
    message = _("You have unsaved changes. Do you really want to proceed?") + "\n" \
              + _("All unsaved changes will be lost.")

    choice_delete = (_("Delete comments"), 0)
    choice_abort = (_("Abort"), 1)

    dialog = Gtk.MessageDialog(transient_for=parent,
                               destroy_with_parent=True,
                               text=message)
    dialog.add_button(*choice_delete)
    dialog.add_button(*choice_abort)
    dialog.set_title(title)
    dialog.show_all()

    response = dialog.run()
    dialog.destroy()
    return response


def message_dialog_unsaved_qc_document_proceed(parent=None):
    """
    Displays a message box asking the user if he wants to continue with his action even if some changes will be lost.

    :param parent: the parent widget to attach to dialog to
    """

    title = _("Unsaved changes")
    message = _("You have unsaved changes. Do you really want to proceed?") + "\n" \
              + _("All unsaved changes will be lost.")

    choice_continue = (_("Continue"), 0)
    choice_abort = (_("Abort"), 1)

    dialog = Gtk.MessageDialog(transient_for=parent,
                               destroy_with_parent=True,
                               text=message)
    dialog.add_button(*choice_continue)
    dialog.add_button(*choice_abort)
    dialog.set_title(title)
    dialog.show_all()

    response = dialog.run()
    dialog.destroy()
    return response


def message_dialog_leave_with_unsaved_qc_document(parent=None):
    """
    Displays a message box asking the user if he wants to really quit while he has unsaved changes.

    :param parent: the parent widget to attach to dialog to
    """

    title = _("Unsaved changes")
    message = _("You have unsaved changes. Do you really want to quit?") + "\n" \
              + _("All unsaved changes will be lost.")

    choice_leave = (_("Leave without saving"), 0)
    choice_abort = (_("Abort"), 1)

    dialog = Gtk.MessageDialog(transient_for=parent,
                               destroy_with_parent=True,
                               text=message)
    dialog.add_button(*choice_leave)
    dialog.add_button(*choice_abort)
    dialog.set_title(title)
    dialog.show_all()

    response = dialog.run()
    dialog.destroy()
    return response


def message_dialog_document_save_failed(parent=None):
    """
    Displays a message dialog telling the user that saving failed.
    """

    title = _("Saving the QC Document Failed")
    message = _("Are you sure you have permission to write in the selected directory?")

    dialog = Gtk.MessageDialog(transient_for=parent,
                               destroy_with_parent=True,
                               modal=True,
                               buttons=Gtk.ButtonsType.OK,
                               text=message)
    dialog.set_title(title)
    dialog.show_all()
    dialog.run()
    dialog.destroy()
