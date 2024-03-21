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


size=`ls -ltr $RTP_DIR/graph.obj-new | awk -F" " '{ print $5 }'`
if [[ $size -gt 200000000 ]]
then
  echo $CUR is active, so update $SCP
  ls -l $RTP_DIR/*new $RTP_DIR/*json
  scp $RTP_DIR/*new $RTP_DIR/*json $SCP:$RTP_DIR/
  rm -f $LOG_FILE
  boltExe "$RUN_NEW" $TOG TRUE
  sleep 60

  isUp $TOG
  if [ $? == 0 ]; then
    echo "Toggeling $LOAD_BALANCER"
    boltLbCmd "$FLIP" RM
  fi
fi
