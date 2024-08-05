export JAVA_HOME=$HOME/jdk_21
export PATH="$JAVA_HOME/bin:.:/home/otp/install/mvn/bin:$PATH"
export JAVA_OPTS="-Xms2298m -Xmx4096m -server"

. ~/secrets

GRAPH=~/loader/ott/loader/otp/graph
CT=${1:-"$GRAPH/call-test/graph.obj"}
MOD=${2:-"$GRAPH/mod/Graph.obj"}
MOD_TIME=`stat -c %Y $MOD`
CT_TIME=`stat -c %Y $CT`
let CT_TIME=$CT_TIME+100 # add a few seconds to prevent same time causing rebuilt
if [ $CT_TIME -gt $MOD_TIME ]; then
  echo "NOT building $CT ($CT_TIME), as it's newer than $MOD ($MOD_TIME)"
  exit 1
else
  echo "BUILDING $CT ($CT_TIME), as it's older than $MOD ($MOD_TIME)"
fi

rm $CT $GRAPH/call-test/*.gtfs.zip
bin/gtfs_update
bin/otp_build call-test
bin/otp_v_new call-test
bin/otp_package_new call-test
bin/otp_export
touch $GRAPH/*/*obj*
