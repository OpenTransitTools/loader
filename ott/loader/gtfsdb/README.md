loader:gtfsdb
=============

purpose: check to see if the cached GTFS .zip files have been updated, and if so, load them into [gtfsdb](http://gtfsdb.com}.
         The [./config/app.ini](../../../config/app.ini) file controls the list of gtfs feeds cached, and the db details.

run: bin/gtfsdb_load (optional -ini <name>.ini | force_update)

Note: the config is set up for a PostGIS geo database, where gtfsdb will create route and stop geometry columns
      http://postgis.net/docs/postgis_installation.html#create_new_db_extensions
      run this to create the db: 
        psql -f ott/loader/gtfsdb/create_postgis_db.psql
        /Applications/Postgres.app/Contents/Versions/9.4/bin/psql -f ott/loader/gtfsdb/create_postgis_db.psql # MACOS
