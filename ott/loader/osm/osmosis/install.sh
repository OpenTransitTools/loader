rm osmosis-latest.tgz
wget http://bretth.dev.openstreetmap.org/osmosis-build/osmosis-latest.tgz
tar xvfz osmosis-latest.tgz
chmod a+x bin/osmosis
chmod a+x bin/osmosis.bat
bin/osmosis
