"""A collection of integration tests for the ephemeral
container service.
"""
import base64
from ConfigParser import ConfigParser
import httplib
import os
import signal
import subprocess
import tempfile
import time
import unittest
import uuid

from nose.plugins.attrib import attr
from tor_async_util.nose_plugins import FileCapture
import requests

import ecs

#
# defines the api version that this set of tests validates
#
_api_version = r'v1.1'


class ServiceConfig(object):
    """This context manager encapsulates the details of creating a
    configuration file suitable for determining how an instance of the
    ephemeral container service should operate. This class is intended
    make writing integration tests a little easlier/cleaner.
    """

    def __init__(self):
        object.__init__(self)

        self._ip = '127.0.0.1'
        self._port = 8448

        self.endpoint = 'http://%s:%d' % (self._ip, self._port)

        self.filename = None

    def __enter__(self):
        section = 'ecs'

        cp = ConfigParser()
        cp.add_section(section)

        cp.set(section, 'address', self._ip)
        cp.set(section, 'port', self._port)
        cp.set(section, 'log_level', 'info')
        cp.set(section, 'max_concurrent_executing_http_requests', '250')
        cp.set(section, 'docker_remote_api', 'http://172.17.42.1:2375')
        cp.set(section, 'docker_remote_api_connect_timeout', 3000)
        cp.set(section, 'docker_remote_api_request_timeout', 300000)

        self.filename = tempfile.mktemp()
        with open(self.filename, 'w+') as fp:
            cp.write(fp)

        FileCapture.watch(self.filename, type(self).__name__)

        return self

    def __exit__(self, exc_type, exc_value, traceback):
        pass


class Service(object):
    """This context manager encapsulates the details behind spinning up
    the ephemeral container service and is intended make writing integration
    tests a little easlier/cleaner.
    """

    def __init__(self, service_config):
        object.__init__(self)

        self.service_config = service_config

        self._stdout_file = None
        self._process = None

    def __enter__(self):
        self._stdout_file = tempfile.mktemp()
        FileCapture.watch(self._stdout_file, 'ecservice.py stdout')

        cmd = [
            'ecservice.py',
            '--config=%s' % self.service_config.filename,
        ]
        self._process = subprocess.Popen(
            cmd,
            stdout=open(self._stdout_file, 'w+'),
            stderr=subprocess.STDOUT,
            preexec_fn=os.setsid,
        )

        url = '%s/%s/_noop' % (self.service_config.endpoint, _api_version)
        for i in range(0, 10):
            try:
                response = requests.get(url)
                if response.status_code == httplib.OK:
                    return self
            except:
                pass

            time.sleep(0.5)

        ex_msg = 'Could not confirm service started @ %s' % url
        ex = Exception(ex_msg)
        raise ex

    def __exit__(self, exc_type, exc_value, traceback):
        if self._process:
            os.killpg(self._process.pid, signal.SIGKILL)
            self._process = None


class IntegrationTestCase(unittest.TestCase):
    """An abstract base class for all integration tests."""

    def setup_env_and_run_func(self, the_test_func):
        endpoint = os.environ.get('ECS_ENDPOINT', None)
        if endpoint:
            key = os.environ.get('ECS_KEY', None)
            secret = os.environ.get('ECS_SECRET', None)
            auth = requests.auth.HTTPBasicAuth(key, secret) if key and secret else None
            the_test_func(endpoint, auth)
        else:
            with ServiceConfig() as service_config:
                with Service(service_config):
                    the_test_func(service_config.endpoint, None)

    def avoid_rate_limiting_and_sleep_one_second(self):
        if os.environ.get('ECS_ENDPOINT', None):
            one_second = 1.0
            time.sleep(one_second)

    def setUp(self):
        self.avoid_rate_limiting_and_sleep_one_second()

    def tearDown(self):
        pass


@attr('integration')
class NoOpTestCase(IntegrationTestCase):
    """A collection of integration tests for the /_noop endpoint."""

    def test_happy_path(self):
        def the_test(endpoint, auth):
            url = '%s/%s/_noop' % (endpoint, _api_version)
            response = requests.get(url, auth=auth)
            self.assertEqual(response.status_code, httplib.OK)

        self.setup_env_and_run_func(the_test)


@attr('integration')
class VersionTestCase(IntegrationTestCase):
    """A collection of integration tests for the /_version endpoint."""

    def test_happy_path_no_quick_arg(self):
        def the_test(endpoint, auth):
            url = '%s/%s/_version' % (endpoint, _api_version)
            response = requests.get(url, auth=auth)
            self.assertEqual(response.status_code, httplib.OK)

            expected_response = {
                'version': ecs.__version__,
                'links': {
                    'self': {
                        'href': url,
                    }
                }
            }
            self.assertEqual(expected_response, response.json())

        self.setup_env_and_run_func(the_test)


