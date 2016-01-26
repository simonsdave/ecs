#
# to build the distrubution @ dist/ecs-*.*.*.tar.gz
#
#   >git clone https://github.com/simonsdave/ecs.git
#   >cd ecs
#   >python setup.py sdist --formats=gztar
#

import re

from setuptools import setup

#
# this approach used below to determine ```version``` was inspired by
# https://github.com/kennethreitz/requests/blob/master/setup.py#L31
#
# why this complexity? wanted version number to be available in the
# a runtime.
#
# the code below assumes the distribution is being built with the
# current directory being the directory in which setup.py is stored
# which should be totally fine 99.9% of the time. not going to add
# the coode complexity to deal with other scenarios
#
reg_ex_pattern = r"__version__\s*=\s*['\"](?P<version>[^'\"]*)['\"]"
reg_ex = re.compile(reg_ex_pattern)
version = ""
with open("ecs/__init__.py", "r") as fd:
    for line in fd:
        match = reg_ex.match(line)
        if match:
            version = match.group("version")
            break
if not version:
    raise Exception("Can't locate project's version number")

setup(
    name="ecs",
    packages=[
        "ecs",
        "ecs.crawls",
        "ecs.spiders",
        "ecs.users",
    ],
    scripts=[
        "bin/crawls.py",
        "bin/crawls.sh",
        "bin/spiders.py",
        "bin/spiders.sh",
        "bin/users.py",
        "bin/users.sh",
    ],
    install_requires=[
        "py-bcrypt==0.4",
        # using tornado.curl_httpclient.CurlAsyncHTTPClient
        "pycurl>=7.19.5.1",
        "python-dateutil==2.4.2",
        "tor-async-couchdb==0.40.0",
        "tor-async-util==1.10.0",
        "tor-async-fleet==0.8.1",
        "tornado==4.3",
    ],
    dependency_links=[
        "https://github.com/simonsdave/tor-async-couchdb/tarball/v0.40.0#egg=tor-async-couchdb-0.40.0",
        "https://github.com/simonsdave/tor-async-fleet/tarball/v0.8.1#egg=tor-async-fleet-0.8.1",
        "https://github.com/simonsdave/tor-async-util/tarball/v1.10.0#egg=tor-async-util-1.10.0",
    ],
    include_package_data=True,
    version=version,
    description="",
    author="Dave Simons",
    author_email="simonsdave@gmail.com",
    url="https://github.com/simonsdave/ecs",
)
