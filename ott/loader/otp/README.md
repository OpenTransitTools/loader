loader:otp
==========

purpose: check the freshness of the OSM and GTFS data, and rebuild a new Graph.obj if new stuff exists
         The [./config/app.ini](../../../config/app.ini) file controls OTP, OSM data and GTFS files...

run: bin/otp_build_graph (optional: -ini <name>.ini | force_update | low_mem)

grab new otp from build:
  1. cd ../loader/
  1. ott/loader/otp/graph/call/install.sh 
  1. ott/loader/otp/graph/prod/install.sh


run test suites:
  1. bin/otp_preflight -hn maps8.trimet.org -p 80 -ws /prod -ts Otp
