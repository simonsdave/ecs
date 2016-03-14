# to build the image
#
#   sudo docker build -t simonsdave/ecs-apidocs .
#
# to run the image
#
#   sudo docker run -d --name=apidocs simonsdave/ecs-apidocs nginx
#
# for testing/debugging
#
#   sudo docker run -p 8081:80 simonsdave/ecs-apidocs nginx
#   sudo docker run -i -t simonsdave/ecs-apidocs /bin/bash
#
# to push to dockerhub
#
#   sudo docker push simonsdave/ecs-apidocs
#
FROM ubuntu:14.04

MAINTAINER Dave Simons

RUN apt-get update -y

#
# install nginx per these instructions
#
#   http://nginx.org/en/linux_packages.html
#
# without the first 5 instructions version 1.4.6 of nginx
# is installed by "apt-get install nginx"
# 
RUN apt-get install wget -y
RUN wget -q -O- http://nginx.org/keys/nginx_signing.key | apt-key add -
RUN echo "deb http://nginx.org/packages/mainline/ubuntu/ trusty nginx" >> /etc/apt/sources.list
RUN echo "deb-src http://nginx.org/packages/mainline/ubuntu/ trusty nginx" >> /etc/apt/sources.list
RUN apt-get update -y
RUN apt-get install nginx -y

#
# configure nginx
#
RUN echo "daemon off;" >> /etc/nginx/nginx.conf
ADD ecs.conf /etc/nginx/conf.d/ecs.conf
RUN mkdir -p /usr/share/nginx/html
ADD api_docs.tar /usr/share/nginx/html

# get access & error logs going to stdout & stderr so
# "standard" patterns for consuming these messages
# can be applied
RUN ln -sf /dev/stdout /var/log/nginx/access.log
RUN ln -sf /dev/stderr /var/log/nginx/error.log


