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


import ctypes

from OpenGL import GL, GLX
from gi.repository import Gtk, Gdk, GLib
from mpv import OpenGlCbGetProcAddrFn, MpvRenderContext, MPV

from mpvqc import get_app_paths, get_app_metadata
from mpvqc.player.mpv import MpvPlayer


def _get_process_address(_, name):
    address = GLX.glXGetProcAddress(name.decode("utf-8"))
    return ctypes.cast(address, ctypes.c_void_p).value


def _set_versioning_metadata(mpv):
    metadata = get_app_metadata()
    metadata.version_mpv = mpv.version_mpv()
    metadata.version_ffmpeg = mpv.version_ffmpeg()


class WaylandContainer(Gtk.GLArea):

    def __init__(self, **properties):
        super().__init__(**properties)

        self._proc_addr_wrapper = OpenGlCbGetProcAddrFn(_get_process_address)

        self.__ctx = None
        self.__mpv = MpvPlayer()

        style: Gtk.StyleContext = self.get_style_context()
        style.add_class("video-area")

        # Add all events but let parent handle them
        self.add_events(Gdk.EventMask.POINTER_MOTION_MASK)
        self.add_events(Gdk.EventMask.BUTTON_PRESS_MASK)
        self.add_events(Gdk.EventMask.BUTTON_RELEASE_MASK)
        self.add_events(Gdk.EventMask.KEY_PRESS_MASK)
        self.add_events(Gdk.EventMask.STRUCTURE_MASK)
        self.add_events(Gdk.EventMask.SCROLL_MASK)

        self.connect("realize", self.on_realize)

    def on_realize(self, area):
        self.make_current()

        app_paths = get_app_paths()
        mpv = MPV(
            vo="libmpv",
            gpu_context="wayland",
            keep_open="yes",
            idle="yes",
            osc="yes",
            cursor_autohide="no",
            input_cursor="no",
            config="yes",
            input_default_bindings="no",
            config_dir=app_paths.dir_config,
            screenshot_directory=app_paths.dir_screenshots,
            log_handler=print
        )
        self.__ctx = MpvRenderContext(mpv, 'opengl', opengl_init_params={'get_proc_address': self._proc_addr_wrapper})
        self.__ctx.update_cb = self.on_mpv_callback
        self.__mpv.initialize(mpv)
        _set_versioning_metadata(self.__mpv)

    def do_render(self, *args):
        if self.__ctx:
            factor = self.get_scale_factor()
            rect = self.get_allocated_size()[0]

            width = rect.width * factor
            height = rect.height * factor

            fbo = GL.glGetIntegerv(GL.GL_DRAW_FRAMEBUFFER_BINDING)
            self.__ctx.render(flip_y=True, opengl_fbo={'w': width, 'h': height, 'fbo': fbo})
            return True
        return False

    def do_unrealize(self, *args, **kwargs):
        self.__ctx.free()
        self.__mpv.terminate()
        return True

    def on_mpv_callback(self):
        GLib.idle_add(self.call_frame_ready, None, GLib.PRIORITY_HIGH)

    def call_frame_ready(self, *args):
        if self.__ctx.update():
            self.queue_render()

    @property
    def player(self):
        return self.__mpv


class XContainer(Gtk.Label):

    def __init__(self, **properties):
        super().__init__(**properties)

        self.__mpv = MpvPlayer()

        style: Gtk.StyleContext = self.get_style_context()
        style.add_class("video-area")

        self.connect("realize", self.on_realize)

    def on_realize(self, *args):
        app_paths = get_app_paths()
        mpv = MPV(
            vo="gpu",
            wid=self.get_window().get_xid(),
            keep_open="yes",
            idle="yes",
            osc="yes",
            cursor_autohide="no",
            input_cursor="no",
            config="yes",
            input_default_bindings="no",
            config_dir=app_paths.dir_config,
            screenshot_directory=app_paths.dir_screenshots,
            log_handler=print
        )
        self.__mpv.initialize(mpv)
        _set_versioning_metadata(self.__mpv)

    def do_unrealize(self, *args, **kwargs):
        self.__mpv.terminate()
        return True

    @property
    def player(self):
        return self.__mpv


def get_mpv_widget(parent: Gtk.Widget):
    if parent.get_display().get_name().lower().startswith("wayland"):
        return WaylandContainer()
    return XContainer()
