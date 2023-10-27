##
## crete OTT spatial db for OTT
##
DIR=`dirname $0`
. $DIR/base.sh

## create user (default is user='ott' with pass='ott' -- change in ./base.sh)
$psql -d ${db_url}${def_db} -c "CREATE USER ${user} WITH PASSWORD '${pass}';"

# create ott and osm DBs
for d in $db $osm_db
do
  $psql -d ${db_url}${def_db} -c "CREATE DATABASE ${d} WITH OWNER ${user};"
  $psql -d ${db_url}${d} -c "CREATE EXTENSION postgis;"
done
