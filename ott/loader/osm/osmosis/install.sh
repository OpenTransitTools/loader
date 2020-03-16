DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )";
FILE="osmosis-latest.tgz"

cd $DIR
echo "I'm in $PWD"

cp ~/cache/osmosis*.tgz $FILE
if [ ! -f $FILE ];
then
    curl https://bretth.dev.openstreetmap.org/osmosis-build/osmosis-latest.tgz > $FILE
fi
tar xvfz $FILE
chmod a+x bin/osmosis
chmod a+x bin/osmosis.bat
bin/osmosis
