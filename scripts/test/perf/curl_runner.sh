#SECONDS=0
for f in {1..10}
do
  curl_bike_transit.sh &
  curl_short_trip.sh &
  curl_airport_zoo.sh &
  sleep 1
  echo
  echo RUN: $f
  echo
done
wait

echo
echo
#echo run of $f curls took $SECONDS seconds
echo
