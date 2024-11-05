#
# patch 
# changes the pelias/GTFS.zip to replace stops with departure stops
# November 2024
#
TM_ZIP=TRIMET.zip
STPS=stops.txt

cd ~/htdocs/pelias/
rm -f $STPS
curl https://developer.trimet.org/schedule/boarding_stops.txt > $STPS 

if [ -f "$STPS" ];
then
  rm -f $TM_ZIP
  cp /home/otp/loader/ott/loader/gtfs/cache/TRIMET.gtfs.zip $TM_ZIP
  zip $TM_ZIP $STPS
fi
