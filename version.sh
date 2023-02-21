export VERSION=`cat version`
echo $VERSION
sed -i "0,/RE/s/^API_VERSION=.*/API_VERSION=${VERSION}/" .env >> .env
