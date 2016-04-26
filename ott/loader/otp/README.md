loader:otp
==========

purpose: check the freshness of the OSM and GTFS data, and rebuild a new Graph.obj if new stuff exists
         The [./config/app.ini](../../../config/app.ini) file controls OTP, OSM data and GTFS files...

run: bin/otp_build_graph (optional: -ini <name>.ini | force_update)
