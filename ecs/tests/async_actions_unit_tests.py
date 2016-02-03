"""This module contains a collection of unit tests which
validate the ..async_actions module.
"""

import httplib
import json
import unittest
import uuid

import mock

from ..async_actions import AsyncEndToEndContainerRunner
from ..async_actions import AsyncHealthChecker


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


class AsyncEndToEndContainerRunnerTestCase(unittest.TestCase):

    def test_ctr_without_async_state(self):
        docker_image = uuid.uuid4().hex
        tag = uuid.uuid4().hex
        cmd = uuid.uuid4().hex
        email = uuid.uuid4().hex
        username = uuid.uuid4().hex
        password = uuid.uuid4().hex

        aetecr = AsyncEndToEndContainerRunner(
            docker_image,
            tag,
            cmd,
            email,
            username,
            password)

        self.assertTrue(aetecr.docker_image is docker_image)
        self.assertTrue(aetecr.tag is tag)
        self.assertTrue(aetecr.cmd is cmd)
        self.assertTrue(aetecr.email is email)
        self.assertTrue(aetecr.username is username)
        self.assertTrue(aetecr.password is password)

        self.assertIsNone(aetecr.async_state)

    def test_ctr_with_async_state(self):
        docker_image = uuid.uuid4().hex
        tag = uuid.uuid4().hex
        cmd = uuid.uuid4().hex
        email = uuid.uuid4().hex
        username = uuid.uuid4().hex
        password = uuid.uuid4().hex
        async_state = uuid.uuid4().hex

        aetecr = AsyncEndToEndContainerRunner(
            docker_image,
            tag,
            cmd,
            email,
            username,
            password,
            async_state)

        self.assertTrue(aetecr.docker_image is docker_image)
        self.assertTrue(aetecr.tag is tag)
        self.assertTrue(aetecr.cmd is cmd)
        self.assertTrue(aetecr.email is email)
        self.assertTrue(aetecr.username is username)
        self.assertTrue(aetecr.password is password)
        self.assertTrue(aetecr.async_state is async_state)


class AsyncHealthCheckerTestCase(unittest.TestCase):

    def test_ctr_without_async_state(self):
        is_quick = uuid.uuid4().hex

        ahc = AsyncHealthChecker(is_quick)

        self.assertTrue(ahc.is_quick is is_quick)
        self.assertIsNone(ahc.async_state)

    def test_ctr_with_async_state(self):
        is_quick = uuid.uuid4().hex
        async_state = uuid.uuid4().hex

        ahc = AsyncHealthChecker(is_quick, async_state)

        self.assertTrue(ahc.is_quick is is_quick)
        self.assertTrue(ahc.async_state is async_state)

    def test_happy_path_on_is_quick_true(self):
        callback = mock.Mock()

        ahc = AsyncHealthChecker(True)
        ahc.check(callback)

        callback.assert_called_once_with(None, ahc)

    def test_failure_on_get_docker_remote_api_version(self):
        response = mock.Mock(
            code=httplib.INTERNAL_SERVER_ERROR,
            body=json.dumps({}),
            request_time=0.001,
            time_info={})

        with AsyncHTTPClientPatcher(response):
            callback = mock.Mock()
            ahc = AsyncHealthChecker(is_quick=False)
            ahc.check(callback)
            expected_response = {
                'docker remote api': {
                    'connectivity': False,
                }
            }
            callback.assert_called_once_with(expected_response, ahc)
