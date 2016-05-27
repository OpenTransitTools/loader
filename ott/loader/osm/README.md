loader:osm
==========

purpose: cached GTFS .zip files into [gtfsdb](http://gtfsdb.com}
         The [./config/app.ini](../../../config/app.ini) file controls the list of gtfs feeds cached.

run: bin/osm_update (optional: -ini <name>.ini | force_update)

build OSMOSIS:
  1. cd ott/loader/osm/osmosis
  1. install.sh
  1. cd -
