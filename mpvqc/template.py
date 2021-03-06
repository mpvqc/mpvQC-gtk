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


import os
import platform
import sys
import xml.etree.ElementTree as ET
from gettext import gettext as _

from gi.repository import GLib, GObject, Gio

_PERFORM_MANUAL_TRANSLATION = platform.system() == "Windows" and not os.environ['LANGUAGE'].startswith("en")


def connect_func(builder, obj, signal_name, handler_name,
                 connect_object, flags, cls):
    if handler_name not in cls.__gtktemplate_methods__:
        return

    method_name = cls.__gtktemplate_methods__[handler_name]
    template_inst = builder.get_object(cls.__gtype_name__)
    template_inst.__gtktemplate_handlers__.add(handler_name)
    handler = getattr(template_inst, method_name)

    after = int(flags & GObject.ConnectFlags.AFTER)
    swapped = int(flags & GObject.ConnectFlags.SWAPPED)
    if swapped:
        raise RuntimeError(
            "%r not supported" % GObject.ConnectFlags.SWAPPED)

    if connect_object is not None:
        if after:
            func = obj.connect_object_after
        else:
            func = obj.connect_object
        func(signal_name, handler, connect_object)
    else:
        if after:
            func = obj.connect_after
        else:
            func = obj.connect
        func(signal_name, handler)


def register_template(cls):
    bound_methods = {}
    bound_widgets = {}

    for attr_name, obj in list(cls.__dict__.items()):
        if isinstance(obj, CallThing):
            setattr(cls, attr_name, obj._func)
            handler_name = obj._name
            if handler_name is None:
                handler_name = attr_name

            if handler_name in bound_methods:
                old_attr_name = bound_methods[handler_name]
                raise RuntimeError(
                    "Error while exposing handler %r as %r, "
                    "already available as %r" % (
                        handler_name, attr_name, old_attr_name))
            else:
                bound_methods[handler_name] = attr_name
        elif isinstance(obj, Child):
            widget_name = obj._name
            if widget_name is None:
                widget_name = attr_name

            if widget_name in bound_widgets:
                old_attr_name = bound_widgets[widget_name]
                raise RuntimeError(
                    "Error while exposing child %r as %r, "
                    "already available as %r" % (
                        widget_name, attr_name, old_attr_name))
            else:
                bound_widgets[widget_name] = attr_name
                cls.bind_template_child_full(widget_name, obj._internal, 0)

    cls.__gtktemplate_methods__ = bound_methods
    cls.__gtktemplate_widgets__ = bound_widgets

    cls.set_connect_func(connect_func, cls)

    base_init_template = cls.init_template
    cls.__dontuse_ginstance_init__ = \
        lambda s: init_template(s, cls, base_init_template)
    # To make this file work with older PyGObject we expose our init code
    # as init_template() but make it a noop when we call it ourselves first
    cls.init_template = cls.__dontuse_ginstance_init__


def init_template(self, cls, base_init_template):
    self.init_template = lambda: None

    if self.__class__ is not cls:
        raise TypeError(
            "Inheritance from classes with @template_custom.TemplateTrans decorators "
            "is not allowed at this time")

    self.__gtktemplate_handlers__ = set()

    base_init_template(self)

    for widget_name, attr_name in self.__gtktemplate_widgets__.items():
        self.__dict__[attr_name] = self.get_template_child(cls, widget_name)

    for handler_name, attr_name in self.__gtktemplate_methods__.items():
        if handler_name not in self.__gtktemplate_handlers__:
            raise RuntimeError(
                "Handler '%s' was declared with @template_custom.TemplateTrans.Callback "
                "but was not present in template" % handler_name)


class Child(object):

    def __init__(self, name=None, **kwargs):
        self._name = name
        self._internal = kwargs.pop("internal", False)
        if kwargs:
            raise TypeError("Unhandled arguments: %r" % kwargs)


class CallThing(object):

    def __init__(self, name, func):
        self._name = name
        self._func = func


class Callback(object):

    def __init__(self, name=None):
        self._name = name

    def __call__(self, func):
        return CallThing(self._name, func)


def validate_resource_path(path):
    """Raises GLib.Error in case the resource doesn't exist"""

    try:
        Gio.resources_get_info(path, Gio.ResourceLookupFlags.NONE)
    except GLib.Error:
        # resources_get_info() doesn't handle overlays but we keep using it
        # as a fast path.
        # https://gitlab.gnome.org/GNOME/pygobject/issues/230
        Gio.resources_lookup_data(path, Gio.ResourceLookupFlags.NONE)


class Template(object):

    def __init__(self, **kwargs):
        self.string = None
        self.filename = None
        self.resource_path = None
        if "string" in kwargs:
            self.string = kwargs.pop("string")
        elif "filename" in kwargs:
            self.filename = kwargs.pop("filename")
        elif "resource_path" in kwargs:
            self.resource_path = kwargs.pop("resource_path")
        else:
            raise TypeError(
                "Requires one of the following arguments: "
                "string, filename, resource_path")

        if kwargs:
            raise TypeError("Unhandled keyword arguments %r" % kwargs)

    @classmethod
    def from_file(cls, filename):
        return cls(filename=filename)

    @classmethod
    def from_string(cls, string):
        return cls(string=string)

    @classmethod
    def from_resource(cls, resource_path):
        return cls(resource_path=resource_path)

    Callback = Callback

    Child = Child

    def __call__(self, cls):
        from gi.repository import Gtk

        if not isinstance(cls, type) or not issubclass(cls, Gtk.Widget):
            raise TypeError("Can only use @template_custom.TemplateTrans on Widgets")

        if "__gtype_name__" not in cls.__dict__:
            raise TypeError(
                "%r does not have a __gtype_name__. Set it to the name "
                "of the class in your template" % cls.__name__)

        if hasattr(cls, "__gtktemplate_methods__"):
            raise TypeError("Cannot nest template classes")

        if self.string is not None:
            data = self.string
            if not isinstance(data, bytes):
                data = data.encode("utf-8")
            bytes_ = GLib.Bytes.new(data)
            cls.set_template(bytes_)
            register_template(cls)
            return cls
        elif self.resource_path is not None:
            validate_resource_path(self.resource_path)
            cls.set_template_from_resource(self.resource_path)
            register_template(cls)
            return cls
        else:
            assert self.filename is not None
            file_ = Gio.File.new_for_path(self.filename)
            bytes_ = GLib.Bytes.new(file_.load_contents()[1])
            cls.set_template(bytes_)
            register_template(cls)
            return cls


class TemplateTrans(Template):

    def __call__(self, cls):
        if not _PERFORM_MANUAL_TRANSLATION:
            return super(TemplateTrans, self).__call__(cls)
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
