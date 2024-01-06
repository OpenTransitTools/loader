#
# COPY a graph directory over to another server
#

#TO=${1:-'mapdata@cs-pd-mapetl01:~/graph/'}
TO=${1:-'otp@rj-dv-mapapp01:~/loader/ott/loader/otp/graph/rtp/'}
FM=${2:-'./ott/loader/otp/graph/call-test'}
CP=${3:-'scp'}

D="${FM}/*pbf ${FM}/*zip ${FM}/*jar ${FM}/ned"
echo
ls -l $D
echo

E="$CP -r ${D} ${TO}"
echo $E
eval $E
