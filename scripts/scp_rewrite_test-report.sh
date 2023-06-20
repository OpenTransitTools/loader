path=${1:-ott/loader/otp/graph/*}
f=${2:-otp_report.html}
#svrs=${3:-maps7 maps8 maps9 maps10}
svrs=${3:-maps8}
ts=${4:-maps6.tri-met.org}

for s in $svrs
do
  for p in $path
  do
    if [ -f $p/$f ]; then
      cp $p/$f tmp
      sed -i "s/${ts}/${s}.trimet.org/g" tmp
      cmd="scp tmp $s:$PWD/$p/$f"
      echo $cmd
      eval $cmd
      rm tmp
    fi
  done
done
