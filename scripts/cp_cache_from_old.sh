CP=cp

## check target directory
if [ ! -d "./ott/loader/" ];
then
    echo "you need to run this script from the ~/loader top level directory"
    echo "you should see something when you run: ls ./ott/loader/"
    exit 1
fi

## check source directory
if [[ $1 = *"@"**":"* ]];
then
    CP=scp  
else 
    if [ ! -d "$1" ];
    then
	echo "directory '$1' does not exist or is not a directory"
	exit 1
    fi
fi


## copy junk over
for d in ott/loader/gtfs/cache ott/loader/osm/cache ott/loader/osm/osmosis ott/loader/otp/graph/call ott/loader/otp/graph/call-test ott/loader/otp/graph/prod ott/loader/otp/graph/test
do
    if [[ "$1/$d" = "./$d" ]];
    then
        echo "can't use the same directory for source and destination '$1/$d' = './$d'"
        exit 1
    fi

    if [[ $CP = "cp" && ! -d "$1/$d" ]];
    then
	echo "src directory '$1/$d' does not exist..."
        continue
    fi

    if [ -d "./$d" ];
    then
        echo rm -rf "./$d"
        rm -rf "./$d"
    fi

    echo $CP -r "$1/$d" "./$d"
    $CP -r "$1/$d" "./$d"
done
