loader:gtfs-rt
==============


**purpose**: 
 load [GTFS Realtime](https://developers.google.com/transit/gtfs-realtime/reference/) data into tables alongside a companion
 [gtfsdb](http://gtfsdb.com} database.

**run**: bin/gtfs_realtime_load (optional -ini <name>.ini)

**Note**: the config is set up for a PostGIS geo database, where gtfsdb will create route and stop geometry columns
      http://postgis.net/docs/postgis_installation.html#create_new_db_extensions
      run scripts/create_db.sh to create a PostGIS db called 'ott' with db user 'ott' 
