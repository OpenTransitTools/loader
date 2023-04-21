. base.sh

FROM="from:{ lat: 45.5082, lon: -122.4289 }"
TO="to:{ lat: 45.5794, lon: -122.7097 }"
MODES="transportModes:[{mode:CAR, qualifier: HAIL}, {mode:TRANSIT}]"

graphql '{"query":
  "{ plan( '"$FROM"' '"$TO"' '"$MODES"' numItineraries: 1) {itineraries {duration legs { mode '"$GEOM"' rideHailingEstimate { provider { id } arrival minPrice{currency {code} amount} maxPrice{currency {code} amount} }}}}}"
}'
