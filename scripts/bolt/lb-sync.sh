DIR=`dirname $0`
. $DIR/base-toggle.sh

isBlue
if [ $? == 1 ]; then
  echo BLUE
else
  echo GREEN
fi
