DIR=`dirname $0`
. $DIR/base-toggle.sh

DO_TOG=${1:-"NO_TOG"}

getMachineToToggle
isUp $TOG TRUE
echo
if [ $? == 0 ]; then
  echo "looks like $TOG is UP!"
  if [ $DO_TOG == "TOG" ]; then
    echo "Toggeling $LOAD_BALANCER"
    boltLbCmd "$FLIP" RM
  fi
else
  echo "doesn't appear that $TOG is running"
fi
