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
from .. import async_docker_remote_api   # noqa


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


class AsyncImagePullPatcher(Patcher):
    """This context manager provides an easy way to install a
    patch allowing the caller to determine the behavior of
    async_docker_remote_api.AsyncImagePull.pull().
    """

    def __init__(self, is_ok):

        def pull_patch(aip, callback):
            callback(is_ok, aip)

        patcher = mock.patch(
            __name__ + '.async_docker_remote_api.AsyncImagePull.pull',
            pull_patch)

        Patcher.__init__(self, patcher)


class AsyncContainerCreatePatcher(Patcher):
    """This context manager provides an easy way to install a
    patch allowing the caller to determine the behavior of
    async_docker_remote_api.AsyncContainerCreate.create().
    """

    def __init__(self, is_ok, container_id=None):

        def create_patch(acc, callback):
            callback(is_ok, container_id, acc)

        patcher = mock.patch(
            __name__ + '.async_docker_remote_api.AsyncContainerCreate.create',
            create_patch)

        Patcher.__init__(self, patcher)


class AsyncContainerStartPatcher(Patcher):
    """This context manager provides an easy way to install a
    patch allowing the caller to determine the behavior of
    async_docker_remote_api.AsyncContainerStart.start().
    """

    def __init__(self, is_ok):

        def start_patch(acs, callback):
            callback(is_ok, acs)

        patcher = mock.patch(
            __name__ + '.async_docker_remote_api.AsyncContainerStart.start',
            start_patch)

        Patcher.__init__(self, patcher)


class AsyncContainerStatusPatcher(Patcher):
    """This context manager provides an easy way to install a
    patch allowing the caller to determine the behavior of
    async_docker_remote_api.AsyncContainerStatus.fetch().
    """

    def __init__(self, is_ok, exit_code=None):

        def fetch_patch(acs, callback):
            callback(is_ok, exit_code, acs)

        patcher = mock.patch(
            __name__ + '.async_docker_remote_api.AsyncContainerStatus.fetch',
            fetch_patch)

        Patcher.__init__(self, patcher)


class AsyncContainerLogsPatcher(Patcher):
    """This context manager provides an easy way to install a
    patch allowing the caller to determine the behavior of
    async_docker_remote_api.AsyncContainerLogs.fetch().
    """

    def __init__(self, is_ok, stdout=None, stderr=None):

        def fetch_patch(acl, callback):
            callback(is_ok, stdout, stderr, acl)

        patcher = mock.patch(
            __name__ + '.async_docker_remote_api.AsyncContainerLogs.fetch',
            fetch_patch)

        Patcher.__init__(self, patcher)


