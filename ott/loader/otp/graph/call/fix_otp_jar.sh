OTP_DIR=${OTP_DIR:="../OpenTripPlanner"}
OTP_JAR=${OTP_JAR:="$OTP_DIR/target/otp-*-shaded.jar"}

EXE_DIR=${EXE_DIR:="ott/loader/otp/graph"}
EXE_JAR=${EXE_JAR:="$EXE_DIR/otp.jar"}

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
        echo "cp $OTP_JAR $EXE_JAR"
        rm $EXE_JAR
        cp $OTP_JAR $EXE_JAR
    fi
}


##
## add the config.js file to our jar file
##
function call_config_jar()
{
    if [ -f $EXT_JAR ];
    then
        echo "ADD CALL config and images to $EXE_JAR"
        cd $EXE_DIR
        jar uf otp.jar client/js/otp/config.js
        jar uf otp.jar client/images/agency_logo.png
        cd -
    fi
}

## build / copy .jar into place
build_jar

## if "CALL", then add the config to the jar
if [[ $* == *"CALL"* ]]
then
    call_config_jar
fi
