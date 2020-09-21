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


# Signals from mpv (to get a list of all possible properties run 'mpv --list-properties')
MPVQC_DURATION \
    = "duration"
MPVQC_FILENAME_NO_EXT \
    = "filename/no-ext"
MPVQC_PATH \
    = "path"
MPVQC_PERCENT_POS \
    = "percent-pos"
MPVQC_TIME_POS \
    = "time-pos"
MPVQC_TIME_REMAINING \
    = "time-remaining"

# Completely custom signals
MPVQC_APPLY \
    = "mpvqc-apply"
MPVQC_CREATE_NEW_COMMENT \
    = "mpvqc-create-new-comment"
MPVQC_ON_VIDEO_RESIZE \
    = "mpvqc-on_video_resize"
MPVQC_QC_STATE_CHANGED \
    = "mpvqc-qc-state-changed"
MPVQC_STATUSBAR_UPDATE \
    = "mpvqc-statusbar-update"
MPVQC_TABLE_CONTENT_CHANGED \
    = "mpvqc-table-content-changed"
MPVQC_USER_RESIZE_VIDEO \
    = "mpvqc-user-resize-video"
