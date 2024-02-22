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
RUN_NEW="cd ~/rtp/loader; rm nohup.out; nohup bin/otp_restart_new_graphs &"


function boltExe() {
  CMD=${1:-$STATUS}
  MACH=${2:-$LOAD_BALANCER}
  ECHO=${3:-$ECHO_SETTINGS}

  cmd="bolt command run \"$CMD\" --targets \"$MACH\" >> $LOG_FILE 2>&1"
  echo $cmd
  eval $cmd

  if [ $ECHO == "TRUE" ]; then
    cat $LOG_FILE
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
    retVal=1
  else
    retVal=0
  fi
  return $retVal
}
