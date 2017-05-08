#
# loader install
#
# preps each graph directory by adding config stuff to otp.jar, as well as
# (possibly) copying cached data (like NED tiles)
#
# June 2016 - created
# May 2017 - update link to otp.jar and also grab otp.v from other server if new install
#

WEB_JAR=${WEB_JAR:="https://repo1.maven.org/maven2/org/opentripplanner/otp/1.1.0/otp-1.1.0-shaded.jar"}

OTP_DIR=${OTP_DIR:="../OpenTripPlanner"}
OTP_JAR=${OTP_JAR:="$OTP_DIR/target/otp-*-shaded.jar"}

EXE_DIR=${EXE_DIR:="ott/loader/otp/graph/$GRAPH_NAME"}
EXE_JAR=${EXE_JAR:="$EXE_DIR/otp.jar"}
CACHE_JAR=${CACHE_JAR:="../cache/otp.jar"}

CFG_DIR=${CFG_DIR:="ott/loader/otp/graph/config"}
TILE_DIR=${TILE_DIR:="../cache/ned/"}

PROD_SVR=${PROD_SVR:="maps8"}

link=false
if [[ $1 == "link" ]]; then
  link=true
fi

##
## grap otp.v from production server, so we don't lose that content with new otp.v file
##
function wget_otpv()
{
    echo scp $PROD_SVR:~/loader/$GRAPH_DIR/otp.v ./$GRAPH_DIR/otp.v
    scp $PROD_SVR:~/loader/$GRAPH_DIR/otp.v ./$GRAPH_DIR/otp.v
}

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
    if [ -f $EXE_JAR ];
    then
        echo "$EXE_JAR exists, so I'm not going to copy/wget a cached version"
        return
    fi

    if [ ! -f $CACHE_JAR ];
    then
        wget -O $EXE_JAR $WEB_JAR
    else
        cp $CACHE_JAR $EXE_JAR
    fi
}

##
## add the config.js file to our jar file
##
# test
function fix_config_jar()
{
    if [ -f $EXT_JAR ];
    then
        if [ ! -f $EXE_DIR/logback.xml ];
        then
            cp $CFG_DIR/logback.xml $EXE_DIR
        fi

        echo "config and images inserted into $EXE_JAR"
        cd $EXE_DIR
        jar uf otp.jar logback.xml
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
    echo "misc..."

    # cp config
    for x in build-config.json router-config.json
    do
        if [ ! -f $EXT_DIR/$x ];
        then
            cp $CFG_DIR/$x $EXE_DIR/
        fi
    done

    # make ned dir if doesn't exist
    if [ ! -d $EXE_DIR/ned/ ];
    then
        mkdir $EXE_DIR/ned/
    else
        # if ned does exist, remove .gtx projection files
        # (seen them screw up OTP build, so better to re-download them)
        rm -f $EXE_DIR/ned/*.gtx
    fi

    # cp cached tiles to ned dir
    if [ -d $TILE_DIR ] && [ ! -f $EXE_DIR/ned/n46w123.tiff ];
    then
        if "$link"; then
            cd $TILE_DIR
            DIR=$PWD
            cd -
            echo "ln -s $DIR/* $EXE_DIR/ned/"
            ln -s $DIR/* $EXE_DIR/ned/
        else
            echo "copying $TILE_DIR/* $EXE_DIR/ned/"
            cp $TILE_DIR/* $EXE_DIR/ned/
        fi
    fi
}

# BELOW is for TESTING...
#function misc()  {
#function build_jar() { echo "TEST fix jar" }
#function wget_jar()  { echo "TEST wget jar" }
#function fix_config_jar() { echo "TEST fix jar" }

