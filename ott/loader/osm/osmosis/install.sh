cp ~/cache/osmosis*.tgz osmosis-latest.tgz
if [ ! -f "osmosis-latest.tgz" ];
then
    wget http://bretth.dev.openstreetmap.org/osmosis-build/osmosis-latest.tgz
fi
tar xvfz osmosis-latest.tgz
chmod a+x bin/osmosis
chmod a+x bin/osmosis.bat
bin/osmosis
