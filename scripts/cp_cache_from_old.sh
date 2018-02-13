if [ ! -d "$1" ];
then
   echo "directory '$1' does not exist or is not a directory"
   exit 1
fi



for d in "gtfs/cache/ osm/cache/ otp/graph/call/ otp/graph/call-test/ otp/graph/prod/ otp/graph/test/"
do
    echo $d
    if [ ! -f "ott/loader/osm/osmosis/bin/osmosis" ];
    then
       echo $d
    fi
done
