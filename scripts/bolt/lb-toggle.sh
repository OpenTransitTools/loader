DIR=`dirname $0`
. $DIR/base-toggle.sh

echo "Toggeling $LOAD_BALANCER"
bolt_cmd "$FLIP" RM
bolt_cmd
