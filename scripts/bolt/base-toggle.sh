# LB script settings
ACCOUNTS=${1:-"rtp"}
ECHO_SETTINGS=${2:-"FALSE"}
LOAD_BALANCER=${3:-"web_ws-trimet-org@rj-st-pubweb01"}

LOG_FILE=/tmp/toggle.txt

# toggle script
TOGGLE_SCRIPT="~/scripts/blue-green_toggle"
FLIP="$TOGGLE_SCRIPT flip"
BLUE="$TOGGLE_SCRIPT blue"
GREEN="$TOGGLE_SCRIPT green"
STATUS="$TOGGLE_SCRIPT status"


function boltCmd() {
  CMD=${1:-$STATUS}
  ECHO=${3:-$ECHO_SETTINGS}

  if [ $2 ]; then
    rm -f $LOG_FILE > /dev/null 2>&1
  fi

  for a in $ACCOUNTS
  do
    bolt command run "$CMD $a" --targets $LOAD_BALANCER >> $LOG_FILE 2>&1
  done

  if [ $ECHO == "TRUE" ]; then
    cat $LOG_FILE
  fi
}


function isBlue() {
  # returns 1 if the MACH val is not found in the log file
  # (e.g., grep returns 0 on success and 1 on fail)
  MACH=${1:-"GREEN"}

  boltCmd "$STATUS" RM "NO";
  GREP=`grep $MACH $LOG_FILE`;
  return $?
}
