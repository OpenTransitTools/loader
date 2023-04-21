GQL_URL=http://maps7.trimet.org/otp_ct/index/graphql
GEOM="legGeometry{points}"

function graphql()
{
  Q=$1
  echo $Q
  echo
  curl "$GQL_URL" -H 'Content-Type: application/json' --data "$Q"
  echo
}
