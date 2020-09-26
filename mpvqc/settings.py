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
from os import path
from pathlib import Path
from typing import List, Tuple

from gi.repository import Gio

"""
How to add new settings entries:

1. Create a new key entry in the schema file: /data/com.github.mpvqc.mpvQC.gschema.xml
2. Create a new instance variable in the Settings class at the bottom of this file.
   Use _Bool() for boolean values, _Int() for int values etc.
   The key entry from (1) must be used to bind the settings objects. 
3. Expose only necessary functionality via Settings class but NOT the backing object
4. Use mpvqc.get_settings() method to access the settings object
"""


class _Storable:

    def __init__(self, key: str, settings: Gio.Settings):
        self._key = key
        self._settings = settings

    def set(self, value) -> None:
        """Sets a value for this storable object"""
        raise NotImplementedError()

    def get(self):
        """Gets the value for this storable object"""
        raise NotImplementedError()

    def bind(self, obj, prop, flags=Gio.SettingsBindFlags.DEFAULT):
        """Binds this setting bidirectionally to [obj] using [obj]'s [property]"""
        self._settings.bind(self._key, obj, prop, flags)

    def reset(self):
        """Resets the value for this storable object"""
        self._settings.reset(self._key)


class _Bool(_Storable):

    def set(self, value: bool) -> None:
        if self.get() != value:
            self._settings.set_boolean(self._key, value)

    def get(self) -> bool:
        return self._settings.get_boolean(self._key)


class _Int(_Storable):

    def set(self, value: int) -> None:
        if self.get() != value:
            self._settings.set_int(self._key, value)

    def get(self) -> int:
        return self._settings.get_int(self._key)


class _Str(_Storable):

    def set(self, value: str) -> None:
        if self.get() != value:
            self._settings.set_string(self._key, value)

    def get(self) -> str:
        return self._settings.get_string(self._key)


class _StrList(_Storable):

    def set(self, value: List[str] or Tuple[str]) -> None:
        if self.get() != value:
            self._settings.set_strv(self._key, value)

    def get(self) -> List[str]:
        return self._settings.get_strv(self._key)


class _Nickname(_Str):

    def __init__(self, key: str, settings: Gio.Settings):
        super().__init__(key, settings)
        if self.get() == "":
            from gi.repository import GLib
            self.set(GLib.get_user_name())


class _StrListCommentTypes(_Storable):

    def __init__(self, key: str, settings: Gio.Settings):
        super().__init__(key, settings)
        self.__current_lang_to_id = {
            _("Translation"): "Translation",
            _("Spelling"): "Spelling",
            _("Punctuation"): "Punctuation",
            _("Phrasing"): "Phrasing",
            _("Timing"): "Timing",
            _("Typeset"): "Typeset",
            _("Hint"): "Hint"
        }

    def set(self, value: List[str] or Tuple[str]) -> None:
        self._settings.set_strv(self._key, [self.__current_lang_to_id.get(x, x) for x in value])

    def get(self) -> List[str]:
        return [_(x) for x in self._settings.get_strv(self._key)]

    def longest(self) -> str:
        return max(self.get(), key=len)


class _PathList(_Storable):

    def __init__(self, key: str, settings: Gio.Settings, keep_max: int = 10):
        super().__init__(key, settings)
        self.__keep_max = keep_max

    def set(self, value: List[str] or Tuple[str]) -> None:
        self._settings.set_strv(self._key, value)

    def get(self) -> List[str]:
        return [p for p in self._settings.get_strv(self._key) if path.exists(p)][:self.__keep_max]

    def add(self, value: str) -> None:
        paths = self.get()
        if value in paths:
            paths.insert(0, paths.pop(paths.index(value)))
        else:
            paths.insert(0, value)
        self.set(paths)


class _ConfigFile:

    def __init__(self, resource_path: str):
        from mpvqc import get_app_paths
        self.__resource_path = resource_path
        self.__file_path = get_app_paths().dir_config / Path(resource_path).name
        self.__file_path.parent.mkdir(parents=True, exist_ok=True)

        self.__content_default = Gio \
            .resources_lookup_data(self.__resource_path, Gio.ResourceLookupFlags.NONE) \
            .get_data() \
            .decode("utf-8")
        self.__content = self.__read()

    def set_content(self, value: str) -> None:
        self.__content = value

    def get_content(self) -> str:
        return self.__content

    def get_file_path(self) -> str:
        return str(self.__file_path)

    def reset(self) -> None:
        self.__content = self.__content_default

    def write(self) -> None:
        if self.__content != self.__read():
            self.__perform_write(self.__content)

    def __read(self) -> str:
        if not self.__file_path.is_file():
            self.__perform_write(content=self.__content_default)
            return self.__content_default
        return self.__file_path.read_text(encoding="utf-8")

    def __perform_write(self, content) -> None:
        self.__file_path.write_text(content, encoding="utf-8")


