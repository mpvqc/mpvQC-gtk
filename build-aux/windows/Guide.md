# Getting mpvQC-gtk to work on Windows

<!-- https://www.gtk.org/docs/installations/windows#using-gtk-from-msys2-packages -->

1. Install *MSYS2* from [here](https://www.msys2.org/)
1. Install the following packages
    ```
    base
    git
    meson
    mingw-w64-x86_64-appstream-glib
    mingw-w64-x86_64-desktop-file-utils
    mingw-w64-x86_64-ftgl
    mingw-w64-x86_64-gtk3
    mingw-w64-x86_64-meson
    mingw-w64-x86_64-mpv
    mingw-w64-x86_64-pkg-config
    mingw-w64-x86_64-python-gobject
    mingw-w64-x86_64-glfw
    ```
1. Clone mpvQC-gtk into `C:\msys64\home\<your username>` and `cd` into it

### Install
```
meson . build
ninja -C build
ninja -C build install
```

### Uninstall
```
ninja -C build uninstall
rm -rf build || true
```
