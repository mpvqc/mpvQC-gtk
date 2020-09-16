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
import platform
from abc import abstractmethod

from gi.repository import Gtk, Gdk, GLib

from mpvqc import get_app_paths, get_app_metadata
from mpvqc.player import MpvPlayer
from mpvqc.player.mpv import OpenGlCbGetProcAddrFn, MpvRenderContext, MPV


class Container:

    @property
    @abstractmethod
    def player(self) -> MpvPlayer:
        """Returns the embedded 'high level mpy player' of the container"""
        raise NotImplementedError()


class __LinuxContainerX(Container, Gtk.Label):

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
    def player(self) -> MpvPlayer:
        return self.__mpv


class __RenderContainer(Container, Gtk.GLArea):

    def __init__(self, **properties):
        super().__init__(**properties)

        # OpenGL

        import glfw

        glfw.init()
        glfw.set_error_callback(self.__error_cb)
        glfw.window_hint(glfw.VISIBLE, glfw.FALSE)

        self.__gl_window = glfw.create_window(1, 1, "mpvQC-OpenGL", None, None)

        if not self.__gl_window:
            glfw.terminate()
            return

        # MPV

        def __get_process_address(_, name):
            address = glfw.get_proc_address(name.decode("utf-8"))
            return ctypes.cast(address, ctypes.c_void_p).value

        self.__ctx = None
        self.__mpv = MpvPlayer()
        self.__proc_addr_wrapper = OpenGlCbGetProcAddrFn(__get_process_address)

        # GTK

        style: Gtk.StyleContext = self.get_style_context()
        style.add_class("video-area")

        self.add_events(Gdk.EventMask.POINTER_MOTION_MASK)
        self.add_events(Gdk.EventMask.BUTTON_PRESS_MASK)
        self.add_events(Gdk.EventMask.BUTTON_RELEASE_MASK)
        self.add_events(Gdk.EventMask.KEY_PRESS_MASK)
        self.add_events(Gdk.EventMask.STRUCTURE_MASK)
        self.add_events(Gdk.EventMask.SCROLL_MASK)

        self.connect("realize", self.__on_realize)
        self.connect("unrealize", self.__on_unrealize)
        self.connect("render", self.__render)

    @property
    def player(self):
        return self.__mpv

    @staticmethod
    def __error_cb(i, m):
        print(i, m)

    def __on_realize(self, *_):
        self.make_current()

        import glfw
        glfw.make_context_current(self.__gl_window)

        app_paths = get_app_paths()
        mpv = self._initialize_mpv(app_paths.dir_config, app_paths.dir_screenshots)
        self.__ctx = MpvRenderContext(mpv, 'opengl', opengl_init_params={'get_proc_address': self.__proc_addr_wrapper})
        self.__ctx.update_cb = self.__on_mpv_callback
        self.__mpv.initialize(mpv)
        _set_versioning_metadata(self.__mpv)

    def __on_unrealize(self, *_):
        import glfw
        glfw.terminate()
        self.__ctx.free()
        self.__mpv.terminate()

    def __render(self, *_):
        self._render(self.__ctx)

    def __on_mpv_callback(self):
        GLib.idle_add(self.__call_frame_ready, None, GLib.PRIORITY_HIGH)

    def __call_frame_ready(self, *args):
        if self.__ctx.update():
            self.queue_render()

    @abstractmethod
    def _initialize_mpv(self, dir_config, dir_screenshots) -> MPV:
        """
        Returns the MPV object perfectly initialized for the render container it will render into.
        """
        pass

    @abstractmethod
    def _render(self, mpv_render_context: MpvRenderContext) -> bool:
        """
        The ::render signal is emitted every time the contents of the GtkGLArea should be redrawn.

        The context is bound to the area prior to emitting this function,
        and the buffers are painted to the window once the emission terminates.

        Returns True to stop other handlers from being invoked for the event. FALSE to propagate the event further.
        """
        pass


class __LinuxContainerWayland(__RenderContainer):

    def _initialize_mpv(self, dir_config, dir_screenshots) -> MPV:
        return MPV(
            vo="libmpv",
            gpu_context="wayland",
            keep_open="yes",
            idle="yes",
            osc="yes",
            cursor_autohide="no",
            input_cursor="no",
            config="yes",
            input_default_bindings="no",
            config_dir=dir_config,
            screenshot_directory=dir_screenshots,
            log_handler=print
        )

    def _render(self, mpv_render_context: MpvRenderContext) -> bool:
        if mpv_render_context:
            factor = self.get_scale_factor()
            rect = self.get_allocated_size()[0]

            width = rect.width * factor
            height = rect.height * factor

            mpv_render_context.render(flip_y=True, opengl_fbo={'w': width, 'h': height, 'fbo': 2})
            return True
        return False


class __WindowsContainer(__RenderContainer):

    def _initialize_mpv(self, dir_config, dir_screenshots) -> MPV:
        return MPV(
            vo="libmpv",
            keep_open="yes",
            idle="yes",
            osc="yes",
            cursor_autohide="no",
            input_cursor="no",
            config="yes",
            input_default_bindings="no",
            config_dir=dir_config,
            screenshot_directory=dir_screenshots,
            log_handler=print
        )

    def _render(self, mpv_render_context: MpvRenderContext) -> bool:
        if mpv_render_context:
            factor = self.get_scale_factor()
            rect = self.get_allocated_size()[0]

            width = rect.width * factor
            height = rect.height * factor

            mpv_render_context.render(flip_y=True, opengl_fbo={'w': width, 'h': height, 'fbo': 1})
            return True
        return False


def get_mpv_widget(parent: Gtk.Widget) -> Gtk.Widget:
    """
    Returns a container holding the 'high level mpv player' object
    """

    import locale
    lc, enc = locale.getlocale(locale.LC_NUMERIC)
    # libmpv requires LC_NUMERIC to be set to "C". Since messing with global variables everyone else relies upon is
    # still better than segfaulting, we are setting LC_NUMERIC to "C".
    locale.setlocale(locale.LC_NUMERIC, 'C')

    plat = platform.system()

    if plat == "Linux":
        is_wayland = parent.get_display().get_name().lower().startswith("wayland")
        if is_wayland:
            return __LinuxContainerWayland()
        else:
            return __LinuxContainerX()
    elif plat == "Windows":
        return __WindowsContainer()
    else:
        raise RuntimeError("Platform '{}' not supported ".format(plat))


def _set_versioning_metadata(mpv):
    metadata = get_app_metadata()
    metadata.version_mpv = mpv.version_mpv()
    metadata.version_ffmpeg = mpv.version_ffmpeg()
