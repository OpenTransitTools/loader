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
        cp $OTP_JAR $EXE_JAR

        cd $EXE_DIR
        jar uf otp.jar client/js/otp/config.js
        jar uf otp.jar images/agency_logo.png
        cd -
    fi
}

build_jar
config_jar

