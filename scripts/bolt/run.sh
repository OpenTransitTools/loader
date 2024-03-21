DIR=`dirname $0`
. $DIR/base-toggle.sh

isBlue
if [ $? == 1 ]; then
  CUR="BLUE ($BLUE_STAG)"
  TOG=$GREEN_STAG
  SCP=$USER@$GREEN_STAG
else
  CUR="GREEN ($GREEN_STAG)"
  TOG=$BLUE_STAG
  SCP=$USER@$BLUE_STAG
fi

echo $CUR is active, so update $SCP
boltExe "$RUN_RTP" $TOG TRUE
