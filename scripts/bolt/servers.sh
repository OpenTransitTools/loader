BLUE_STAG="cs-st-mapapp01"
GREEN_STAG="rj-st-mapapp01"

OTP_PORT=52425

if [ $USER == 'otp' ]; then
  ACCOUNTS="rtp"
elif [ $USER == 'geoserver' ]; then
  ACCOUNTS="geoserver"
elif [ $USER == 'pelias' ]; then
  ACCOUNTS="pelias peliaswrap solrwrap"
elif [ $USER == 'tileserver-gl' ]; then
  ACCOUNTS="tiles"
  LOAD_BALANCER="web_tiles-trimet-org@rj-st-mapweb01"
else
  ACCOUNTS="unknown"
fi
