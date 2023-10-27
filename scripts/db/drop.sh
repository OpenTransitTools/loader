##
## drop OTT database
##
DIR=`dirname $0`
. $DIR/base.sh

$psql -d ${db_url}${def_db} -c "DROP DATABASE ${db};"
$psql -d ${db_url}${def_db} -c "DROP DATABASE ${osm_db};"
$psql -d ${db_url}${def_db} -c "DROP USER ${user};"
