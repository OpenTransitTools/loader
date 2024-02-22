DIR=`dirname $0`
. $DIR/base-toggle.sh

isBlue
if [ $? == 1 ]; then
  CUR=BLUE
  TOG=$GREEN_STAG
  SCP=$USER@$GREEN_STAG
else
  CUR=GREEN
  TOG=$BLUE_STAG
  SCP=$USER@$BLUE_STAG
fi

echo $CUR is active, so update $SCP
ls -l $RTP_DIR/*new $RTP_DIR/*json
scp $RTP_DIR/*new $RTP_DIR/*json $SCP:$RTP_DIR/
rm -f $LOG_FILE
boltExe "$RUN_NEW" $TOG TRUE
