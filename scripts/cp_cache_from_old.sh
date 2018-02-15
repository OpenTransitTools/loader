## check source directory
if [ ! -d "$1" ];
then
   echo "directory '$1' does not exist or is not a directory"
   exit 1
fi

## check target directory
if [ ! -d "./ott/loader/" ];
then
   echo "you need to run this script from the ~/loader top level directory"
   echo "you should see something when you run: ls ./ott/loader/"
   exit 1
fi


## copy junk over
for d in ott/loader/gtfs/cache/ ott/loader/osm/cache/ ott/loader/otp/graph/call/ ott/loader/otp/graph/call-test/ ott/loader/otp/graph/prod/ ott/loader/otp/graph/test/
do
    if [ -d "$1/$d" ];
    then
        if [ -d "./$d" ];
        then
            rm -rf "./$d"
        fi
        cp -r "$1/$d" "./$d"
    else
       echo "can't find: $1/$d"
    fi
done
