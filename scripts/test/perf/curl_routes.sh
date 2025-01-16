s=${1:-"60"}
m=${2:-"https://maps.trimet.org"}
p=${3:-"/rtp/gtfs/v1"}
#echo "curl $m$p - $s seconds timeout"

# trip date & time: 2024-09-27 10:53
d=`date +"%Y-%m-%d"`
t=`date +"%H:%M"`
# echo $d $t; exit

curl -m $s "$m$p" \
  -H 'Content-Type: application/json' \
  --compressed \
  --data $'{"query":"query GtfsExampleQuery{ routes{shortName gtfsId} }"}'
