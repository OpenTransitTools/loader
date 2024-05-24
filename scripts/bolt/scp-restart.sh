DIR=`dirname $0`
. $DIR/base-toggle.sh


size=`ls -ltr $RTP_DIR/graph.obj-new | awk -F" " '{ print $5 }'`
if [[ $size -gt 200000000 ]]
then
  getMachineToToggle
  echo "$CUR is active, so scp new files to $SCP"
  boltExe "update.sh" $TOG RM  # git update first
  ls -l $RTP_DIR/*new $RTP_DIR/*json
  rm -f $LOG_FILE
  scp $RTP_DIR/*new $RTP_DIR/*json $SCP:$RTP_DIR/
  boltExe "$RUN_NEW" $TOG TRUE
  sleep 60

  isUp $TOG
  if [ $? == 0 ]; then
    echo "Toggeling $LOAD_BALANCER"
    boltLbCmd "$FLIP" RM
  else
    echo "Unsure $TOG is running, so not touching the $LOAD_BALANCER ($FLIP)"
  fi
else
  echo "doing nothing: $RTP_DIR/graph.obj-new looks small at $size bytes"
fi
