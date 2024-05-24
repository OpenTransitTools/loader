DIR=`dirname $0`
. $DIR/servers.sh

# LB script settings
ECHO_SETTINGS=${1:-"FALSE"}
LOAD_BALANCER=${2:-"web_ws-trimet-org@rj-st-pubweb01"}

RTP_DIR=~/rtp/loader/ott/loader/otp/graph/rtp
LOG_FILE=/tmp/toggle.txt

# toggle script
TOGGLE_SCRIPT="~/scripts/blue-green_toggle"
FLIP="$TOGGLE_SCRIPT flip"
BLUE="$TOGGLE_SCRIPT blue"
GREEN="$TOGGLE_SCRIPT green"
STATUS="$TOGGLE_SCRIPT status"

#RUN_NEW="cd ~/rtp/loader; rm nohup.out; nohup bin/otp_restart_new_graphs &"
RUN_NEW="cd ~/rtp/loader; tmux; bin/otp_restart_new_graphs > out.txt 2>&1"
#RUN_RTP="cd ~/rtp/loader; tmux new-session -d -s my_session 'bin/otp_run -s rtp > out.txt 2>&1'"
RUN_RTP="cd ~/rtp/loader; tmux; bin/otp_run -s rtp > out.txt 2>&"1


function boltExe() {
  CMD=${1:-$STATUS}
  MACH=${2:-$LOAD_BALANCER}
  ECHO=${3:-$ECHO_SETTINGS}

  cmd="bolt command run \"$CMD\" --targets \"$MACH\" >> $LOG_FILE 2>&1"
  if [ $ECHO == "TRUE" ]; then
    echo $cmd
  fi
  eval $cmd

  if [ $ECHO == "TRUE" ]; then
    cat $LOG_FILE
  elif [ $ECHO == "RM" ]; then
    RM $LOG_FILE
  fi
}


function boltLbCmd() {
  CMD=${1:-$STATUS}
  ECHO=${3:-$ECHO_SETTINGS}
  MACH=${4:-$LOAD_BALANCER}

  if [ $2 ]; then
    rm -f $LOG_FILE
  fi

  for a in $ACCOUNTS
  do
    boltExe "$CMD $a" $MACH FALSE
  done

  if [ $ECHO == "TRUE" ]; then
    cat $LOG_FILE
  fi
}


#
# returns 1 if the MACH val is not found in the log file
# (e.g., grep returns 0 on success and 1 on fail)
#
function isBlue() {
  rm -f $LOG_FILE 
  boltLbCmd "$STATUS" RM "NO";
  if grep -q BLUE $LOG_FILE; then
    #echo "BLUE"
    retVal=1
  else
    #echo "GREEN"; cat $LOG_FILE
    retVal=0
  fi
  return $retVal
}


function isUp() {
  MACH=${1:-""}
  ECHO=${2:-$ECHO_SETTINGS}

  UP=/tmp/otpup
  rm -f $UP
  cmd="curl http://$MACH:52425/otp/routers > $UP 2>&1"
  eval $cmd
  if [ $ECHO == "TRUE" ]; then
    echo $cmd
    echo $UP
  fi

  grep TRANSIT $UP
}


function getMachineToToggle() {
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
}
