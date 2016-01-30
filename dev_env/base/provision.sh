#!/usr/bin/env bash

#
# this script creates a base vagrant box which can
# be used for ecs development
#

set -e

apt-get update -y

#
# install docker and configure docker's remote API
# to listen on http://127.0.0.1:4243
#
apt-get install -y docker.io
sed -i -e 's/#DOCKER_OPTS="--dns 8.8.8.8 --dns 8.8.4.4"/DOCKER_OPTS="-H tcp:\/\/127.0.0.1:4243 -H unix:\/\/\/var\/run\/docker.sock"/g' /etc/default/docker

apt-get install -y git
apt-get install -y python-virtualenv
apt-get install -y python-dev
apt-get build-dep -y python-crypto
apt-get install -y libcurl4-openssl-dev
apt-get install -y libffi-dev
apt-get build-dep -y python-pycurl
apt-get install -y unzip

timedatectl set-timezone EST

apt-get install -y nodejs
apt-get install -y npm
ln -s /usr/bin/nodejs /usr/bin/node
chmod a+x /usr/bin/nodejs
npm i -g raml2md
npm i -g raml2html

apt-get install -y nginx
cp /vagrant/nginx.site /etc/nginx/sites-available/default
mkdir -p /usr/share/nginx/ecs/html
chown root:root /usr/share/nginx/ecs/html

curl -s -L --output /etc/jq 'https://github.com/stedolan/jq/releases/download/jq-1.5/jq-linux64'
chown root.root /etc/jq
chmod a+x /etc/jq

# instructions from https://cloud.google.com/sdk/#debubu
export CLOUD_SDK_REPO=cloud-sdk-`lsb_release -c -s`
echo "deb http://packages.cloud.google.com/apt $CLOUD_SDK_REPO main" | tee /etc/apt/sources.list.d/google-cloud-sdk.list
curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key add -
apt-get update && apt-get install google-cloud-sdk

exit 0
