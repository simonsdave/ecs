"""This module contains a collection of unit tests which
validate the ..request_handler module.
"""

import base64
import httplib
import json
import socket
import re
import uuid

import mock
import semantic_version
import tor_async_util
import tornado
import tornado.netutil
import tornado.testing
import tornado.web

from ..async_actions import AsyncEndToEndContainerRunner     # noqa
import ecs
from ..request_handlers import HealthRequestHandler
from ..request_handlers import NoOpRequestHandler
from ..request_handlers import TasksRequestHandler
from ..request_handlers import VersionRequestHandler


#
# the motivation for patching tornado.testing.bind_unused_port is
# described https://github.com/tornadoweb/tornado/pull/1574
#
# believe the PR will be incorporated in tornado release after 4.3
# and hence the version check. obviously once the PR is released
# the patch below can be deleted
#
assert semantic_version.Version(tornado.version, partial=True) <= semantic_version.Version('4.3', partial=True)


def _fix_for_travis_bind_unused_port():
    [sock] = tornado.netutil.bind_sockets(None, '127.0.0.1', family=socket.AF_INET)
    port = sock.getsockname()[1]
    return sock, port


tornado.testing.bind_unused_port = _fix_for_travis_bind_unused_port


class Patcher(object):
    """An abstract base class for all patcher context managers."""

    def __init__(self, patcher):
        object.__init__(self)
        self._patcher = patcher

    def __enter__(self):
        self._patcher.start()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self._patcher.stop()


class AsyncHTTPClientPatcher(Patcher):
    """This context manager provides an easy way to install a
    patch allowing the caller to determine the behavior of
    tornado.httpclient.AsyncHTTPClient.fetch().
    """

    def __init__(self, response):

        def fetch_patch(ahc, request, callback):
            callback(response)

        patcher = mock.patch(
            'tornado.httpclient.AsyncHTTPClient.fetch',
            fetch_patch)

        Patcher.__init__(self, patcher)


class AsyncEndToEndContainerRunnerPatcher(Patcher):
    """This context manager provides an easy way to install a
    patch allowing the caller to determine the behavior of
    AsyncEndToEndContainerRunner.create().
    """

    def __init__(self,
                 is_ok,
                 is_image_found=None,
                 exit_code=None,
                 stdout=None,
                 stderr=None):

        def create_patch(acr, callback):
            callback(is_ok, is_image_found, exit_code, stdout, stderr, acr)

        patcher = mock.patch(
            __name__ + '.AsyncEndToEndContainerRunner.create',
            create_patch)

        Patcher.__init__(self, patcher)


class WriteAndVerifyPatcher(Patcher):
    """This context manager provides an easy way to install a
    patch allowing the caller to determine the behavior of
    tor_async_util's write_and_verify().
    """

    def __init__(self, is_ok):

        def write_and_verify_patch(request_handler, body, schema):
            return is_ok

        patcher = mock.patch(
            'tor_async_util.RequestHandler.write_and_verify',
            write_and_verify_patch)

        Patcher.__init__(self, patcher)


class AsyncRequestHandlerTestCase(tornado.testing.AsyncHTTPTestCase):

    def assertDebugDetail(self, response, expected_value):
        """Assert a debug failure detail HTTP header appears in
        ```response``` with a value equal to ```expected_value```."""
        value = response.headers.get(
            tor_async_util.debug_details_header_name,
            None)
        self.assertIsNotNone(value)
        self.assertTrue(value.startswith("0x"))
        self.assertEqual(int(value, 16), expected_value)

    def assertNoDebugDetail(self, response):
        """Assert *no* debug failure detail HTTP header appears
        in ```response```."""
        value = response.headers.get(
            tor_async_util.debug_details_header_name,
            None)
        self.assertIsNone(value)

    def assertJsonDocumentResponse(self, response, expected_body):
        content_type = response.headers.get('Content-Type', None)
        self.assertIsNotNone(content_type)
        json_utf8_content_type_reg_ex = re.compile(
            '^\s*application/json(;\s+charset\=utf-{0,1}8){0,1}\s*$',
            re.IGNORECASE)
        self.assertIsNotNone(json_utf8_content_type_reg_ex.match(content_type))

        self.assertEqual(json.loads(response.body), expected_body)

    def assertEmptyJsonDocumentResponse(self, response):
        self.assertJsonDocumentResponse(response, {})


