p=$1
f=$2

for s in maps7 maps8 maps9 maps10
do
    cmd="scp $p/$f $s:$PWD/$p/$f"
    echo $cmd
    eval $cmd
done
