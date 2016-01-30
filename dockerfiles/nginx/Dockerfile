# to build the image
#
#   docker build -t simonsdave/ecs-nginx .
#
# to run the image
#
#   docker run -d -p 80:80 -p 443:443 --link ecs:ecs --link apidocs:apidocs simonsdave/ecs-nginx nginx.sh <config-tar-file-url>
#
# for testing/debugging
#
#   docker run -i -t --link ecs:ecs --link apidocs:apidocs simonsdave/ecs-nginx /bin/bash
#
# to push to dockerhub
#
#   docker push simonsdave/ecs-nginx
#
FROM ubuntu:14.04

MAINTAINER Dave Simons

RUN apt-get update -y
RUN apt-get install -y nginx
RUN apt-get install -y curl

RUN echo "daemon off;" >> /etc/nginx/nginx.conf
ADD nginx.site /etc/nginx/sites-available/default
ADD nginx.sh /usr/local/bin/nginx.sh
RUN mkdir -p /etc/nginx/ssl

# get access & error logs going to stdout & stderr so
# "standard" patterns for consuming these messages
# can be applied
RUN ln -sf /dev/stdout /var/log/nginx/access.log
RUN ln -sf /dev/stderr /var/log/nginx/error.log
