DIR=`dirname $0`
. $DIR/base-toggle.sh

isBlue
if [ $? == 1 ]; then
  CUR=BLUE
  TOG=$GREEN
  SCP=$USER@$GREEN_STAG
else
  CUR=GREEN
  TOG=$BLUE
  SCP=$USER@$BLUE_STAG
fi

echo $CUR is active, so update $SCP

RTP_DIR=~/rtp/loader/ott/loader/otp/graph/rtp
ls $RTP_DIR/*new $RTP_DIR/*json
scp $RTP_DIR/*new $RTP_DIR/*json $SCP:$RTP_DIR/
