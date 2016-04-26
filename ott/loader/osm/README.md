loader:osm
==========

purpose: cached GTFS .zip files into [gtfsdb](http://gtfsdb.com}
         The [./config/app.ini](../../../config/app.ini) file controls the list of gtfs feeds cached.

run: bin/osm_update (optional: -ini <name>.ini | force_update)