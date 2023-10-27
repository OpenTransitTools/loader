mac_psql=/Applications/Postgres.app/Contents/Versions/9.4/bin/psql
unix_psql=`which psql`

if [ -f "$mac_psql" ]
then
    psql=$mac_psql
elif [ -f "$unix_psql" ]
then
    psql=$unix_psql
fi

db_url=$1
def_db=${2:-postgres}

# IMPORTANT: there are are python configs for user, pass and db in loader/config/app.ini, which also need to change
user=ott
pass=ott
db=ott
osm_db=osm

# use URL if we get content on the cmd line (default to docker url when no ://)
if  [[ "$db_url" != "" ]] && [[ "$db_url" != *"://"* ]]; then
    db_url=postgres://docker:docker@localhost:5432/
fi
