from gi.repository import Gtk

from mpvqc import template
from mpvqc.ui.window import MpvqcWindow


@template.TemplateTrans(resource_path='/data/ui/contentpref.ui')
class ContentPref(Gtk.Box):
    __gtype_name__ = 'ContentPref'

    _header_bar: Gtk.HeaderBar = template.TemplateTrans.Child()
    _stack: Gtk.Stack = template.TemplateTrans.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.init_template()

        print(self._header_bar)
        print(self._stack)

    @property
    def __parent(self) -> MpvqcWindow:
        return self.get_parent().get_parent()

    @property
    def header_bar(self):
        return self._header_bar
