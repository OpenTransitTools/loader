WEB_JAR=${WEB_JAR:="http://maven.conveyal.com.s3.amazonaws.com/org/opentripplanner/otp/0.20.0/otp-0.20.0-shaded.jar"}

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
## download pre-built release of OTP
##
function wget_jar()
{
    wget -O $EXE_JAR $WEB_JAR
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

    # make ned dir if doesn't exist
    if [ ! -f $EXE_DIR/ned/ ];
    then
        mkdir $EXE_DIR/ned/
    else
        # if ned does exist, remove .gtx projection files
        # (seen them screw up OTP build, so better to re-download them)
        rm -f $EXE_DIR/ned/*.gtx
    fi

    # cp cached tiles to ned dir
    if [ -f $TILE_DIR ];
    then
        cp $TILE_DIR/* $EXE_DIR/ned/
    fi
}
