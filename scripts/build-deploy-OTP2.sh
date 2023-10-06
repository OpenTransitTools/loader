. ~/secrets
export JAVA_HOME=$HOME/jdk_17
export PATH="$JAVA_HOME/bin:.:/home/otp/install/mvn/bin:$PATH"
export JAVA_OPTS="-Xms2298m -Xmx4096m -server"

rm ott/loader/otp/graph/call-test/graph.obj
bin/otp_build -d call-test
bin/otp_package_new call-test
bin/otp_export -svr maps8

touch ~/l*/o*/l*/o*/g*/*/*obj*
