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


import sys


def main(app_id, app_name, app_url, app_version, vcs_hash, vcs_tag):
    from mpvqc import AppHolder

    path_resource_base = "/data"
    path_logo = path_resource_base + "/com.github.mpvqc.mpvQC.svg"

    # Metadata
    from mpvqc.utils.metadata import Metadata
    AppHolder.METADATA = Metadata(app_id=app_id,
                                  app_name=app_name,
                                  app_url=app_url,
                                  app_version=app_version,
                                  path_resource_base=path_resource_base,
                                  path_logo=path_logo,
                                  vcs_hash=vcs_hash,
                                  vcs_tag=vcs_tag)

    # Paths
    from mpvqc.utils.files import FilePaths
    AppHolder.PATHS = FilePaths()

    # Settings
    from mpvqc import Settings
    AppHolder.SETTINGS = Settings(app_id=app_id,
                                  app_resource_base_path=path_resource_base)

    # App itself
    from mpvqc.app import Application
    AppHolder.APP = Application(app_id=app_id,
                                app_name=app_name,
                                app_resource_base_path=path_resource_base)

    return AppHolder.APP.run(sys.argv)
