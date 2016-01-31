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
#   sudo docker run -i -t simonsdave/ecs-apidocs /bin/bash
#
# to push to dockerhub
#
#   sudo docker push simonsdave/ecs-apidocs
#
FROM ubuntu:14.04

MAINTAINER Dave Simons

RUN apt-get update -y
RUN apt-get install -y nginx

RUN echo "daemon off;" >> /etc/nginx/nginx.conf
ADD nginx.site /etc/nginx/sites-available/default
RUN mkdir -p /usr/share/nginx/html
ADD api_docs.tar /usr/share/nginx/html

# get access & error logs going to stdout & stderr so
# "standard" patterns for consuming these messages
# can be applied
RUN ln -sf /dev/stdout /var/log/nginx/access.log
RUN ln -sf /dev/stderr /var/log/nginx/error.log