class AsyncContainerDeletePatcher(Patcher):
    """This context manager provides an easy way to install a
    patch allowing the caller to determine the behavior of
    async_docker_remote_api.AsyncContainerDelete.fetch().
    """

    def __init__(self, is_ok):

        def delete_patch(acd, callback):
            callback(is_ok, acd)

        patcher = mock.patch(
            __name__ + '.async_docker_remote_api.AsyncContainerDelete.delete',
            delete_patch)

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

    def test_error_pulling_image(self):
        with AsyncImagePullPatcher(is_ok=False):
            callback = mock.Mock()
            aetecr = AsyncEndToEndContainerRunner(
                docker_image=uuid.uuid4().hex,
                tag=uuid.uuid4().hex,
                cmd=uuid.uuid4().hex,
                email=uuid.uuid4().hex,
                username=uuid.uuid4().hex,
                password=uuid.uuid4().hex)
            aetecr.create(callback)
            callback.assert_called_once_with(
                False,
                None,
                None,
                None,
                aetecr)
            self.assertEqual(
                aetecr.create_failure_detail,
                type(aetecr).CFD_ERROR_PULLING_IMAGE)

    def test_error_creating_container(self):
        with AsyncImagePullPatcher(is_ok=True):
            with AsyncContainerCreatePatcher(is_ok=False):
                callback = mock.Mock()
                aetecr = AsyncEndToEndContainerRunner(
                    docker_image=uuid.uuid4().hex,
                    tag=uuid.uuid4().hex,
                    cmd=uuid.uuid4().hex,
                    email=uuid.uuid4().hex,
                    username=uuid.uuid4().hex,
                    password=uuid.uuid4().hex)
                aetecr.create(callback)
                callback.assert_called_once_with(
                    False,
                    None,
                    None,
                    None,
                    aetecr)
                self.assertEqual(
                    aetecr.create_failure_detail,
                    type(aetecr).CFD_ERROR_CREATING_CONTAINER)

    def test_error_starting_container(self):
        with AsyncImagePullPatcher(is_ok=True):
            with AsyncContainerCreatePatcher(is_ok=True, container_id=uuid.uuid4().hex):
                with AsyncContainerStartPatcher(is_ok=False):
                    callback = mock.Mock()
                    aetecr = AsyncEndToEndContainerRunner(
                        docker_image=uuid.uuid4().hex,
                        tag=uuid.uuid4().hex,
                        cmd=uuid.uuid4().hex,
                        email=uuid.uuid4().hex,
                        username=uuid.uuid4().hex,
                        password=uuid.uuid4().hex)
                    aetecr.create(callback)
                    callback.assert_called_once_with(
                        False,
                        None,
                        None,
                        None,
                        aetecr)
                    self.assertEqual(
                        aetecr.create_failure_detail,
                        type(aetecr).CFD_ERROR_STARTING_CONTAINER)

    def test_error_getting_container_status(self):
        with AsyncImagePullPatcher(is_ok=True):
            with AsyncContainerCreatePatcher(is_ok=True, container_id=uuid.uuid4().hex):
                with AsyncContainerStartPatcher(is_ok=True):
                    with AsyncContainerStatusPatcher(is_ok=False):
                        callback = mock.Mock()
                        aetecr = AsyncEndToEndContainerRunner(
                            docker_image=uuid.uuid4().hex,
                            tag=uuid.uuid4().hex,
                            cmd=uuid.uuid4().hex,
                            email=uuid.uuid4().hex,
                            username=uuid.uuid4().hex,
                            password=uuid.uuid4().hex)
                        aetecr.create(callback)
                        callback.assert_called_once_with(
                            False,
                            None,
                            None,
                            None,
                            aetecr)
                        self.assertEqual(
                            aetecr.create_failure_detail,
                            type(aetecr).CFD_WAITING_FOR_CONTAINER_TO_EXIT)

    def test_happy_path(self):
        exit_code = 0
        stdout = uuid.uuid4().hex
        stderr = uuid.uuid4().hex
        with AsyncImagePullPatcher(is_ok=True):
            with AsyncContainerCreatePatcher(is_ok=True, container_id=uuid.uuid4().hex):
                with AsyncContainerStartPatcher(is_ok=True):
                    with AsyncContainerStatusPatcher(is_ok=True, exit_code=exit_code):
                        with AsyncContainerLogsPatcher(is_ok=True, stdout=stdout, stderr=stderr):
                            with AsyncContainerDeletePatcher(is_ok=True):
                                callback = mock.Mock()
                                aetecr = AsyncEndToEndContainerRunner(
                                    docker_image=uuid.uuid4().hex,
                                    tag=uuid.uuid4().hex,
                                    cmd=uuid.uuid4().hex,
                                    email=uuid.uuid4().hex,
                                    username=uuid.uuid4().hex,
                                    password=uuid.uuid4().hex)
                                aetecr.create(callback)
                                callback.assert_called_once_with(
                                    True,
                                    exit_code,
                                    stdout,
                                    stderr,
                                    aetecr)
                                self.assertEqual(
                                    aetecr.create_failure_detail,
                                    type(aetecr).CFD_OK)


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
