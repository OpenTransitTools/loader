CACHE=~/rtp/cache
LOADR=~/rtp/loader
RTP=~/rtp/loader/ott/loader/otp/graph/rtp

UP_GTFS=${1:-"NOPE"}
if [ $UP_GTFS == GTFS ]; then
  echo "update gtfs"
  rm $CACHE/*
  cd $LOADR
  bin/gtfs_update

  cd $CACHE

  echo "patch CTRAN"
  cp OLD/CTRAN*zip .

  echo "patch SMART"
  cp OLD/SMART*zip .
fi


cd $RTP
rm *.zip or-wa*
scp maps6:~/htdocs/pelias/or-wa.osm.pbf .

cd $LOADR
bin/otp_build rtp
bin/otp_package_new rtp
scripts/bolt/scp-restart.sh

cd $RTP
mv *new OLD/
