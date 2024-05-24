DIR=`dirname $0`
. $DIR/base-toggle.sh

getMachineToToggle
echo "$CUR is the live server, so run/restart rtp on other server $SCP"
boltExe "update.sh" $TOG RM  # git update first
boltExe "$RUN_RTP" $TOG TRUE
echo "Check that $TOG is now running, and then manually hit the lb $LOAD_BALANCER ($FLIP)"
