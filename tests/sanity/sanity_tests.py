"""A collection of sanity tests for an ECS deployment
that's already been spun up.
"""
import httplib
import os
import unittest

from nose.plugins.attrib import attr
import requests


class SanityTestCase(unittest.TestCase):
    """An abstract base class for all sanity tests."""

    def get_env_and_run_func(self, the_test_func):
        endpoint = os.environ.get('ECS_ENDPOINT', None)
        key = os.environ.get('ECS_KEY', None)
        secret = os.environ.get('ECS_SECRET', None)
        if endpoint and key and secret:
            auth = requests.auth.HTTPBasicAuth(key, secret)
            the_test_func(endpoint, auth)


@attr('sanity')
class TasksTestCase(SanityTestCase):
    """A collection of sanity tests for the /_tasks endpoint."""

    def test_request_too_large(self):
        sizes = {
            3 * 1024: httplib.CREATED,
            6 * 1024: httplib.REQUEST_ENTITY_TOO_LARGE,
        }

        for (size, expected_status_code) in sizes.iteritems():
            def the_test(endpoint, auth):
                url = '%s/v1.0/tasks' % endpoint
                body = {
                    'docker_image': 'ubuntu',
                    'tag': 'latest',
                    'cmd': [
                        'echo',
                        '0' * size,
                    ],
                }
                response = requests.post(url, auth=auth, json=body)
                self.assertEqual(response.status_code, expected_status_code)

            self.get_env_and_run_func(the_test)
