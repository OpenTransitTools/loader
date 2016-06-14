#
# loader install
# will go from buildout to grabbing proper otp.jar files
# June 2016
#

# run buildout (and ignore .pydev)
buildout
git update-index --assume-unchanged .pydevproject

# install OSMOSIS (OpenStreetMap .pbf to .osm converter and db loader)
cd ott/loader/osm/osmosis/
./install.sh
cd -

# get OTP .jar file put into each folder
for x in ott/loader/otp/graph/*/install.sh
do 
  echo $x
  $x
done

