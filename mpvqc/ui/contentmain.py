from gi.repository import Gtk

from mpvqc import template, get_settings
from mpvqc.ui.window import MpvqcWindow


@template.TemplateTrans(resource_path='/data/ui/contentmain.ui')
class ContentMain(Gtk.Box):
    __gtype_name__ = 'ContentMain'

    _header_bar: Gtk.HeaderBar = template.TemplateTrans.Child()
    _stack: Gtk.Stack = template.TemplateTrans.Child()

    _button_dark_theme = template.TemplateTrans.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.init_template()

        print(self._header_bar)
        print(self._stack)

        s = get_settings()

        self._button_dark_theme.set_property("role", Gtk.ButtonRole.CHECK)
        self._button_dark_theme.set_property("active", s.prefer_dark_theme)
        Gtk.Settings.get_default().set_property("gtk-application-prefer-dark-theme", s.prefer_dark_theme)

    @property
    def __parent(self) -> MpvqcWindow:
        return self.get_parent().get_parent()

    @property
    def header_bar(self):
        return self._header_bar

    @template.TemplateTrans.Callback()
    def _on_button_dark_theme_toggle_clicked(self, *data):
        s = get_settings()
        s.prefer_dark_theme = not s.prefer_dark_theme

        self._button_dark_theme.set_property("active", s.prefer_dark_theme)
        Gtk.Settings.get_default().set_property("gtk-application-prefer-dark-theme", s.prefer_dark_theme)

    @template.TemplateTrans.Callback()
    def _on_menu_preferences_clicked(self, *widget):
        self.__parent.show_pref()


