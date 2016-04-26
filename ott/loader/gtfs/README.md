loader:gtfs
===========

purpose: to download and cache GTFS .zip files from N number of providers. Compare tools are provided to then determine  
         whether a feed in a given cache is either the same or newer based on version stamps and calendar dates.
         The [./config/app.ini](../../../config/app.ini) file controls the list of gtfs feeds cached.

run: bin/gtfs_update (optional -ini <name>.ini | force_update)
