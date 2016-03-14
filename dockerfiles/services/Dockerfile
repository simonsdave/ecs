# to build the image
#
#   sudo docker build -t simonsdave/ecs-services .
#
# to run the image
#
#   sudo docker run -d --name=tasks simonsdave/ecs-services ephemeral_container_service.py
#
# for testing/debugging
#
#   sudo docker run -i -t simonsdave/ecs-services /bin/bash
#
# to push to dockerhub
#
#   sudo docker push simonsdave/ecs-services

FROM ubuntu:14.04

MAINTAINER Dave Simons

RUN apt-get update -y
RUN apt-get install -y curl
RUN apt-get install -y python
RUN apt-get install -y python-dev
RUN apt-get install -y python-pip
RUN pip install pip==1.5.6

RUN apt-get install -y python-crypto
RUN apt-get install -y libcurl4-openssl-dev
RUN apt-get install -y python-pycurl

COPY services.tar.gz /tmp/services.tar.gz

RUN pip install --process-dependency-links /tmp/services.tar.gz

RUN rm /tmp/services.tar.gz
