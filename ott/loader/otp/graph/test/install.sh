# name the GRAPH (based on directory name where this script is, ala 'prod'
GRAPH_DIR=$(dirname "$0")
GRAPH_NAME=${GRAPH_DIR##*/}

# src the lib file
. ott/loader/otp/graph/config/install-base.sh

## build / copy .jar into place
#build_jar
wget_jar
fix_config_jar
misc
