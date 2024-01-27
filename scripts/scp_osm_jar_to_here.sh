fdir=${1-"call-test"}
tdir=${1-"rtp"}
svr=${2-"otp@maps6"}

# scp OSM
osm="loader/ott/loader/osm/cache"
rm -f ~/rtp/$osm
mkdir ~/rtp/$osm
cmd="scp $svr:~/$osm/*[fls] ~/rtp/$osm"
echo $cmd
#eval $cmd

# scp OSM
otp="loader/ott/loader/otp/graph"
cmd="scp $svr:~/$otp/$fdir/*.jar ~/rtp/$otp/$tdir/"
echo $cmd
eval $cmd

cmd="scp -r $svr:~/$otp/$fdir/ned ~/rtp/$otp/$tdir/"
echo $cmd
eval $cmd
