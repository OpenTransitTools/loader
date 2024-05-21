DIR=`dirname $0`
. $DIR/base-toggle.sh

isBlue
if [ $? == 1 ]; then
  CUR="BLUE ($BLUE_STAG)"
  TOG=$GREEN_STAG
else
  CUR="GREEN ($GREEN_STAG)"
  TOG=$BLUE_STAG
fi

boltExe "update.sh" $TOG TRUE
