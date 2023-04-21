. base.sh

FROM="from:{ lat: 45.55, lon: -122.55 }"
TO="to:{ lat: 45.56, lon: -122.60 }"
MODES="transportModes:[{ mode: TRANSIT }]"
GEOM=""

graphql '{"query":
  "{ plan( '"$FROM"' '"$TO"' '"$MODES"' numItineraries: 3) {itineraries {duration legs { mode '"$GEOM"' }}}}"
}'
