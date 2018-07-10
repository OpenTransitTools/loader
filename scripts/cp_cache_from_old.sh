#
# COPY cache and necessary binary stuff from one 'loader' instance to another
# EXAMPLE: scripts/cp_cache_from_old.sh ./ user@server:~/loader/
#

CP=cp
CP_PARAMS=-pr
FM=${1:-'./'}
TO=${2:-'./'}
echo $FM $TO


## check target directory
if [ ! -d "./ott/loader/" ];
then
    echo "you need to run this script from the ~/loader top level directory"
    echo "you should see something when you run: ls ./ott/loader/"
    exit 1
fi

## check source directory
if [[ $FM = *"@"*":"* || $TO = *"@"*":"* ]];
then
    CP=scp
    CP_PARAMS=-prq
fi

## copy junk over
for d in ott/loader/gtfs/cache ott/loader/gtfsdb/cache ott/loader/osm/cache ott/loader/osm/osmosis ott/loader/otp/graph/call ott/loader/otp/graph/call-test ott/loader/otp/graph/prod ott/loader/otp/graph/test
do
    if [[ "${FM}${d}" = "${TO}${d}" ]];
    then
        echo "can't use the same directory for source and destination ${FM}${d} = ${TO}${d}"
        exit 1
    fi

    # copy things to paraent directory, so we don't get cache/cache junk, etc...
    echo $CP $CP_PARAMS "${FM}${d}/." "${TO}${d}/"
    $CP $CP_PARAMS "${FM}${d}/." "${TO}${d}/"
done

# remove gtfs.zip junk
rm ott/loader/gtfs*/cache/*.txt

touch ott/loader/osm/cache/*.osm
sleep 1
touch ott/loader/otp/graph/*/*.osm
sleep 1
touch ott/loader/otp/graph/*/Graph.obj
