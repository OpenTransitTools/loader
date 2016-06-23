GRAPH_DIR=$(dirname "$0")
GRAPH_NAME=${GRAPH_DIR##*/}
. install-base.sh
build_jar
fix_config_jar
