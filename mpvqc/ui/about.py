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


from gi.repository import Gtk, GdkPixbuf

from mpvqc import get_app_metadata


@Gtk.Template(resource_path='/data/ui/about.ui')
class AboutDialog(Gtk.AboutDialog):
    __gtype_name__ = 'AboutDialog'

    label_version_ffmpeg: Gtk.Label = Gtk.Template.Child()
    label_version_mpv: Gtk.Label = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.init_template()

        metadata = get_app_metadata()
        self.set_name(metadata.app_name)
        self.set_version(metadata.get_app_version_str())
        self.set_website_label(metadata.app_url)
        self.set_website(metadata.app_url)
        self.set_logo(GdkPixbuf.Pixbuf.new_from_resource(resource_path=metadata.path_logo))
        self.label_version_mpv.set_text(metadata.version_mpv)
        self.label_version_ffmpeg.set_text(metadata.version_ffmpeg)
