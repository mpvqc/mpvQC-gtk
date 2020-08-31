# Development

This guide assumes that all required dependencies mentioned in the `README.md` are installed.

## Recommended tools

* **Glade** for creating/editing `.ui` files
* **Text editor** or **IDE** for developing/running (recommendation: PyCharm)

## Developing

To make things easier some helper scripts exist that work on custom directories.
So the original mpvQC application on the system will not be touched.

**The following commands should be executed in the root directory of the repository and may require sudo.**

### Install development version
The following command installs the current code base into a custom directory
```shell script
./build-aux/local/dev-install.sh
```

### Run development version
After the development version is installed, it can be executed by
```shell script
./build-aux/local/dev-start.sh
```

**Note:** The `dev-start.sh` script contains a parameter which allows testing different translations.

### Uninstall development version
To uninstall the development version run
```shell script
./build-aux/local/dev-uninstall.sh
```

### Clean up all development files
```shell script
./build-aux/local/dev-clean.sh
```

## Workflow

1. Choose/create an issue and assign yourself. If there are people already assigned to the issue, please talk to them before adding yourself to the assignees.
2. Next create a branch and merge request for the issue.
3. Update your local project and switch to the new branch.
4. Make changes and commit/push them.
5. When the branch is ready for review, remove the WIP tag from the merge request.
6. Assign someone for the review.

# Translating

## Recommended tools:

* Poedit

### Contribute translations to the project

1. Choose/create an issue and assign yourself. If there are people already assigned to the issue, please talk to them before adding yourself to the assignees.
1. Copy an existing po file in the po directory and rename it to `<newlocale>`.po.
1. Delete all translated strings (but keep the file header).
1. Update the LINGUAS file in the po directory.
1. Open Poedit, select the `<newlocale>`.po file and hit 'Update from Source'.
1. Translate and save the file.
1. Review the translation: open `dev-start.sh` and adjust the *language* parameter
1. Create a new pull request with the new .po file.

# MISC

## Inspecting GTK Apps

Run the following in a terminal
```shell
gsettings set org.gtk.Settings.Debug enable-inspector-keybinding true
```
When the app is running now press `CTRL + SHIFT + D` to inspect the window.