@attr('integration')
class HealthTestCase(IntegrationTestCase):
    """A collection of integration tests for the /_health endpoint."""

    def test_happy_path_no_quick_arg(self):
        def the_test(endpoint, auth):
            url = '%s/%s/_health' % (endpoint, _api_version)
            response = requests.get(url, auth=auth)
            self.assertEqual(response.status_code, httplib.OK)

        self.setup_env_and_run_func(the_test)

    def test_happy_path_quick_arg_is_true(self):
        def the_test(endpoint, auth):
            url = '%s/%s/_health?quick=true' % (endpoint, _api_version)
            response = requests.get(url, auth=auth)
            self.assertEqual(response.status_code, httplib.OK)

        self.setup_env_and_run_func(the_test)

    def test_happy_path_quick_arg_is_false(self):
        def the_test(endpoint, auth):
            url = '%s/%s/_health?quick=false' % (endpoint, _api_version)
            response = requests.get(url, auth=auth)
            self.assertEqual(response.status_code, httplib.OK)

        self.setup_env_and_run_func(the_test)

    def test_happy_path_quick_arg_is_not_boolean(self):
        def the_test(endpoint, auth):
            url = '%s/%s/_health?quick=dave' % (endpoint, _api_version)
            response = requests.get(url, auth=auth)
            self.assertEqual(response.status_code, httplib.BAD_REQUEST)

        self.setup_env_and_run_func(the_test)


@attr('integration')
class TasksTestCase(IntegrationTestCase):
    """A collection of integration tests for the /_tasks endpoint."""

    def _test_happy_path_with_simple_echo(self, trailing_slash):
        def the_test(endpoint, auth):
            url = '%s/%s/tasks%s' % (
                endpoint,
                _api_version,
                '/' if trailing_slash else '',
            )
            body = {
                'docker_image': 'ubuntu:14.04',
                'cmd': [
                    'echo',
                    'hello world',
                ],
            }
            response = requests.post(url, auth=auth, json=body)
            self.assertEqual(response.status_code, httplib.CREATED)
            json_response_body = response.json()
            self.assertEqual(json_response_body['exitCode'], 0)
            self.assertEqual(
                base64.b64decode(json_response_body['stdout']).strip(),
                body['cmd'][1])
            self.assertEqual(
                json_response_body['stderr'].strip(),
                '')

        self.setup_env_and_run_func(the_test)

    def test_happy_path_with_simple_echo_with_training_slash(self):
        self._test_happy_path_with_simple_echo(trailing_slash=True)

    def test_happy_path_with_simple_echo_without_training_slash(self):
        self._test_happy_path_with_simple_echo(trailing_slash=False)

    def test_non_zero_exit_code(self):
        def the_test(endpoint, auth):
            url = '%s/%s/tasks' % (endpoint, _api_version)
            exit_code = 1
            body = {
                'docker_image': 'ubuntu:14.04',
                'cmd': [
                    'bash',
                    '-c',
                    'exit %d' % exit_code,
                ]
            }
            response = requests.post(url, auth=auth, json=body)
            self.assertEqual(response.status_code, httplib.CREATED)
            json_response_body = response.json()
            self.assertEqual(json_response_body['exitCode'], exit_code)
            self.assertEqual(json_response_body['stdout'].strip(), '')
            self.assertEqual(json_response_body['stderr'].strip(), '')

        self.setup_env_and_run_func(the_test)

    def test_stdout_and_stderr_output(self):
        def the_test(endpoint, auth):
            url = '%s/%s/tasks' % (endpoint, _api_version)
            stdout = uuid.uuid4().hex
            stderr = uuid.uuid4().hex
            body = {
                'docker_image': 'ubuntu:14.04',
                'cmd': [
                    'bash',
                    '-c',
                    'echo %s > /dev/stdout && echo %s > /dev/stderr' % (stdout, stderr)
                ]
            }
            response = requests.post(url, auth=auth, json=body)
            self.assertEqual(response.status_code, httplib.CREATED)
            json_response_body = response.json()
            self.assertEqual(
                base64.b64decode(json_response_body['stdout']).strip(),
                stdout)
            self.assertEqual(
                base64.b64decode(json_response_body['stderr']).strip(),
                stderr)

        self.setup_env_and_run_func(the_test)

    def test_unknown_docker_image(self):
        def the_test(endpoint, auth):
            url = '%s/%s/tasks' % (endpoint, _api_version)
            body = {
                'docker_image': 'bindle/berry',
                'cmd': [
                    'echo',
                    'dave was here',
                ]
            }
            response = requests.post(url, auth=auth, json=body)
            self.assertEqual(response.status_code, httplib.NOT_FOUND)

        self.setup_env_and_run_func(the_test)

    def test_invalid_docker_image_name(self):
        def the_test(endpoint, auth):
            url = '%s/%s/tasks' % (endpoint, _api_version)
            body = {
                'docker_image': 'IMAGE_NAME_IS_INVALID',
                'cmd': [
                    'echo',
                    'dave was here',
                ]
            }
            response = requests.post(url, auth=auth, json=body)
            self.assertEqual(response.status_code, httplib.NOT_FOUND)

        self.setup_env_and_run_func(the_test)

    def test_bad_request_body(self):
        def the_test(endpoint, auth):
            bodies = [
                {
                    'cmd': [
                        'echo',
                        'dave was here',
                    ]
                },
                {
                    'docker_image': 'ubuntu:14.04',
                },
                {
                    'docker_image': 'ubuntu:14.04',
                    'cmd': [
                    ]
                },
                {
                },
            ]
            for body in bodies:
                self.avoid_rate_limiting_and_sleep_one_second()
                url = '%s/%s/tasks' % (endpoint, _api_version)
                response = requests.post(url, auth=auth, json=body)
                self.assertEqual(response.status_code, httplib.BAD_REQUEST)

        self.setup_env_and_run_func(the_test)
