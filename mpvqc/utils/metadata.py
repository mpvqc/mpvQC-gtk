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


class Metadata:

    # todo: Use dataclass once python 3.7+ becomes widely adopted

    def __init__(self,
                 app_id,
                 app_name,
                 app_url,
                 app_version,
                 path_resource_base,
                 path_logo,
                 vcs_hash,
                 vcs_tag):
        self.__app_id = app_id
        self.__app_name = app_name
        self.__app_url = app_url
        self.__path_resource_base = path_resource_base
        self.__path_logo = path_logo

        # Only accessible via get_app_version_str
        self.__app_version = app_version
        self.__vcs_hash = vcs_hash
        self.__vcs_tag = vcs_tag

        self.__version_mpv = None
        self.__version_ffmpeg = None

    @property
    def app_id(self):
        return self.__app_id

    @property
    def app_name(self):
        return self.__app_name

    @property
    def app_url(self):
        return self.__app_url

    @property
    def path_resource_base(self):
        return self.__path_resource_base

    @property
    def path_logo(self):
        return self.__path_logo

    def get_app_version_str(self, short=False):
        if self.__vcs_tag != "" and self.__vcs_hash != "":
            if short:
                return self.__vcs_tag
            else:
                return "{} - {}".format(self.__vcs_tag, self.__vcs_hash)
        else:
            return self.__app_version

    @property
    def version_mpv(self):
        return self.__version_mpv

    @version_mpv.setter
    def version_mpv(self, value):
        self.__version_mpv = value

    @property
    def version_ffmpeg(self):
        return self.__version_ffmpeg

    @version_ffmpeg.setter
    def version_ffmpeg(self, value):
        self.__version_ffmpeg = value