class Settings:

    def __init__(self, app_id: str, app_resource_base_path: str):
        s = Gio.Settings.new(app_id)

        self.__header_bar_subtitle_format = _Int("header-bar-subtitle-format", s)

        self.__prefer_dark_theme = _Bool("prefer-dark-theme", s)

        self.__comment_types = _StrListCommentTypes("comment-types", s)

        self.__auto_save_enabled = _Bool("auto-backup-enabled", s)
        self.__auto_save_interval = _Int("auto-backup-interval", s)

        self.__status_bar_time_format = _Int("status-bar-time-format", s)
        self.__status_bar_percentage = _Bool("status-bar-percentage", s)

        self.__import_open_video_automatically = _Bool("import-open-video-automatically", s)

        self.__export_qc_document_nick = _Nickname("export-qc-document-nick", s)
        self.__export_append_nick = _Bool("export-append-nick", s)
        self.__export_write_header = _Bool("export-write-header", s)
        self.__export_write_date = _Bool("export-write-date", s)
        self.__export_write_generator = _Bool("export-write-generator", s)
        self.__export_write_nick = _Bool("export-write-nick", s)
        self.__export_write_path = _Bool("export-write-path", s)

        self.__latest_paths_import_qc_directory = _Str("latest-paths-import-qc-directory", s)
        self.__latest_paths_import_video_directory = _Str("latest-paths-import-video-directory", s)
        self.__latest_paths_import_subtitle_directory = _Str("latest-paths-import-subtitle-directory", s)
        self.__latest_paths_recent_files = _PathList("latest-paths-recent-files", s, keep_max=10)

        self.__config_input = _ConfigFile(resource_path=app_resource_base_path + "/config/input.conf")
        self.__config_mpv = _ConfigFile(resource_path=app_resource_base_path + "/config/mpv.conf")

    #
    # Header bar subtitle format
    #

    @property
    def header_subtitle_format(self) -> int:
        return self.__header_bar_subtitle_format.get()

    def bind_header_subtitle_format(self, obj, prop, flags=Gio.SettingsBindFlags.DEFAULT) -> None:
        self.__header_bar_subtitle_format.bind(obj, prop, flags)

    def reset_header_subtitle_format(self) -> None:
        self.__header_bar_subtitle_format.reset()

    #
    # Dark theme
    #

    @property
    def prefer_dark_theme(self) -> bool:
        return self.__prefer_dark_theme.get()

    @prefer_dark_theme.setter
    def prefer_dark_theme(self, value) -> None:
        self.__prefer_dark_theme.set(value)

    #
    # Comment types
    #

    @property
    def comment_types(self) -> List[str]:
        return self.__comment_types.get()

    @comment_types.setter
    def comment_types(self, value) -> None:
        self.__comment_types.set(value)

    @property
    def comment_types_longest(self) -> str:
        return self.__comment_types.longest()

    def reset_comment_types(self) -> None:
        self.__comment_types.reset()

    #
    # Auto save enabled
    #

    @property
    def auto_save_enabled(self) -> bool:
        return self.__auto_save_enabled.get()

    def reset_auto_save_enabled(self) -> None:
        self.__auto_save_enabled.reset()

    def bind_auto_save_enabled(self, obj, prop, flags=Gio.SettingsBindFlags.DEFAULT) -> None:
        self.__auto_save_enabled.bind(obj, prop, flags)

    #
    # Auto save interval
    #

    @property
    def auto_save_interval(self) -> int:
        return self.__auto_save_interval.get()

    def reset_auto_save_interval(self) -> None:
        self.__auto_save_interval.reset()

    def bind_auto_save_interval(self, obj, prop, flags=Gio.SettingsBindFlags.DEFAULT) -> None:
        self.__auto_save_interval.bind(obj, prop, flags)

    #
    # Status bar time format
    #

    @property
    def status_bar_time_format(self) -> int:
        return self.__status_bar_time_format.get()

    @status_bar_time_format.setter
    def status_bar_time_format(self, value) -> None:
        self.__status_bar_time_format.set(value)

    #
    # Status bar percentage
    #

    @property
    def status_bar_percentage(self) -> bool:
        return self.__status_bar_percentage.get()

    @status_bar_percentage.setter
    def status_bar_percentage(self, value) -> None:
        self.__status_bar_percentage.set(value)

    #
    # Import: open video automatically
    #

    @property
    def import_open_video_automatically(self) -> bool:
        return self.__import_open_video_automatically.get()

    def reset_import_open_video_automatically(self) -> None:
        self.__import_open_video_automatically.reset()

    def bind_import_open_video_automatically(self, obj, prop, flags=Gio.SettingsBindFlags.DEFAULT) -> None:
        self.__import_open_video_automatically.bind(obj, prop, flags)

    #
    # Export: qc document nickname
    #

    @property
    def export_qc_document_nick(self) -> str:
        return self.__export_qc_document_nick.get()

    def reset_qc_document_nick(self) -> None:
        self.__export_qc_document_nick.reset()

    def bind_export_qc_document_nick(self, obj, prop, flags=Gio.SettingsBindFlags.DEFAULT) -> None:
        self.__export_qc_document_nick.bind(obj, prop, flags)

    #
    # Export: append nick
    #

    @property
    def export_append_nick(self) -> bool:
        return self.__export_append_nick.get()

    def reset_export_append_nick(self) -> None:
        self.__export_append_nick.reset()

    def bind_export_append_nick(self, obj, prop, flags=Gio.SettingsBindFlags.DEFAULT) -> None:
        self.__export_append_nick.bind(obj, prop, flags)

    #
    # Export: write header
    #

    @property
    def export_write_header(self) -> bool:
        return self.__export_write_header.get()

    def reset_export_write_header(self) -> None:
        self.__export_write_header.reset()

    def bind_export_write_header(self, obj, prop, flags=Gio.SettingsBindFlags.DEFAULT) -> None:
        self.__export_write_header.bind(obj, prop, flags)

    #
    # Export: write date
    #

    @property
    def export_write_date(self) -> bool:
        return self.__export_write_date.get()

    def reset_export_write_date(self) -> None:
        self.__export_write_date.reset()

    def bind_export_write_date(self, obj, prop, flags=Gio.SettingsBindFlags.DEFAULT) -> None:
        self.__export_write_date.bind(obj, prop, flags)

    #
    # Export: write generator
    #

    @property
    def export_write_generator(self) -> bool:
        return self.__export_write_generator.get()

    def reset_export_write_generator(self) -> None:
        self.__export_write_generator.reset()

    def bind_export_write_generator(self, obj, prop, flags=Gio.SettingsBindFlags.DEFAULT) -> None:
        self.__export_write_generator.bind(obj, prop, flags)

    #
    # Export: write nickname
    #

    @property
    def export_write_nick(self) -> bool:
        return self.__export_write_nick.get()

    def reset_export_write_nick(self) -> None:
        self.__export_write_nick.reset()

    def bind_export_write_nick(self, obj, prop, flags=Gio.SettingsBindFlags.DEFAULT) -> None:
        self.__export_write_nick.bind(obj, prop, flags)

    #
    # Export: write path
    #

    @property
    def export_write_path(self) -> bool:
        return self.__export_write_path.get()

    def reset_export_write_path(self) -> None:
        self.__export_write_path.reset()

    def bind_export_write_path(self, obj, prop, flags=Gio.SettingsBindFlags.DEFAULT) -> None:
        self.__export_write_path.bind(obj, prop, flags)

    #
    # Latest files: import qc directory
    #

    @property
    def latest_paths_import_qc_directory(self) -> str:
        return self.__latest_paths_import_qc_directory.get()

    @latest_paths_import_qc_directory.setter
    def latest_paths_import_qc_directory(self, value) -> None:
        self.__latest_paths_import_qc_directory.set(value)

    #
    # Latest files: import video directory
    #

    @property
    def latest_paths_import_video_directory(self) -> str:
        return self.__latest_paths_import_video_directory.get()

    @latest_paths_import_video_directory.setter
    def latest_paths_import_video_directory(self, value) -> None:
        self.__latest_paths_import_video_directory.set(value)

    #
    # Latest files: import subtitle directory
    #

    @property
    def latest_paths_import_subtitle_directory(self) -> str:
        return self.__latest_paths_import_subtitle_directory.get()

    @latest_paths_import_subtitle_directory.setter
    def latest_paths_import_subtitle_directory(self, value) -> None:
        self.__latest_paths_import_subtitle_directory.set(value)

    #
    # Latest files: recent files
    #

    @property
    def latest_paths_recent_files(self) -> List[str]:
        return self.__latest_paths_recent_files.get()

    def latest_paths_recent_files_add(self, f_path: str) -> None:
        self.__latest_paths_recent_files.add(f_path)

    def reset_latest_paths_recent_files(self) -> None:
        self.__latest_paths_recent_files.reset()

    #
    # Config file: input.conf
    #

    @property
    def config_file_input_path(self) -> str:
        return self.__config_input.get_file_path()

    @property
    def config_file_input_content(self) -> str:
        return self.__config_input.get_content()

    @config_file_input_content.setter
    def config_file_input_content(self, value) -> None:
        self.__config_input.set_content(value)

    def reset_config_file_input_content(self) -> None:
        self.__config_input.reset()

    def write_config_file_input_content(self) -> None:
        self.__config_input.write()

    #
    # Config file: mpv.conf
    #

    @property
    def config_file_mpv_path(self) -> str:
        return self.__config_mpv.get_file_path()

    @property
    def config_file_mpv_content(self) -> str:
        return self.__config_mpv.get_content()

    @config_file_mpv_content.setter
    def config_file_mpv_content(self, value) -> None:
        self.__config_mpv.set_content(value)

    def reset_config_file_mpv_content(self) -> None:
        self.__config_mpv.reset()

    def write_config_file_mpv_content(self) -> None:
        self.__config_mpv.write()
