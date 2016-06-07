OTP_DIR=${OTP_DIR:="../OpenTripPlanner"}
OTP_JAR=${OTP_JAR:="$OTP_DIR/target/otp-*-shaded.jar"}

EXE_DIR=${EXE_DIR:="ott/loader/otp/graph/prod"}
EXE_JAR=${EXE_JAR:="$EXE_DIR/otp.jar"}

CFG_DIR=${CFG_DIR:="ott/loader/otp/graph/config"}
TILE_DIR=${TILE_DIR:="../ned-tiles/"}

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


##
## add the config.js file to our jar file
##
function misc()
{
    # cp config
    for x in build-config.json router-config.json
    do
        if [ ! -f $EXT_DIR/$x ];
        then
            cp $CFG_DIR/$x $EXE_DIR/
        fi
    done

    # cp cached tiles to ned dir
    if [ ! -f $TILE_DIR ];
    then
        mkdir $EXE_DIR/ned
        cp $TILE_DIR/* $EXE_DIR/ned/
    fi
}



## build / copy .jar into place
build_jar
fix_config_jar
misc
