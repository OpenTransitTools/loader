for f in `ls ott/loader/otp/graph/*/router-config.json` versions.cfg
do
  git update-index --assume-unchanged $f
done
