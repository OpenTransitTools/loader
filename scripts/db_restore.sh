DIR=`dirname $0`
cd $DIR/../ott/loader/gtfsdb/cache
echo $PWD
ls *.tar*

for x in `ls *.tar`
do
  echo restore backup: $x
  r="pg_restore -d ott $x"
  echo $r
  eval $r

  m="mv $x $x-processed"
  echo $m
  eval $m

  echo
done
