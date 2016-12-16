#!/usr/bin/env bash

#
# this script provisions an ECS development environment
#

set -e

apt-get update -y

#
# this next set of commands installs and configures the latest
# version of docker. all pretty straight forward / obvious stuff
# except the while loop. the while loop was added when upgrading
# to docker 1.12 and was introduced to fix a timing problem.
# the final 'service docker restart' was failing because the
# configuration change in the sed command was telling the docker
# daemon to listen on docker0 (172.17.0.1) but docker0 had yet
# to be created (theory is that the docker daemon creates
# docker0 on daemon startup if docker0 doesn't already exist).
# so, the while loops just gives the daemon time to create docker0.
#
until apt-key adv --keyserver hkp://p80.pool.sks-keyservers.net:80 --recv-keys 58118E89F3A912897C070ADBF76221572C52609D; do echo '.'; done
echo "deb https://apt.dockerproject.org/repo ubuntu-trusty main" | tee /etc/apt/sources.list.d/docker.list
apt-get update
apt-get install -y docker-engine
echo 'waiting for docker0 network to start '
while ! ifconfig | grep docker0 >& /dev/null
do
        echo '.'
        sleep 1
done
echo 'docker0 network started'
sed -i -e 's|#DOCKER_OPTS="--dns 8.8.8.8 --dns 8.8.4.4"|DOCKER_OPTS="-H tcp://172.17.0.1:2375 -H unix:///var/run/docker.sock"|g' /etc/default/docker
usermod -aG docker vagrant
service docker restart

apt-get install -y git

apt-get install -y python-virtualenv
apt-get install -y python-dev
apt-get build-dep -y python-crypto
apt-get install -y libcurl4-openssl-dev
apt-get install -y libffi-dev
apt-get build-dep -y python-pycurl
apt-get install -y unzip

# apache2-utils installed to get access to htpasswd
apt-get install -y apache2-utils

# as per http://blog.pangyanhan.com/posts/2015-07-25-how-to-install-matplotlib-using-virtualenv-on-ubuntu.html
apt-get -y build-dep matplotlib
# as per http://stackoverflow.com/questions/29073802/matplotlib-cannot-find-configuration-file-matplotlibrc
mkdir -p ~vagrant/.config/matplotlib
cp /vagrant/matplotlibrc ~vagrant/.config/matplotlib
chown --recursive vagrant:vagrant ~vagrant/.config

timedatectl set-timezone EST

#
# this install process does not feel right
# look @ .travis.yml for how it uses nvm - that feels correct
# could not get nvm to work here :-(
#
apt-get install -y nodejs
apt-get install -y npm
ln -s /usr/bin/nodejs /usr/bin/node
chmod a+x /usr/bin/nodejs
curl -sL https://deb.nodesource.com/setup_4.x | sudo -E bash -
apt-get install -y nodejs
npm i -g raml2md
npm i -g raml2html

apt-get install -y nginx
cp /vagrant/nginx.site /etc/nginx/sites-available/default
mkdir -p /usr/share/nginx/ecs/html
chown root:root /usr/share/nginx/ecs/html
service nginx restart

curl -s -L --output /usr/local/bin/jq 'https://github.com/stedolan/jq/releases/download/jq-1.5/jq-linux64'
chown root.root /usr/local/bin/jq
chmod a+x /usr/local/bin/jq

# instructions from https://cloud.google.com/sdk/#debubu
export CLOUD_SDK_REPO=cloud-sdk-`lsb_release -c -s`
echo "deb http://packages.cloud.google.com/apt $CLOUD_SDK_REPO main" | tee /etc/apt/sources.list.d/google-cloud-sdk.list
curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key add -
apt-get update -y && apt-get install -y google-cloud-sdk

cp /vagrant/.vimrc ~vagrant/.vimrc
chown vagrant:vagrant ~vagrant/.vimrc

echo 'export VISUAL=vim' >> ~vagrant/.profile
echo 'export EDITOR="$VISUAL"' >> ~vagrant/.profile

if [ $# == 2 ]; then
    su - vagrant -c "git config --global user.name \"${1:-}\""
    su - vagrant -c "git config --global user.email \"${2:-}\""
fi

exit 0
