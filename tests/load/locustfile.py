#
# this module is a locustfile drives load into a ECS deployment
#
# this locustfile is expected to called from a BASH script
#

import random
import uuid

from locust import HttpLocust
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
# with more than one locust executing, the weight attributes
# defines the relatively likihood that a locust will run a
# particular taskset
#
_noop_weight = 5
_version_weight = 5
_quick_health_check_weight = 10
_comprehensive_health_check_weight = 5
_tasks_happy_path_weight = 75
assert 100 == (
    _noop_weight +
    _version_weight +
    _quick_health_check_weight +
    _comprehensive_health_check_weight +
    _tasks_happy_path_weight
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

    #
    # ```min_wait``` and ```max_wait``` define the time in milliseconds
    # that a simulated entity will wait between executing each task
    #
    min_wait = 0
    max_wait = 0


class ECSHttpLocust(HttpLocust):
    """An abstract base class for all HTTP locusts."""

    #
    # ```min_wait``` and ```max_wait``` define the time in milliseconds
    # that a simulated entity will wait between executing each task
    #
    min_wait = 0
    max_wait = 0

    def __init__(self, *args, **kwargs):
        HttpLocust.__init__(self, *args, **kwargs)

        self.locust_id = uuid.uuid4().hex

        print 'Created %s' % self


class NoOpBehavior(ECSTaskSet):

    @task
    def check_noop(self):
        response = self.client.get('/v1.1/_noop')
        print 'NoOp\t%s\t%s\t%.2f' % (
            self.locust.locust_id,
            response.status_code,
            1000 * response.elapsed.total_seconds())


class NoOpLocust(ECSHttpLocust):

    task_set = NoOpBehavior

    weight = _noop_weight

    def __str__(self):
        return 'NoOp-Locust-%s' % self.locust_id


class VersionBehavior(ECSTaskSet):

    @task
    def version(self):
        response = self.client.get('/v1.1/_version')
        print 'Version\t%s\t%s\t%.2f' % (
            self.locust.locust_id,
            response.status_code,
            1000 * response.elapsed.total_seconds())


class VersionLocust(ECSHttpLocust):

    task_set = VersionBehavior

    weight = _version_weight

    def __str__(self):
        return 'Version-Locust-%s' % self.locust_id


class QuickHealthBehavior(ECSTaskSet):

    @task
    def quick_health_check(self):
        response = self.client.get('/v1.1/_health?quick=true')
        print 'Health-Check-Quick\t%s\t%s\t%.2f' % (
            self.locust.locust_id,
            response.status_code,
            1000 * response.elapsed.total_seconds())


class QuickHealthLocust(ECSHttpLocust):

    task_set = QuickHealthBehavior

    weight = _quick_health_check_weight

    def __str__(self):
        return 'Quick-Health-Locust-%s' % self.locust_id


class ComprehensiveHealthBehavior(ECSTaskSet):

    @task
    def comprehensive_health_check(self):
        response = self.client.get('/v1.1/_health?quick=false')
        print 'Health-Check-Comprehensive\t%s\t%s\t%.2f' % (
            self.locust.locust_id,
            response.status_code,
            1000 * response.elapsed.total_seconds())


class ComprehensiveHealthLocust(ECSHttpLocust):

    task_set = ComprehensiveHealthBehavior

    weight = _tasks_happy_path_weight

    def __str__(self):
        return 'Tasks-Happy-Path-Locust-%s' % self.locust_id


class TasksHappyPathBehavior(ECSTaskSet):

    @task
    def happy_path_task(self):
        url = '/v1.1/tasks?comment=happy_path'
        body = {
            'docker_image': 'ubuntu:14.04',
            'cmd': [
                'echo',
                'hello world',
            ],
        }
        response = self.client.post(url, json=body)
        print 'Tasks-Happy-Path\t%s\t%s\t%.2f' % (
            self.locust.locust_id,
            response.status_code,
            1000 * response.elapsed.total_seconds())


class TasksHappyPathLocust(ECSHttpLocust):

    task_set = TasksHappyPathBehavior

    weight = _tasks_happy_path_weight

    def __str__(self):
        return 'Tasks-Happy-Path-Locust-%s' % self.locust_id
