CACHE=~/rtp/cache
LOADR=~/rtp/loader
RTP=~/rtp/loader/ott/loader/otp/graph/rtp

echo "update gtfs"
rm $CACHE/*
cd $LOADR
bin/gtfs_update

echo "patch CTRAN"
cd $CACHE
cp OLD/CTRAN*zip .

cd $RTP
rm *.zip or-wa*
scp maps6:~/htdocs/pelias/or-wa.osm.pbf .

cd $LOADR
bin/otp_build rtp
bin/otp_package_new rtp
scripts/bolt/scp-restart.sh

cd $RTP
mv *new OLD/
