#!/bin/bash
# Meant to be executed from root directory
# Alternatively from the IDE run configuration

DIR_EXEC=".execdir"

#######################################################################################################################

_DIR=$(pwd)

_DIR_EXEC=$_DIR/$DIR_EXEC

if [ -d "$_DIR_EXEC" ]; then
  language=#"de_DE"
  LANGUAGE="$language" python "$_DIR_EXEC"/bin/mpvQC
else
  echo "Application is not installed yet"
  echo "Run './build-aux/local/dev-install.sh', then try again."
fi


