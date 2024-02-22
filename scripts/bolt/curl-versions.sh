DIR=`dirname $0`
. $DIR/base-toggle.sh


function showMachines() {
  for m in $*
  do 
    cmd="curl $m:52425/otp"
    echo $cmd
    eval $cmd
    echo
    echo
  done
}


isBlue
if [ $? == 1 ]; then
  CUR=BLUE
  MACH="$BLUE_STAG"
  OTHER="$GREEN_STAG"
else
  CUR=GREEN
  MACH="$GREEN_STAG"
  OTHER="$BLUE_STAG"
fi


echo
echo $CUR is active:
echo
showMachines $MACH

echo
echo "OTHER MACHINES:"
echo
showMachines $OTHER
echo
