loader:otp
==========

purpose: check the freshness of the OSM and GTFS data, and rebuild a new Graph.obj if new stuff exists
         The [./config/app.ini](../../../config/app.ini) file controls OTP, OSM data and GTFS files...

run: bin/otp_build_graph (optional: -ini <name>.ini | force_update)


grab new otp from build:
  1. cd OpenTripPlanner
  1. mvn package
  1. cd ../loader/
  1. rm ott/loader/otp/graph/cache/Graph.obj
  1. cp ../OpenTripPlanner/target/otp*shaded.jar ott/loader/otp/graph/otp.jar
  1. bin/otp_build_graph <low_mem>

