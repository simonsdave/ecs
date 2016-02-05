"""This module contains a collection of unit tests which
validate the ..async_docker_remote_api module.
"""

import httplib
import json
import unittest
import uuid

import mock

from ..async_docker_remote_api import AsyncContainerStart
from ..async_docker_remote_api import AsyncImagePull
from ..async_docker_remote_api import AsyncHealthChecker


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


class AsyncHttpClientFetchPatcher(Patcher):
    """This context manager provides an easy way to install a
    patch allowing the caller to determine the behavior of
    tornado.httpclient.HTTPRequest.fetch().
    """

    def __init__(self, response):

        def fetch_patch(*args, **kwargs):
            kwargs['callback'](response)

        patcher = mock.patch(
            'tornado.httpclient.AsyncHTTPClient.fetch',
            fetch_patch)

        Patcher.__init__(self, patcher)


class AsyncHealthCheckTestCase(unittest.TestCase):

    def test_ctr_without_async_state(self):
        ahc = AsyncHealthChecker()
        self.assertIsNone(ahc.async_state)

    def test_ctr_with_async_state(self):
        async_state = uuid.uuid4().hex
        ahc = AsyncHealthChecker(async_state)
        self.assertTrue(ahc.async_state is async_state)

    def test_connectivity_failure(self):
        response = mock.Mock(
            code=httplib.NOT_FOUND,
            body=json.dumps({}),
            time_info={},
            request_time=0.042,
            effective_url='http://www.bindle.com',
            request=mock.Mock(method='GET'))
        with AsyncHttpClientFetchPatcher(response):
            callback = mock.Mock()
            ahc = AsyncHealthChecker()
            ahc.check(callback)
            callback.assert_called_once_with({'connectivity': False}, ahc)

    def test_api_version_failure(self):
        response = mock.Mock(
            code=httplib.OK,
            body=json.dumps({'ApiVersion': '1.0'}),
            time_info={},
            request_time=0.042,
            effective_url='http://www.bindle.com',
            request=mock.Mock(method='GET'))
        with AsyncHttpClientFetchPatcher(response):
            callback = mock.Mock()
            ahc = AsyncHealthChecker()
            ahc.check(callback)
            expected_response = {
                'connectivity': True,
                'api version': False,
            }
            callback.assert_called_once_with(expected_response, ahc)

    def test_happy_path(self):
        response = mock.Mock(
            code=httplib.OK,
            body=json.dumps({'ApiVersion': '1.18'}),
            time_info={},
            request_time=0.042,
            effective_url='http://www.bindle.com',
            request=mock.Mock(method='GET'))
        with AsyncHttpClientFetchPatcher(response):
            callback = mock.Mock()
            ahc = AsyncHealthChecker()
            ahc.check(callback)
            expected_response = {
                'connectivity': True,
                'api version': True,
            }
            callback.assert_called_once_with(expected_response, ahc)


class AsyncImagePullTestCase(unittest.TestCase):

    def test_ctr_without_async_state(self):
        docker_image = uuid.uuid4().hex
        tag = uuid.uuid4().hex
        email = uuid.uuid4().hex
        username = uuid.uuid4().hex
        password = uuid.uuid4().hex

        aip = AsyncImagePull(
            docker_image,
            tag,
            email,
            username,
            password)

        self.assertTrue(aip.docker_image is docker_image)
        self.assertTrue(aip.tag is tag)
        self.assertTrue(aip.email is email)
        self.assertTrue(aip.username is username)
        self.assertTrue(aip.password is password)

        self.assertIsNone(aip.async_state)

    def test_ctr_with_async_state(self):
        docker_image = uuid.uuid4().hex
        tag = uuid.uuid4().hex
        email = uuid.uuid4().hex
        username = uuid.uuid4().hex
        password = uuid.uuid4().hex
        async_state = uuid.uuid4().hex

        aip = AsyncImagePull(
            docker_image,
            tag,
            email,
            username,
            password,
            async_state)

        self.assertTrue(aip.docker_image is docker_image)
        self.assertTrue(aip.tag is tag)
        self.assertTrue(aip.email is email)
        self.assertTrue(aip.username is username)
        self.assertTrue(aip.password is password)
        self.assertTrue(aip.async_state is async_state)

    def test_error_pulling_image(self):
        response = mock.Mock(
            code=httplib.NOT_FOUND,
            body=None,
            time_info={},
            request_time=0.042,
            effective_url='http://www.bindle.com',
            request=mock.Mock(method='GET'))
        with AsyncHttpClientFetchPatcher(response):
            callback = mock.Mock()
            aip = AsyncImagePull(
                docker_image=uuid.uuid4().hex,
                tag=uuid.uuid4().hex,
                email=uuid.uuid4().hex,
                username=uuid.uuid4().hex,
                password=uuid.uuid4().hex)
            aip.pull(callback)
            callback.assert_called_once_with(False, aip)
            self.assertEqual(aip.pull_failure_detail, type(aip).PFD_ERROR_PULLING_IMAGE)

    def test_happy_path(self):
        response = mock.Mock(
            code=httplib.OK,
            body=None,
            time_info={},
            request_time=0.042,
            effective_url='http://www.bindle.com',
            request=mock.Mock(method='GET'))
        with AsyncHttpClientFetchPatcher(response):
            callback = mock.Mock()
            aip = AsyncImagePull(
                docker_image=uuid.uuid4().hex,
                tag=uuid.uuid4().hex,
                email=uuid.uuid4().hex,
                username=uuid.uuid4().hex,
                password=uuid.uuid4().hex)
            aip.pull(callback)
            callback.assert_called_once_with(True, aip)
            self.assertEqual(aip.pull_failure_detail, type(aip).PFD_OK)


class AsyncContainerStartTestCase(unittest.TestCase):

    def test_ctr_without_async_state(self):
        container_id = uuid.uuid4().hex

        acs = AsyncContainerStart(container_id)

        self.assertTrue(acs.container_id is container_id)

        self.assertIsNone(acs.async_state)

    def test_ctr_with_async_state(self):
        container_id = uuid.uuid4().hex
        async_state = uuid.uuid4().hex

        acs = AsyncContainerStart(container_id, async_state)

        self.assertTrue(acs.container_id is container_id)
        self.assertTrue(acs.async_state is async_state)
