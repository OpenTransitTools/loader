loader:gtfsdb
=============

purpose: check to see if the cached GTFS .zip files have been updated, and if so, load them into [gtfsdb](http://gtfsdb.com}.
         The [./config/app.ini](../../../config/app.ini) file controls the list of gtfs feeds cached, and the db details.

run: bin/gtfsdb_load (optional -ini <name>.ini | force_update)

PostGIS database:
     http://postgis.net/docs/postgis_installation.html#create_new_db_extensions
     createdb ott
     createuser ott
     psql  -d ott -c "CREATE EXTENSION postgis;"

     MAC:
       /Applications/Postgres.app/Contents/Versions/9.4/bin/createdb ott
       /Applications/Postgres.app/Contents/Versions/9.4/bin/createuser ott
       /Applications/Postgres.app/Contents/Versions/9.4/bin/psql  -d ott -c "CREATE EXTENSION postgis;"

