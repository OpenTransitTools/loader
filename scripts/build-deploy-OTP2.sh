export JAVA_HOME=$HOME/jdk_21
export PATH="$JAVA_HOME/bin:.:/home/otp/install/mvn/bin:$PATH"
export JAVA_OPTS="-Xms2298m -Xmx4096m -server"

. ~/secrets

GRAPH=~/loader/ott/loader/otp/graph
CT=${1:-"$GRAPH/call-test/graph.obj"}
MOD=${2:-"$GRAPH/mod/Graph.obj"}
CT_TIME=`stat -c %Y $CT`
MOD_TIME=`stat -c %Y $MOD`
if [ $CT_TIME -gt $MOD_TIME ]; then
  echo "NOT building $CT ($CT_TIME), as it's newer than $MOD ($MOD_TIME)"
  exit 1
else
  echo "BUILDING $CT ($CT_TIME), as it's older than $MOD ($MOD_TIME)"
fi

rm $CT
bin/otp_build -d call-test
bin/otp_v_new call-test
bin/otp_package_new call-test
bin/otp_export

touch $GRAPH/*/*obj*
sleep 5
touch $CT
