# to build the image
#
#   docker build -t simonsdave/ecs-analyze-load-test-tsv .
#
# to run the image
#
#   docker run -v /tmp/tmp.75LLN1gtrF:/locust-log -v $PWD:/graphs simonsdave/ecs-analyze-load-test-tsv
#
# for testing/debugging
#
#   docker run -i -t simonsdave/ecs-analyze-load-test-tsv /bin/bash
#
# to push to dockerhub
#
#   docker push simonsdave/ecs-analyze-load-test-tsv
#
FROM ubuntu:14.04

MAINTAINER Dave Simons

RUN apt-get update -y && apt-get install -y python python-dev python-pip libxft-dev libfreetype6 libfreetype6-dev libffi-dev
# as per http://blog.pangyanhan.com/posts/2015-07-25-how-to-install-matplotlib-using-virtualenv-on-ubuntu.html
RUN apt-get -y build-dep matplotlib
ADD requirements.txt /tmp/requirements.txt
RUN pip install --requirement /tmp/requirements.txt

ADD analyze_load_test_tsv.py /usr/local/bin/analyze_load_test_tsv.py

# as per http://stackoverflow.com/questions/29073802/matplotlib-cannot-find-configuration-file-matplotlibrc
RUN mkdir -p /root/.config/matplotlib
ADD matplotlibrc /root/.config/matplotlib/matplotlibrc
RUN chown --recursive root:root /root/.config

# the command line syntax is derived from directions in
# http://stackoverflow.com/questions/34632959/redirecting-command-output-in-docker
RUN mkdir -p /graphs
CMD ["/bin/sh", "-c", "analyze_load_test_tsv.py --graphs=/graphs/load-test-graphs.pdf < /locust-log"]
