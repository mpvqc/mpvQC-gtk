# Meant to be executed from root directory
# Alternatively from the IDE run configuration

DIR_BUILD=".builddir"

#######################################################################################################################

_DIR=$(pwd)

_DIR_BUILD=$_DIR/$DIR_BUILD

if [ -d "$_DIR_BUILD" ]; then
  ninja -C "$_DIR_BUILD" uninstall
else
  echo "Build directory does not exist."
  echo "Skip uninstall."
fi


