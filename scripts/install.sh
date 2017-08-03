#
# loader install
# will go from buildout to grabbing proper otp.jar files
# April 2017
#

link=false
if [[ $1 == "link" ]]; then
  link=true
fi

# run buildout (and ignore .pydev)
buildout
git update-index --assume-unchanged .pydevproject

# install OSMOSIS if necessary
# OSMOSIS is the OpenStreetMap .pbf to .osm converter and db loader
if [ ! -f "ott/loader/osm/osmosis/bin/osmosis" ];
then
    cd ott/loader/osm/osmosis/
    ./install.sh
    cd -
fi

# get a leg up on the load by copying a cache'd OSM .pbf into place
if [ -d "../cache/osm/" ]
then
    # first make sure .osm is 'newer' than any *.pbf files
    touch ../cache/osm/*.*
    sleep 5
    touch ../cache/osm/*.osm

    mkdir ott/loader/osm/cache


    if "$link"; then
        cd ../cache/osm/
        DIR=$PWD
        cd -
        ln -s $DIR/*.* ott/loader/osm/cache/
    else
        cp ../cache/osm/*.* ott/loader/osm/cache/
        sleep 5
        touch ott/loader/osm/cache/*.osm
    fi
fi

# remove OpenTripPlanner target directory and git pull latest code (in case we have to build)
if [ -d "../OpenTripPlanner/" ]
then
    cd ../OpenTripPlanner/
    rm -rf ./target
    git pull
    cd -
fi

# get OTP .jar file put into each folder
for x in ott/loader/otp/graph/*/install.sh
do
    echo $x $*
    $x $*
done

# FINALLY ... run the load all script to execute the loader for the first time...
nohup bin/load_and_export > ./load_and_export.log 2>&1 &
