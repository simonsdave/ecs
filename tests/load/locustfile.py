#
# this module is a locustfile drives load into a ECS deployment
#
# this locustfile is expected to called from a BASH script
#

import httplib
import os
import random
import re
import uuid

from locust import HttpLocust
import requests
from locust import task
from locust import TaskSet

"""
#
# when requests is configured to not verify the ids' SSL/TLS cert (which
# should only be done during development ie. when a self signed SSL/TLS
# cert is being used) a very annoying InsecureRequestWarning and IMHO
# **not** so valuable warning message is generated on every request.
# disable_warnings is a hack to eliminate the warning:-)
#
# there's a discussion @ https://github.com/kennethreitz/requests/issues/2214
# describing why what's being done here is a bad idea.
#
if not _verify_ids_cert:
    requests.packages.urllib3.disable_warnings()
"""


#
# credentials for basic authentication are required when running
# a load test against a real ECS deployment. the environment variable
# ECS_CREDENTIALS is expected to point to a file which contains
# a single set of credentials on each line - specifically, a key
# and secret seperated by a colon (the stdout created when using the
# "ecsctl.sh creds" command).
#
def _create_credentials():
    credentials_filename = os.environ.get('ECS_CREDENTIALS', None)
    if not credentials_filename:
        return None

    reg_ex_pattern = r'^\s*(?P<key>[^\:\s]+)\:(?P<secret>[^\s]+)\s*$'
    reg_ex = re.compile(reg_ex_pattern)

    rv = []
    with open(credentials_filename, 'r') as fd:
        for line in fd:
            match = reg_ex.match(line)
            if match:
                key = match.group('key')
                secret = match.group('secret')
                auth = requests.auth.HTTPBasicAuth(key, secret)
                rv.append(auth)
    return rv


_credentials = _create_credentials()


def _get_random_credentials():
    return random.choice(_credentials) if _credentials else None

#
# with more than one locust executing, the weight attributes
# defines the relatively likihood that a locust will run a
# particular taskset
#


_noop_weight = 5
_version_weight = 5
_quick_health_check_weight = 10
_slow_health_check_weight = 5
_tasks_weight = 75
assert 100 == (
    _noop_weight +
    _version_weight +
    _quick_health_check_weight +
    _slow_health_check_weight +
    _tasks_weight
)


def _is_percent_of_time(percent_of_time):
    """Returns ```True``` if ```percent_of_time``` if it less
    than or equal to a randomly generated number from a uniform
    distribution.

    This function is useful for scenarios expressing locust behavior
    of the format "N % of the time do X".
    """
    assert 0 <= percent_of_time
    assert percent_of_time <= 100
    random_number = random.uniform(0, 100)
    return random_number <= percent_of_time


class ECSTaskSet(TaskSet):
    """An abstract base class for all tasksets."""

    min_wait = 0
    max_wait = 0

    def log_on_response(self, behavior, response, expected_status_code):
        print '%s\t%s\t%d\t%.2f' % (
            behavior,
            self.locust.locust_id,
            1 if response.status_code == expected_status_code else 0,
            1000 * response.elapsed.total_seconds())


class ECSHttpLocust(HttpLocust):
    """An abstract base class for all HTTP locusts."""

    def __init__(self, *args, **kwargs):
        HttpLocust.__init__(self, *args, **kwargs)

        self.locust_id = uuid.uuid4().hex

        print 'Created %s' % self


class NoOpBehavior(ECSTaskSet):

    min_wait = 500
    max_wait = 1000

    @task
    def check_noop(self):
        response = self.client.get('/v1.1/_noop', auth=_get_random_credentials())
        self.log_on_response('NoOp', response, httplib.OK)


class NoOpLocust(ECSHttpLocust):

    task_set = NoOpBehavior

    weight = _noop_weight

    def __str__(self):
        return 'NoOp-Locust-%s' % self.locust_id


class VersionBehavior(ECSTaskSet):

    min_wait = 500
    max_wait = 1000

    @task
    def version(self):
        response = self.client.get('/v1.1/_version', auth=_get_random_credentials())
        self.log_on_response('Version', response, httplib.OK)


class VersionLocust(ECSHttpLocust):

    task_set = VersionBehavior

    weight = _version_weight

    def __str__(self):
        return 'Version-Locust-%s' % self.locust_id


class QuickHealthBehavior(ECSTaskSet):

    min_wait = 500
    max_wait = 1000

    @task
    def quick_health_check(self):
        response = self.client.get('/v1.1/_health?quick=true', auth=_get_random_credentials())
        self.log_on_response('Health-Check-Quick', response, httplib.OK)


class QuickHealthLocust(ECSHttpLocust):

    task_set = QuickHealthBehavior

    weight = _quick_health_check_weight

    def __str__(self):
        return 'Quick-Health-Locust-%s' % self.locust_id


class SlowHealthBehavior(ECSTaskSet):

    min_wait = 500
    max_wait = 1000

    @task
    def comprehensive_health_check(self):
        response = self.client.get('/v1.1/_health?quick=false', auth=_get_random_credentials())
        self.log_on_response('Health-Check-Slow', response, httplib.OK)


class SlowHealthLocust(ECSHttpLocust):

    task_set = SlowHealthBehavior

    weight = _slow_health_check_weight

    def __str__(self):
        return 'Tasks-Happy-Path-Locust-%s' % self.locust_id


class TasksBehavior(ECSTaskSet):

    min_wait = 0
    max_wait = 0

    _templates = [
        {
            'name': 'Happy-Path',
            'body': {
                'docker_image': 'ubuntu:14.04',
                'cmd': [
                    'echo',
                    'hello world',
                ],
            },
            'expected_status_code': 201,
            'weight': 80,
        },
        {
            'name': 'Image-Not-Found',
            'body': {
                'docker_image': 'bindle:berry',
                'cmd': [
                    'echo',
                    'hello world',
                ],
            },
            'expected_status_code': 404,
            'weight': 10,
        },
        {
            'name': 'Bad-Request-Body',
            'body': {
            },
            'expected_status_code': 400,
            'weight': 10,
        },
    ]

    @task
    def task(self):
        weighted_templates = []
        for template in type(self)._templates:
            weighted_templates.extend([template] * template['weight'])

        template = weighted_templates[random.randint(0, len(weighted_templates) - 1)]

        url = '/v1.1/tasks?comment=%s' % template['name'].lower()
        body = template['body']
        with self.client.post(url, auth=_get_random_credentials(), json=body, catch_response=True) as response:
            self.log_on_response(
                'Tasks-%s' % template['name'],
                response,
                template['expected_status_code'])

            if response.status_code == template['expected_status_code']:
                response.success()
            else:
                msg = 'Got status code %d and expected %d' % (
                    response.status_code,
                    template['expected_status_code'],
                )
                response.failure(msg)


class TasksLocust(ECSHttpLocust):

    task_set = TasksBehavior

    weight = _tasks_weight

    def __str__(self):
        return 'Tasks-Locust-%s' % self.locust_id
