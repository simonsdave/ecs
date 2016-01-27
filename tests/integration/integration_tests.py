"""A collection of integration tests for the ephemeral
container service.
"""
from ConfigParser import ConfigParser
import httplib
import os
import signal
import subprocess
import tempfile
import time
import unittest

from tor_async_util.nose_plugins import FileCapture
import requests


class ServiceConfig(object):
    """This context manager encapsulates the details of creating a
    configuration file suitable for determining how an instance of the
    ephemeral container service should operate. This class is intended
    make writing integration tests a little easlier/cleaner.
    """

    def __init__(self):
        object.__init__(self)

        self.ip = '127.0.0.1'
        self.port = 8448

        self.filename = None

    def __enter__(self):
        section = 'ecs'

        cp = ConfigParser()
        cp.add_section(section)

        cp.set(section, 'ip', self.ip)
        cp.set(section, 'port', self.port)
        cp.set(section, 'log_level', 'info')
        cp.set(section, 'max_concurrent_executing_http_requests', '250')

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
        FileCapture.watch(self._stdout_file, 'ephemeral_container_service.py stdout')

        cmd = [
            'ephemeral_container_service.py',
            '--config=%s' % self.service_config.filename,
        ]
        self._process = subprocess.Popen(
            cmd,
            stdout=open(self._stdout_file, 'w+'),
            stderr=subprocess.STDOUT,
            preexec_fn=os.setsid,
        )

        url = 'http://%s:%d/v1.0/_noop' % (
            self.service_config.ip,
            self.service_config.port,
        )
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
        with ServiceConfig() as service_config:
            with Service(service_config):
                the_test_func(service_config)


class NoOpTestCase(IntegrationTestCase):
    """A collection of integration tests for the /_noop endpoint."""

    def test_happy_path(self):
        def the_test(service_config):
            url = 'http://%s:%d/v1.0/_noop' % (
                service_config.ip,
                service_config.port,
            )
            response = requests.get(url)
            self.assertEqual(response.status_code, httplib.OK)

        self.setup_env_and_run_func(the_test)


class HealthTestCase(IntegrationTestCase):
    """A collection of integration tests for the /_health endpoint."""

    def test_happy_path_no_quick_arg(self):
        def the_test(service_config):
            url = 'http://%s:%d/v1.0/_health' % (
                service_config.ip,
                service_config.port,
            )
            response = requests.get(url)
            self.assertEqual(response.status_code, httplib.OK)

        self.setup_env_and_run_func(the_test)

    def test_happy_path_quick_arg_is_true(self):
        def the_test(service_config):
            url = 'http://%s:%d/v1.0/_health?quick=true' % (
                service_config.ip,
                service_config.port,
            )
            response = requests.get(url)
            self.assertEqual(response.status_code, httplib.OK)

        self.setup_env_and_run_func(the_test)

    def test_happy_path_quick_arg_is_false(self):
        def the_test(service_config):
            url = 'http://%s:%d/v1.0/_health?quick=false' % (
                service_config.ip,
                service_config.port,
            )
            response = requests.get(url)
            self.assertEqual(response.status_code, httplib.OK)

        self.setup_env_and_run_func(the_test)

    def test_happy_path_quick_arg_is_not_boolean(self):
        def the_test(service_config):
            url = 'http://%s:%d/v1.0/_health?quick=dave' % (
                service_config.ip,
                service_config.port,
            )
            response = requests.get(url)
            self.assertEqual(response.status_code, httplib.BAD_REQUEST)

        self.setup_env_and_run_func(the_test)


class ECSTestCase(IntegrationTestCase):
    """A collection of integration tests for the /_health endpoint."""

    def test_happy_path_with_simple_echo(self):
        def the_test(service_config):
            url = 'http://%s:%d/v1.0/tasks' % (
                service_config.ip,
                service_config.port,
            )
            body = {
                'docker_image': 'ubuntu',
                'tag': 'latest',
                'cmd': [
                    'echo',
                    'hello world',
                ]
            }
            headers = {
                'Content-Type': 'application/json',
            }
            response = requests.post(url, json=body)
            self.assertEqual(response.status_code, httplib.CREATED)
            json_response_body = response.json()
            self.assertEqual(json_response_body['exitCode'], 0)
            self.assertEqual(json_response_body['base64EncodedStdOut'].strip(), body['cmd'][1])
            self.assertEqual(json_response_body['base64EncodedStdErr'].strip(), '')

        self.setup_env_and_run_func(the_test)

    def test_non_zero_exit_code(self):
        def the_test(service_config):
            url = 'http://%s:%d/v1.0/tasks' % (
                service_config.ip,
                service_config.port,
            )
            exit_code = 1
            body = {
                'docker_image': 'ubuntu',
                'tag': 'latest',
                'cmd': [
                    'bash',
                    '-c',
                    'exit %d' % exit_code,
                ]
            }
            headers = {
                'Content-Type': 'application/json',
            }
            response = requests.post(url, json=body)
            self.assertEqual(response.status_code, httplib.CREATED)
            json_response_body = response.json()
            self.assertEqual(json_response_body['exitCode'], exit_code)
            self.assertEqual(json_response_body['base64EncodedStdOut'].strip(), '')
            self.assertEqual(json_response_body['base64EncodedStdErr'].strip(), '')

        self.setup_env_and_run_func(the_test)

