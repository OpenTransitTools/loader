loader:gtfsdb
=============

purpose: check to see if the cached GTFS .zip files have been updated, and if so, load them into [gtfsdb](http://gtfsdb.com}.
         The [./config/app.ini](../../../config/app.ini) file controls the list of gtfs feeds cached, and the db details.

run: bin/gtfsdb_load (optional -ini <name>.ini | force_update)
