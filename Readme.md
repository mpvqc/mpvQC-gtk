<div align="center">
  <h1>mpvQC</h1>
  <img alt="Logo" src="https://avatars3.githubusercontent.com/u/47739558?s=200&v=4" width="128" height="128"/>
  <br/>
  <br/>
  <b>libmpv based application for the quick and easy creation of quality control reports of video files</b>
</div>

![screenshot](data/screenshots/mpvQC-1.png)

---

## Installation

Currently, this application runs on Linux only.

### Arch/Manjaro

Install the AUR package: [https://aur.archlinux.org/packages/mpvqc-gtk-git/](https://aur.archlinux.org/packages/mpvqc-gtk-git/)

### Other distributions

**Install**

<!-- 
### Flatpak

1. Download the flatpak file.
2. Install it either via software center or via cli:  
   `flatpak install com.github.mpvqc.mpvQC.flatpak`
3. The application should now be accessible via application menu.  
   Else running `flatpak run com.github.mpvqc.mpvQC` will start the application.
   
Running `flatpak remove com.github.mpvqc.mpvQC` will remove the software.

-->

* Make sure `python>=3.6` and `mpv>=0.29.0` are installed on the system
* Make sure build dependencies `meson` and `ninja` are installed
* Install dependencies `pip install -r requirements.txt`

In the root directory of the project run:

```shell script
meson . .builddir
ninja -C .builddir
ninja -C .builddir install
```

The application now pops up in the system search or can be executed via `mpvQC`.

**Uninstall**

```shell script
ninja -C .builddir uninstall
```

## Keybindings

Access the keyboard shortcut menu via menu or via shortcut `CTRL + F1`.  

## FAQ

* Are there plans for Windows Binaries?
  > No. While the application does run fine on Windows, the user experience didn't match our expectations.  
  > Please refer to the [default version](https://github.com/mpvqc/mpvQC).
* How can I contribute code to the project?
  > Please read the **development section** from the [contributing guide](CONTRIBUTING.md)  
  > Then create or select an issue or tackle one of the todos in the code
* How can I contribute translations to the project?
  > Please read the **translation section** from the [contributing guide](CONTRIBUTING.md)
