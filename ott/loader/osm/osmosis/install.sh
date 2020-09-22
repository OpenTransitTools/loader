DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )";
cd $DIR
echo "I'm in $PWD"

# OSMOSIS download as of (Sept) 2020:
#   https://github.com/openstreetmap/osmosis/releases/download/0.48.3/osmosis-0.48.3.tgz
URL=https://github.com/openstreetmap/osmosis/releases/download
VER=0.48.3
EXT=tgz
FILE=osmosis-$VER.$EXT

if [ ! -f $FILE ];
then
    echo "PLEAZZE CHEEEECK LATEST VERSION (currently using version $VER):"
    echo "https://github.com/openstreetmap/osmosis/releases/latest/"
    echo
    curl -L $URL/$VER/$FILE > $FILE
fi
tar xvfz $FILE
chmod a+x bin/osmosis
chmod a+x bin/osmosis.bat
bin/osmosis
