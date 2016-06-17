#
# loader install
# will go from buildout to grabbing proper otp.jar files
# June 2016
#

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
mkdir ott/loader/osm/cache/
cp ../cache/osm/*.* ott/loader/osm/cache/
sleep 5
touch ott/loader/osm/cache/*.osm

# remove OpenTripPlanner target directory and git pull latest code
cd ../OpenTripPlanner/
rm -rf ./target
git pull
cd -

# get OTP .jar file put into each folder
for x in ott/loader/otp/graph/*/install.sh
do
    echo $x
    $x
done

# FINALLY ... run the load all script to execute the loader for the first time...
bin/load_all
