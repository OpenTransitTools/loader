. base.sh
graphql '
{
  plan(  
    from: {lat: 45.508271755944975, lon: -122.4288940}
    to: {lat: 45.579445114, lon: -122.7097320556}
    transportModes: [{mode: CAR, qualifier: HAIL}, {mode: TRANSIT}]
    numItineraries: 1
    carReluctance: 4
  ) {
    itineraries {
      duration
      legs {
        mode
        legGeometry {
          points
        }
        rideHailingEstimate {
          provider {
            id
          }
          arrival
          minPrice {
            currency {
              code
            }
            amount
          }
          maxPrice {
            currency {
              code
            }
            amount
          }
        }
      }
    }
  }"
}
'
