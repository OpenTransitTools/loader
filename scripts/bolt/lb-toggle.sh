DIR=`dirname $0`
. $DIR/base-toggle.sh

echo "Toggeling $LOAD_BALANCER"
boltLbCmd "$FLIP" RM

if [ $ECHO_SETTINGS == "TRUE" ]; then
  boltLbCmd
fi
