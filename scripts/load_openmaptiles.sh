#!/bin/bash
set -o errexit
set -o pipefail
set -o nounset

osm_area=or-wa
testdata="${osm_area}.osm.pbf"

##  Min versions ...
MIN_COMPOSE_VER=1.7.1
MIN_DOCKER_VER=1.12.3
STARTTIME=$(date +%s)
STARTDATE=$(date +"%Y-%m-%dT%H:%M%z")
githash=$( git rev-parse HEAD )

# Options to run with docker and docker-compose - ensure the container is destroyed on exit,
# as well as pass any other common parameters.
# In the future this should use -u $(id -u "$USER"):$(id -g "$USER") instead of running docker as root.
DC_OPTS="--rm -u $(id -u "$USER"):$(id -g "$USER")"

log_file=./load_or_wa.log
rm -f $log_file

#####  backup log from here ...
exec &> >(tee -a "$log_file")

echo " "
echo "====================================================================================="
echo "                                Start processing                                     "
echo "-------------------------------------------------------------------------------------"
echo "====> : OpenMapTiles quickstart! [ https://github.com/openmaptiles/openmaptiles ]    "
echo "      : This will be logged to the $log_file file (for debugging) and to the screen"
echo "      : Area             : $osm_area "
echo "      : Git version      : $githash "
echo "      : Started          : $STARTDATE "
echo "      : Your bash version: $BASH_VERSION"
echo "      : Your OS          : $OSTYPE"
docker         --version
docker-compose --version

if [[ "$OSTYPE" == "linux-gnu" ]]; then
    echo " "
    echo "-------------------------------------------------------------------------------------"
    echo "      : This is working on x86_64 ; Your kernel is:"
    uname -r
    uname -m

    KERNEL_CPU_VER=$(uname -m)
    if [ "$KERNEL_CPU_VER" != "x86_64" ]; then
      echo "ERR: Sorry this is working only on x86_64!"
      exit 1
    fi
    echo "      : --- Memory, CPU info ---- "
    mem=$( grep MemTotal /proc/meminfo | awk '{print $2}' | xargs -I {} echo "scale=4; {}/1024^2" | bc  )
    echo "system memory (GB): ${mem}"
    grep SwapTotal /proc/meminfo
    echo "cpu number: $(grep -c processor /proc/cpuinfo) x $(cat /proc/cpuinfo | grep "bogomips" | head -1)"
    cat /proc/meminfo  | grep Free
else
    echo " "
    echo "Warning : Platforms other than Linux are less tested"
    echo " "
fi

echo " "
echo "-------------------------------------------------------------------------------------"
echo "====> : Stopping running services & removing old containers"
make clean-docker

echo " "
echo "-------------------------------------------------------------------------------------"
echo "====> : Checking OpenMapTiles docker images "
docker images | grep openmaptiles

echo " "
echo "-------------------------------------------------------------------------------------"
echo "====> : Create directories if they don't exist"
make init-dirs

echo " "
echo "-------------------------------------------------------------------------------------"
echo "====> : Removing old MBTILES if exists ( ./data/*.mbtiles ) "
rm -f ./data/*.mbtiles

if [ !  -f "./data/${testdata}" ]; then
    echo " "
    echo "Missing ./data/$testdata , Download or Parameter error? "
    exit 1
fi

make clean
echo "====> : Code generating from the layer definitions ( ./build/mapping.yaml; ./build/tileset.sql )"
echo "      : The tool source code: https://github.com/openmaptiles/openmaptiles-tools "
echo "      : But we generate the tm2source, Imposm mappings and SQL functions from the layer definitions! "
make
make db-start
make forced-clean-sql
make import-water
make import-natural-earth
make import-lakelines
make import-osm
make import-borders

echo " "
echo "-------------------------------------------------------------------------------------"
echo "====> : Start SQL postprocessing:  ./build/tileset.sql -> PostgreSQL "
echo "      : Source code: https://github.com/openmaptiles/openmaptiles-tools/blob/master/bin/import-sql"
# If the output contains a WARNING, stop further processing
# Adapted from https://unix.stackexchange.com/questions/307562
make import-sql | \
    awk -v s=": WARNING:" '$0~s{print; print "\n*** WARNING detected, aborting"; exit(1)} 1'

make psql-analyze
make import-wikidata
echo "====> : Testing PostgreSQL tables to match layer definitions metadata"
docker-compose run $DC_OPTS openmaptiles-tools test-perf openmaptiles.yaml --test null --no-color

echo "====> : Start generating MBTiles (containing gzipped MVT PBF) from a TM2Source project. "
#make generate-tiles

echo " "
echo "-------------------------------------------------------------------------------------"
echo "====> : Stop PostgreSQL service ( but we keep PostgreSQL data volume for debugging )"
make db-stop

echo " "
echo "-------------------------------------------------------------------------------------"
echo "====> : Inputs - Outputs md5sum for debugging "
rm -f ./data/quickstart_checklist.chk
md5sum build/mapping.yaml                     >> ./data/quickstart_checklist.chk
md5sum build/tileset.sql                      >> ./data/quickstart_checklist.chk
md5sum build/openmaptiles.tm2source/data.yml  >> ./data/quickstart_checklist.chk
md5sum "./data/${testdata}"                   >> ./data/quickstart_checklist.chk
md5sum ./data/tiles.mbtiles                   >> ./data/quickstart_checklist.chk
md5sum ./data/docker-compose-config.yml       >> ./data/quickstart_checklist.chk
md5sum ./data/osmstat.txt                     >> ./data/quickstart_checklist.chk
cat ./data/quickstart_checklist.chk

ENDTIME=$(date +%s)
ENDDATE=$(date +"%Y-%m-%dT%H:%M%z")
if stat --help >/dev/null 2>&1; then
  MODDATE=$(stat -c %y "./data/${testdata}" )
else
  MODDATE=$(stat -f%Sm -t '%F %T %z' "./data/${testdata}" )
fi

docker images | grep openmaptiles
ls -la ./data/*.mbtiles

echo "*  Use   make start-postserve    to explore tile generation on request"
echo "*  Use   make start-tileserver   to view pre-generated tiles"
make help

make start-postserve
