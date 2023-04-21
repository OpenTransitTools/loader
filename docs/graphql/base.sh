#
# 
# params
#
MAPS=${1:-"maps7"}
SVR=${2:-"ct"}
GEOM=${3:-"legGeometry{points}"}

GQL_URL=http://${MAPS}.trimet.org/otp_${SVR}/index/graphql


function graphql()
{
  Q=$1
  echo $Q
  echo $GQL_URL
  echo
  curl "$GQL_URL" -H 'Content-Type: application/json' --data "$Q"
  echo
}
