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
import sys
import xml.etree.ElementTree as ET
from gettext import gettext as _

from gi._gtktemplate import register_template, validate_resource_path, Template
from gi.repository import GLib, Gio

_PERFORM_MANUAL_TRANSLATION = bool(platform.system() == "Windows")


class TemplateTrans(Template):

    def __new__(cls, *args, **kwargs):
        if not _PERFORM_MANUAL_TRANSLATION:
            from gi.repository import Gtk
            return Gtk.Template.__new__(cls)
        return object.__new__(cls)

    def __call__(self, cls):
        if self.resource_path is not None:
            validate_resource_path(self.resource_path)
            element = Gio.resources_lookup_data(self.resource_path, Gio.ResourceLookupFlags.NONE) \
                .get_data().decode('utf-8')
            tree = ET.fromstring(element)
            for node in tree.iter():
                context = ''
                if 'context' in node.attrib:
                    context = node.attrib['context'] + "\x04"
                if 'translatable' in node.attrib:
                    node.text = _(context + node.text)
            as_str = ET.tostring(tree, encoding='unicode', method='xml')
            as_byte = as_str.encode("utf-8")
            bytes_ = GLib.Bytes.new(as_byte)
            cls.set_template(bytes_)
            register_template(cls)
            return cls
        else:
            if _PERFORM_MANUAL_TRANSLATION:
                print("Translation will not work. To get working translations use 'resource_path='/path/to/gui.ui'",
                      file=sys.stderr)
            super(TemplateTrans, self).__call__(cls)
