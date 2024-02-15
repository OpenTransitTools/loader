DIR=`dirname $0`
. $DIR/base-toggle.sh

isBlue
if [ $? == 1 ]; then
  echo BLUE
  echo "otp@cs-st-mapapp01"
else
  echo GREEN
  echo "otp@rj-st-mapapp01"
fi

if [ $ECHO_SETTINGS == "TRUE" ]; then
  boltLbCmd
fi
