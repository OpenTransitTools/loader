CACHE=~/rtp/cache
LOADR=~/rtp/loader
TMP=~/rtp/loader/ott/loader/gtfs*/tmp
RTP=~/rtp/loader/ott/loader/otp/graph/rtp

UP_GTFS=${1:-"NOPE"}
if [ $UP_GTFS == GTFS ]; then
  echo "update gtfs"
  rm -f $CACHE/*
  rm -f $RTP/*gtfs.zip
  rm -rf $TMP

  cd $LOADR
  bin/gtfs_update

  cd $CACHE

  echo "patch CTRAN"
  cp OLD/CTRAN*zip .

  scp *gtfs.zip geoserver@rj-dv-mapapp01:~/gtfs/cache/
fi


cd $RTP
mkdir -p OLD
mv *.zip or-wa* *new ./OLD/
scp maps6:~/htdocs/pelias/or-wa.osm.pbf .

cd $LOADR
rm -f $RTP/graph.obj*
bin/otp_build rtp
bin/otp_package_new rtp

cd $RTP
jar uf otp.jar client
cp otp.jar otp.jar-new

cd $LOADR
scripts/bolt/scp-restart.sh

cd $RTP
mv *new OLD/
