# Meant to be executed from root directory
# Alternatively from the IDE run configuration

DIR_BUILD=".builddir"
DIR_EXEC=".execdir"

#######################################################################################################################

_DIR=$(pwd)

_DIR_BUILD=$_DIR/$DIR_BUILD
_DIR_EXEC=$_DIR/$DIR_EXEC

meson setup "$_DIR_BUILD"
meson --prefix "$_DIR_EXEC" "$_DIR_BUILD" --reconfigure
ninja -C "$_DIR_BUILD"
ninja -C "$_DIR_BUILD" install