class TasksRequestHandlerTestCase(AsyncRequestHandlerTestCase):
    """Unit tests for TasksRequestHandler"""

    def get_app(self):
        handlers = [
            (
                TasksRequestHandler.url_spec,
                TasksRequestHandler
            ),
        ]
        return tornado.web.Application(handlers=handlers)

    def test_post_bad_request_body(self):
        headers = {
            'Content-Type': 'application/json; charset=utf-8',
        }
        body = {
        }
        response = self.fetch(
            '/v1.1/tasks',
            method='POST',
            headers=headers,
            body=json.dumps(body))

        self.assertEqual(response.code, httplib.BAD_REQUEST)

        self.assertDebugDetail(
            response,
            TasksRequestHandler.PDD_BAD_REQUEST_BODY)

        self.assertEmptyJsonDocumentResponse(response)

    def test_container_runner_error(self):
        with AsyncEndToEndContainerRunnerPatcher(is_ok=False):
            headers = {
                'Content-Type': 'application/json; charset=utf-8',
            }
            body = {
                'docker_image': 'ubuntu:latest',
                'cmd': [
                    'echo',
                    'hello world!!!',
                ],
            }
            response = self.fetch(
                '/v1.1/tasks',
                method='POST',
                headers=headers,
                body=json.dumps(body))

            self.assertEqual(response.code, httplib.INTERNAL_SERVER_ERROR)

            self.assertDebugDetail(
                response,
                TasksRequestHandler.PDD_ERROR_CREATING_RAW_CRAWL)

            self.assertEmptyJsonDocumentResponse(response)

    def test_image_not_found(self):
        with AsyncEndToEndContainerRunnerPatcher(is_ok=True, is_image_found=False):
            headers = {
                'Content-Type': 'application/json; charset=utf-8',
            }
            body = {
                'docker_image': 'ubuntu:latest',
                'cmd': [
                    'echo',
                    'hello world!!!',
                ],
            }
            response = self.fetch(
                '/v1.1/tasks',
                method='POST',
                headers=headers,
                body=json.dumps(body))

            self.assertEqual(response.code, httplib.NOT_FOUND)

            self.assertDebugDetail(
                response,
                TasksRequestHandler.PDD_IMAGE_NOT_FOUND)

            self.assertEmptyJsonDocumentResponse(response)

    def test_response_body_error(self):
        exit_code = 45
        stdout = uuid.uuid4().hex
        stderr = uuid.uuid4().hex
        with AsyncEndToEndContainerRunnerPatcher(is_ok=True,
                                                 is_image_found=True,
                                                 exit_code=exit_code,
                                                 stdout=stdout,
                                                 stderr=stderr):
            with WriteAndVerifyPatcher(is_ok=False):
                headers = {
                    'Content-Type': 'application/json; charset=utf-8',
                }
                body = {
                    'docker_image': 'ubuntu:latest',
                    'cmd': [
                        'echo',
                        'hello world!!!',
                    ],
                }
                response = self.fetch(
                    '/v1.1/tasks',
                    method='POST',
                    headers=headers,
                    body=json.dumps(body))

                self.assertEqual(response.code, httplib.INTERNAL_SERVER_ERROR)
                self.assertDebugDetail(response, TasksRequestHandler.PDD_BAD_RESPONSE_BODY)
                self.assertEmptyJsonDocumentResponse(response)

    def test_happy_path(self):
        exit_code = 45
        stdout = uuid.uuid4().hex
        stderr = uuid.uuid4().hex
        with AsyncEndToEndContainerRunnerPatcher(is_ok=True,
                                                 is_image_found=True,
                                                 exit_code=exit_code,
                                                 stdout=stdout,
                                                 stderr=stderr):
            headers = {
                'Content-Type': 'application/json; charset=utf-8',
            }
            body = {
                'docker_image': 'ubuntu:latest',
                'cmd': [
                    'echo',
                    'hello world!!!',
                ],
            }
            response = self.fetch(
                '/v1.1/tasks',
                method='POST',
                headers=headers,
                body=json.dumps(body))

            self.assertEqual(response.code, httplib.CREATED)
            self.assertNoDebugDetail(response)

            expected_body = {
                'exitCode': exit_code,
                'stdout': base64.b64encode(stdout),
                'stderr': base64.b64encode(stderr),
            }
            self.assertJsonDocumentResponse(response, expected_body)


class VersionRequestHandlerTestCase(AsyncRequestHandlerTestCase):
    """Unit tests for NoOpRequestHandler"""

    def get_app(self):
        handlers = [
            (
                VersionRequestHandler.url_spec,
                VersionRequestHandler
            ),
        ]
        return tornado.web.Application(handlers=handlers)

    def test_happy_path(self):
        response = self.fetch('/v1.1/_version', method='GET')

        self.assertEqual(response.code, httplib.OK)

        self.assertNoDebugDetail(response)

        self.assertEqual(
            response.headers['location'],
            response.effective_url)

        expected_response_body = {
            'version': ecs.__version__,
            'links': {
                'self': {
                    'href': response.effective_url,
                },
            },
        }
        self.assertJsonDocumentResponse(response, expected_response_body)


class NoOpRequestHandlerTestCase(AsyncRequestHandlerTestCase):
    """Unit tests for NoOpRequestHandler"""

    def get_app(self):
        handlers = [
            (
                NoOpRequestHandler.url_spec,
                NoOpRequestHandler
            ),
        ]
        return tornado.web.Application(handlers=handlers)

    def test_happy_path(self):
        response = self.fetch('/v1.1/_noop', method='GET')

        self.assertEqual(response.code, httplib.OK)

        self.assertNoDebugDetail(response)

        self.assertEqual(
            response.headers['location'],
            response.effective_url)

        expected_response_body = {
            'links': {
                'self': {
                    'href': response.effective_url,
                },
            },
        }
        self.assertJsonDocumentResponse(response, expected_response_body)


class HealthRequestHandlerTestCase(AsyncRequestHandlerTestCase):
    """Unit tests for HealthRequestHandler"""

    def get_app(self):
        handlers = [
            (
                HealthRequestHandler.url_spec,
                HealthRequestHandler
            ),
        ]
        return tornado.web.Application(handlers=handlers)

    def test_happy_path(self):
        response = self.fetch('/v1.1/_health', method='GET')

        self.assertEqual(response.code, httplib.OK)

        self.assertNoDebugDetail(response)

        self.assertEqual(
            response.headers['location'],
            response.effective_url)

        expected_response_body = {
            'status': 'green',
            'links': {
                'self': {
                    'href': response.effective_url,
                },
            },
        }
        self.assertJsonDocumentResponse(response, expected_response_body)
