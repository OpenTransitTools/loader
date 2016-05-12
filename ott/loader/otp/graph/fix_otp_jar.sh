OTP_DIR=${OTP_DIR:="../OpenTripPlanner"}
OTP_JAR=${OTP_JAR:="$OTP_DIR/target/otp-*-shaded.jar"}

EXE_DIR=${EXE_DIR:="ott/loader/otp/graph"}
EXE_JAR=${EXE_JAR:="$EXE_DIR/otp.jar"}

function build_jar()
{
    if [ ! -f $OTP_JAR ];
    then
        cd $OTP_DIR
        mvn package -DskipTests
        cd -
    fi
}

function config_jar()
{
    if [ ! -f $OTP_JAR ];
    then
        rm $EXE_JAR

        cd $EXE_DIR
        jar uf $WAR js/otp/config.js
        jar uf $WAR images/agency_logo.png
        cd -

    echo scp $WAR otp@$svr:~/archives/
    scp $WAR otp@$svr:~/archives/
}
