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
    raise Exception('Can\'t locate project\'s version number')

setup(
    name='ecs',
    packages=[
        'ecs',
    ],
    scripts=[
        'bin/ecservice.py',
    ],
    install_requires=[
        # using tornado.curl_httpclient.CurlAsyncHTTPClient
        'pycurl>=7.19.5.1',
        'semantic-version==2.5.0',
        'tor-async-util==1.12.0',
        'tornado==4.3',
    ],
    dependency_links=[
        'https://github.com/simonsdave/tor-async-util/tarball/v1.12.0#egg=tor-async-util-1.12.0',
    ],
    include_package_data=True,
    version=version,
    description='Ephemeral Container Service',
    author='Dave Simons',
    author_email='simonsdave@gmail.com',
    url='https://github.com/simonsdave/ecs',
)
