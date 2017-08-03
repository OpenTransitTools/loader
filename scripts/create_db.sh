##
## crete OTT spatial db for OTT
##

mac_psql = "/Applications/Postgres.app/Contents/Versions/9.4/bin/psql"
psql = $mac_psql
user = ott
db = ott

$psql -c "CREATE USER ${user};"
$psql -c "CREATE DATABASE ${db} WITH OWNER ${user};"
$psql -d $db -c "CREATE EXTENSION postgis;"



