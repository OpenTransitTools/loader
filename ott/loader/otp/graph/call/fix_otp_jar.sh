OTP_DIR=${OTP_DIR:="../OpenTripPlanner"}
OTP_JAR=${OTP_JAR:="$OTP_DIR/target/otp-*-shaded.jar"}

EXE_DIR=${EXE_DIR:="ott/loader/otp/graph/call"}
EXE_JAR=${EXE_JAR:="$EXE_DIR/otp.jar"}

##
## build OTP.jar and copy it to a given location
##
function build_jar()
{
    if [ ! -f $OTP_JAR ];
    then
        cd $OTP_DIR
        echo "BUILDING $OTP_JAR"
        mvn package -DskipTests
        cd -
    fi
    if [ -f $OTP_JAR ];
    then
        mv $EXE_JAR ${EXE_JAR}.old
        echo "cp $OTP_JAR $EXE_JAR"
        cp $OTP_JAR $EXE_JAR
    fi
}

##
## add the config.js file to our jar file
##
function fix_config_jar()
{
    if [ -f $EXT_JAR ];
    then
        echo "config and images to $EXE_JAR"
        cd $EXE_DIR
        jar uf otp.jar client/js/otp/config.js
        jar uf otp.jar client/images/agency_logo.png
        cd -
    fi
}

## build / copy .jar into place
build_jar
fix_config_jar

