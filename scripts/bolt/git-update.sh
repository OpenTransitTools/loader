DIR=`dirname $0`
. $DIR/base-toggle.sh

getMachineToToggle
echo "$CUR is the live server, so git update other server $SCP"
boltExe "update.sh" $TOG TRUE
