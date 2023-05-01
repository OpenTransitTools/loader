. base.sh
graphql '{"query":
  "{rentalVehicles {network vehicleId lat lon vehicleType{formFactor} }}",
  "variables":{}
}'
