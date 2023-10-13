DIR=`dirname $0`
. $DIR/base.sh

cd $DIR/../../ott/loader/gtfsdb/cache
echo $PWD
ls *.tar*

for x in `ls *.tar`
do
  echo restore backup: $x
  r="pg_restore -d ${db_url}${db} $x"
  echo $r
  eval $r

  m="mv $x $x-processed"
  echo $m
  eval $m

  echo
done
