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


from mpvqc.app import Application
from mpvqc.settings import Settings
from mpvqc.utils.files import FilePaths
from mpvqc.utils.metadata import Metadata


class AppHolder:
    APP = None
    METADATA = None
    PATHS = None
    SETTINGS = None


def get_app() -> Application:
    return AppHolder.APP


def get_app_metadata() -> Metadata:
    return AppHolder.METADATA


def get_app_paths() -> FilePaths:
    return AppHolder.PATHS


def get_settings() -> Settings:
    return AppHolder.SETTINGS
