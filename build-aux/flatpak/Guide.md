# Building and installing mpvQC-gtk as Flatpak locally

**TODO:** This does not work on Wayland yet.  
**TODO:** Dependencies are outdated.

1. Ensure `flatpak` and `flatpak-builder` are installed
1. Clone the repository
1. From the project root run 
   ```shell
   flatpak-builder --force-clean build-dir build-aux/flatpak/com.github.mpvqc.mpvQC.yml
   ```
1. Then run
   ```shell
   flatpak-builder --user --install build-dir build-aux/flatpak/com.github.mpvqc.mpvQC.yml --force-clean
    ```
1. Start the application 
   ```shell
   flatpak run com.github.mpvqc.mpvQC
   ```
   
More information can be found [here](https://docs.flatpak.org/en/latest/first-build.html#).