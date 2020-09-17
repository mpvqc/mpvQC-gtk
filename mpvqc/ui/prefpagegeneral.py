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

from gi.repository import Gtk, Gio, GObject

from mpvqc import get_settings, template_custom
from mpvqc.ui.input import InputPopover
from mpvqc.utils import list_header_func
from mpvqc.utils.signals import APPLY
from mpvqc.utils.validators import NewCommentTypeValidator, ExistingCommentTypeValidator


@template_custom.TemplateTrans(resource_path='/data/ui/prefpagegeneral.ui')
class PreferencePageGeneral(Gtk.ScrolledWindow):
    __gtype_name__ = 'PreferencePageGeneral'

    class CommentTypeListItem(GObject.GObject):
        text = GObject.Property(type=str)

    list_ct = Gtk.Template.Child()

    button_ct_add = Gtk.Template.Child()
    button_ct_remove = Gtk.Template.Child()
    button_ct_edit = Gtk.Template.Child()
    button_ct_up = Gtk.Template.Child()
    button_ct_down = Gtk.Template.Child()

    cbox_header: Gtk.ComboBox = Gtk.Template.Child()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.init_template()

        # Set up comment type list
        self.__comment_type_model = Gio.ListStore()
        self.__set_up_comment_types_list_widget()
        self.__set_comment_type_content()

        # Set up header combo box
        self.__combo_model = Gtk.ListStore(str)
        self.__set_up_combo_box_header_subtitle()

        self.list_ct.unselect_all()

    def on_preferences_closed(self):
        """
        Called when preferences view is closed.
        """

        self.list_ct.unselect_all()

    def on_restore_default_clicked(self):
        """
        Called whenever the user presses restore and this preference page is visible.
        """

        s = get_settings()
        s.reset_header_subtitle_format()
        s.reset_comment_types()

        self.__set_comment_type_content()

    def __set_comment_type_content(self):
        """
        Set initial values from settings.
        """

        self.__comment_type_model.remove_all()

        for comment_type in get_settings().comment_types:
            self.__ct_add_item(comment_type)

    """ 
    Header bar subtitle related 
    """

    def __set_up_combo_box_header_subtitle(self):
        """
        Sets up the combo box regarding the display subtitle.
        """

        self.__combo_model.append([_("Display nothing")])
        self.__combo_model.append([_("Current file name")])
        self.__combo_model.append([_("Current file path")])
        renderer = Gtk.CellRendererText()
        self.cbox_header.pack_start(renderer, True)
        self.cbox_header.add_attribute(renderer, "text", 0)
        self.cbox_header.set_model(self.__combo_model)
        get_settings().bind_header_subtitle_format(self.cbox_header, "active")

    """ 
    Comment type related 
    """

    def __set_up_comment_types_list_widget(self):
        """
        Sets up the comment type list widget
        """

        self.list_ct.bind_model(self.__comment_type_model, ct_create_widget_func)
        self.list_ct.set_placeholder(_get_placeholder())
        self.list_ct.set_header_func(list_header_func, None)

    @template_custom.TemplateTrans.Callback()
    def on_ct_add_button_clicked(self, widget):
        """
        When user clicks on the 'plus' button.
        """

        def __apply(widget, new_value):
            self.__ct_add_item(text=new_value, position=0)
            self.list_ct.select_row(self.list_ct.get_row_at_index(0))
            self.__update_comment_type_setting()

        pop = InputPopover(label=_("New comment type:"),
                           validator=NewCommentTypeValidator(),
                           placeholder=_("Enter a new comment type"),
                           current_text="")
        pop.set_relative_to(self.button_ct_add)
        pop.connect(APPLY, __apply)
        pop.popup()

    @template_custom.TemplateTrans.Callback()
    def on_ct_remove_button_clicked(self, widget):
        """
        When user clicks on the 'minus' button.
        """

        self.__comment_type_model.remove(position=self.list_ct.get_selected_row().get_index())
        self.__update_comment_type_setting()

    @template_custom.TemplateTrans.Callback()
    def on_ct_edit_button_clicked(self, widget):
        """
        When user clicks on the 'edit' button.
        """

        row = self.list_ct.get_selected_row()
        idx = row.get_index()
        item = self.__comment_type_model.get_item(position=idx)

        current_label = row.get_children()[0].get_children()[0]
        current_text = item.text

        def __apply(widget, new_value):
            current_label.set_text(new_value)
            item.text = new_value
            self.__update_comment_type_setting()

        pop = InputPopover(label=_("Edit comment type:"),
                           validator=ExistingCommentTypeValidator(current_comment_type=current_text),
                           placeholder=_("Enter a new comment type"),
                           current_text=current_text)
        pop.set_position(Gtk.PositionType.RIGHT)
        pop.set_relative_to(current_label)
        pop.connect(APPLY, __apply)
        pop.popup()

    @template_custom.TemplateTrans.Callback()
    def on_ct_up_button_clicked(self, widget):
        """
        When user clicks on the 'go-up' button.
        """

        idx_cur = self.list_ct.get_selected_row().get_index()
        idx_new = idx_cur - 1

        item = self.__comment_type_model.get_item(position=idx_cur)

        self.__comment_type_model.remove(position=idx_cur)
        self.__comment_type_model.insert(idx_new, item)
        self.list_ct.select_row(self.list_ct.get_row_at_index(idx_new))
        self.__update_comment_type_setting()

    @template_custom.TemplateTrans.Callback()
    def on_ct_down_button_clicked(self, widget):
        """
        When user clicks on the 'go-down' button.
        """

        idx_cur = self.list_ct.get_selected_row().get_index()
        idx_new = idx_cur + 1

        item = self.__comment_type_model.get_item(position=idx_cur)

        self.__comment_type_model.remove(position=idx_cur)
        self.__comment_type_model.insert(idx_new, item)
        self.list_ct.select_row(self.list_ct.get_row_at_index(idx_new))
        self.__update_comment_type_setting()

    @template_custom.TemplateTrans.Callback()
    def on_ct_list_row_selected(self, widget, row):
        """
        When the selection of a row changes.
        """

        if row:
            row_idx = row.get_index()
            self.button_ct_edit.set_sensitive(True)
            self.button_ct_remove.set_sensitive(True)
            self.button_ct_up.set_sensitive(row_idx != 0)
            self.button_ct_down.set_sensitive(row_idx != max(0, len(self.list_ct) - 1))
        else:
            self.button_ct_edit.set_sensitive(False)
            self.button_ct_remove.set_sensitive(False)
            self.button_ct_up.set_sensitive(False)
            self.button_ct_down.set_sensitive(False)

    def __ct_add_item(self, text, position=None):
        """
        Inserts a new comment type item into the list.

        :param text: the text of the new comment type
        :param position: if a position (as int) is given, the item will be inserted at that position
        """

        item = PreferencePageGeneral.CommentTypeListItem()
        item.text = text

        if position is None:
            self.__comment_type_model.append(item)
        else:
            self.__comment_type_model.insert(position, item)

    def __update_comment_type_setting(self):
        """
        Updates the comment type setting.
        """

        new_comment_types = []
        for idx, __ in enumerate(self.list_ct):
            new_comment_types.append(self.__comment_type_model.get_item(idx).text)

        get_settings().comment_types = new_comment_types


def ct_create_widget_func(item):
    """
    This method is used to create a new row in the comment type list widget.

    :param item: which will provide the content for the row
    :return: the new widget
    """

    label = Gtk.Label(label=item.text)
    label.set_halign(align=Gtk.Align.START)
    label.set_valign(align=Gtk.Align.CENTER)

    box = Gtk.Box()
    box.set_margin_start(margin=20)
    box.pack_start(child=label, expand=True, fill=True, padding=0)

    row = Gtk.ListBoxRow()
    row.add(box)
    row.set_size_request(100, 50)
    row.set_can_focus(False)

    row.show_all()

    return row


def _get_placeholder():
    """
    Return a placeholder widget if no comment type is available.
    """

    label = Gtk.Label(label=_("No comment type yet"))
    label.set_halign(align=Gtk.Align.START)
    label.set_valign(align=Gtk.Align.CENTER)
    label.set_margin_start(margin=20)
    label.set_sensitive(False)
    label.set_size_request(100, 50)
    label.show_all()
    return label
