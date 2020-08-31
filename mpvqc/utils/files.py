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


from pathlib import Path

from gi.repository import GLib


class FilePaths:

    def __init__(self):
        documents = Path(GLib.get_user_special_dir(GLib.USER_DIRECTORY_DOCUMENTS))
        pictures = Path(GLib.get_user_special_dir(GLib.USER_DIRECTORY_PICTURES))

        self.__dir_backup = documents / "mpvQC" / "backup"
        self.__dir_backup.mkdir(exist_ok=True, parents=True)

        self.__dir_config = documents / "mpvQC"
        self.__dir_config.mkdir(exist_ok=True, parents=True)

        self.__dir_screenshots = pictures / "mpvQC"
        self.__dir_screenshots.mkdir(exist_ok=True, parents=True)

    @property
    def dir_backup(self) -> Path:
        return self.__dir_backup

    @property
    def dir_config(self) -> Path:
        return self.__dir_config

    @property
    def dir_screenshots(self) -> Path:
        return self.__dir_screenshots
