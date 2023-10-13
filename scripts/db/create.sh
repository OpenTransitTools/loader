##
## crete OTT spatial db for OTT
##
DIR=`dirname $0`
. $DIR/base.sh

for d in $db $osm_db
do
  $psql -d ${db_url}${def_db} -c "CREATE USER ${user};"
  $psql -d ${db_url}${def_db} -c "CREATE DATABASE ${d} WITH OWNER ${user};"
  $psql -d ${db_url}${d} -c "CREATE EXTENSION postgis;"
done
