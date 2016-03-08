"""This module contains a collection of unit tests which
validate the ..async_docker_remote_api module.
"""

import httplib
import json
import unittest
import uuid

import mock

from ..async_docker_remote_api import AsyncContainerCreate
from ..async_docker_remote_api import AsyncContainerDelete
from ..async_docker_remote_api import AsyncContainerLogs
from ..async_docker_remote_api import AsyncContainerStart
from ..async_docker_remote_api import AsyncContainerStatus
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

    def __init__(self, *args, **kwargs):
        chunks = kwargs.get('chunks', [])

        def fetch_patch(*args, **kwargs):
            streaming_callback = args[1].streaming_callback
            for chunk in chunks:
                streaming_callback(chunk)

            kwargs['callback'](self._responses.pop(0))

        patcher = mock.patch(
            'tornado.httpclient.AsyncHTTPClient.fetch',
            fetch_patch)

        Patcher.__init__(self, patcher)

        response = kwargs.get('response', None)
        if response is not None:
            self._responses = [response]
        else:
            self._responses = kwargs['responses'][:]


class AsyncActionIOLoopAddTimeoutPatcher(Patcher):
    """This context manager provides an easy way to install a
    patch allowing the caller to determine the behavior of
    tornado.httpclient.HTTPRequest.fetch().
    """

    def __init__(self):

        def add_timeout_patch(io_loop, deadline, callback, *args, **kwargs):
            callback(*args, **kwargs)

        patcher = mock.patch(
            'tornado.ioloop.IOLoop.add_timeout',
            add_timeout_patch)

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
        with AsyncHttpClientFetchPatcher(response=response):
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
        with AsyncHttpClientFetchPatcher(response=response):
            callback = mock.Mock()
            ahc = AsyncHealthChecker()
            ahc.check(callback)
            expected_response = {
                'connectivity': True,
                'api version': False,
            }
            callback.assert_called_once_with(expected_response, ahc)

    def test_happy_path(self):
        versions = {
            '1.17': False,
            '1.18': True,
            '1.19': True,
            '1.20': True,
            '1.21': False,
        }
        for (version, version_ok) in versions.iteritems():
            response = mock.Mock(
                code=httplib.OK,
                body=json.dumps({'ApiVersion': version}),
                time_info={},
                request_time=0.042,
                effective_url='http://www.bindle.com',
                request=mock.Mock(method='GET'))
            with AsyncHttpClientFetchPatcher(response=response):
                callback = mock.Mock()
                ahc = AsyncHealthChecker()
                ahc.check(callback)
                expected_response = {
                    'connectivity': True,
                    'api version': version_ok,
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
        with AsyncHttpClientFetchPatcher(response=response):
            callback = mock.Mock()
            aip = AsyncImagePull(
                docker_image=uuid.uuid4().hex,
                tag=uuid.uuid4().hex,
                email=uuid.uuid4().hex,
                username=uuid.uuid4().hex,
                password=uuid.uuid4().hex)
            aip.pull(callback)
            callback.assert_called_once_with(False, None, aip)
            self.assertEqual(aip.pull_failure_detail, type(aip).PFD_ERROR_PULLING_IMAGE)

    def test_image_not_found(self):
        docker_image = uuid.uuid4().hex
        tag = uuid.uuid4().hex

        response = mock.Mock(
            code=httplib.INTERNAL_SERVER_ERROR,
            body=None,
            time_info={},
            request_time=0.042,
            effective_url='http://www.bindle.com',
            request=mock.Mock(method='GET'))
        chunks = [
            (
                '{"errorDetail":{"message":"Error: image %s:%s not found"},'
                '"error":"Error: image %s:%s not found"}\n'
            ) % (docker_image, tag, docker_image, tag),
        ]
        with AsyncHttpClientFetchPatcher(response=response, chunks=chunks):
            callback = mock.Mock()
            aip = AsyncImagePull(
                docker_image=docker_image,
                tag=tag,
                email=uuid.uuid4().hex,
                username=uuid.uuid4().hex,
                password=uuid.uuid4().hex)
            aip.pull(callback)
            callback.assert_called_once_with(True, False, aip)
            self.assertEqual(aip.pull_failure_detail, type(aip).PFD_IMAGE_NOT_FOUND)

    def test_image_not_found_invalid_namespace_name(self):
        docker_image = uuid.uuid4().hex
        tag = uuid.uuid4().hex

        response = mock.Mock(
            code=httplib.INTERNAL_SERVER_ERROR,
            body=None,
            time_info={},
            request_time=0.042,
            effective_url='http://www.bindle.com',
            request=mock.Mock(method='GET'))
        chunks = [
            'Invalid namespace name (%s). Only [a-z0-9-_] are allowed\n' % docker_image,
        ]
        with AsyncHttpClientFetchPatcher(response=response, chunks=chunks):
            callback = mock.Mock()
            aip = AsyncImagePull(
                docker_image=docker_image,
                tag=tag,
                email=uuid.uuid4().hex,
                username=uuid.uuid4().hex,
                password=uuid.uuid4().hex)
            aip.pull(callback)
            callback.assert_called_once_with(True, False, aip)
            self.assertEqual(aip.pull_failure_detail, type(aip).PFD_IMAGE_NOT_FOUND)

    def test_image_not_found_invalid_repo_name(self):
        docker_image = uuid.uuid4().hex
        tag = uuid.uuid4().hex

        response = mock.Mock(
            code=httplib.INTERNAL_SERVER_ERROR,
            body=None,
            time_info={},
            request_time=0.042,
            effective_url='http://www.bindle.com',
            request=mock.Mock(method='GET'))
        chunks = [
            'Invalid repository name (%s), only [a-z0-9-_.] are allowed\n' % docker_image,
        ]
        with AsyncHttpClientFetchPatcher(response=response, chunks=chunks):
            callback = mock.Mock()
            aip = AsyncImagePull(
                docker_image=docker_image,
                tag=tag,
                email=uuid.uuid4().hex,
                username=uuid.uuid4().hex,
                password=uuid.uuid4().hex)
            aip.pull(callback)
            callback.assert_called_once_with(True, False, aip)
            self.assertEqual(aip.pull_failure_detail, type(aip).PFD_IMAGE_NOT_FOUND)

    def test_happy_path_with_creds(self):
        response = mock.Mock(
            code=httplib.OK,
            body=None,
            time_info={},
            request_time=0.042,
            effective_url='http://www.bindle.com',
            request=mock.Mock(method='GET'))
        chunks = [
            'ok',
            'great',
            'good',
        ]
        with AsyncHttpClientFetchPatcher(response=response, chunks=chunks):
            callback = mock.Mock()
            aip = AsyncImagePull(
                docker_image=uuid.uuid4().hex,
                tag=uuid.uuid4().hex,
                email=uuid.uuid4().hex,
                username=uuid.uuid4().hex,
                password=uuid.uuid4().hex)
            aip.pull(callback)
            callback.assert_called_once_with(True, True, aip)
            self.assertEqual(aip.pull_failure_detail, type(aip).PFD_OK)

    def test_happy_path_no_creds(self):
        response = mock.Mock(
            code=httplib.OK,
            body=None,
            time_info={},
            request_time=0.042,
            effective_url='http://www.bindle.com',
            request=mock.Mock(method='GET'))
        with AsyncHttpClientFetchPatcher(response=response):
            callback = mock.Mock()
            aip = AsyncImagePull(
                docker_image=uuid.uuid4().hex,
                tag=uuid.uuid4().hex)
            aip.pull(callback)
            callback.assert_called_once_with(True, True, aip)
            self.assertEqual(aip.pull_failure_detail, type(aip).PFD_OK)


class AsyncContainerCreateTestCase(unittest.TestCase):

    def test_ctr_without_async_state(self):
        docker_image = uuid.uuid4().hex
        tag = uuid.uuid4().hex
        cmd = uuid.uuid4().hex

        acc = AsyncContainerCreate(docker_image, tag, cmd)

        self.assertTrue(acc.docker_image is docker_image)
        self.assertTrue(acc.tag is tag)
        self.assertTrue(acc.cmd is cmd)
        self.assertIsNone(acc.async_state)

    def test_ctr_with_async_state(self):
        docker_image = uuid.uuid4().hex
        tag = uuid.uuid4().hex
        cmd = uuid.uuid4().hex
        async_state = uuid.uuid4().hex

        acc = AsyncContainerCreate(docker_image, tag, cmd, async_state)

        self.assertTrue(acc.docker_image is docker_image)
        self.assertTrue(acc.tag is tag)
        self.assertTrue(acc.cmd is cmd)
        self.assertTrue(acc.async_state is async_state)

    def test_create_error(self):
        response = mock.Mock(
            code=httplib.NOT_FOUND,
            body=None,
            time_info={},
            request_time=0.042,
            effective_url='http://www.bindle.com',
            request=mock.Mock(method='GET'))
        with AsyncHttpClientFetchPatcher(response=response):
            callback = mock.Mock()
            acc = AsyncContainerCreate(
                docker_image=uuid.uuid4().hex,
                tag=uuid.uuid4().hex,
                cmd=uuid.uuid4().hex)
            acc.create(callback)
            callback.assert_called_once_with(False, None, acc)
            self.assertEqual(
                acc.create_failure_detail,
                type(acc).CFD_ERROR_CREATING_CONTAINER)

    def test_happy_path(self):
        response = mock.Mock(
            code=httplib.CREATED,
            body=json.dumps({'Id': uuid.uuid4().hex}),
            time_info={},
            request_time=0.042,
            effective_url='http://www.bindle.com',
            request=mock.Mock(method='GET'))
        with AsyncHttpClientFetchPatcher(response=response):
            callback = mock.Mock()
            acc = AsyncContainerCreate(
                docker_image=uuid.uuid4().hex,
                tag=uuid.uuid4().hex,
                cmd=uuid.uuid4().hex)
            acc.create(callback)
            callback.assert_called_once_with(
                True,
                json.loads(response.body)['Id'],
                acc)
            self.assertEqual(acc.create_failure_detail, type(acc).CFD_OK)


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

    def test_start_error(self):
        response = mock.Mock(
            code=httplib.NOT_FOUND,
            body=None,
            time_info={},
            request_time=0.042,
            effective_url='http://www.bindle.com',
            request=mock.Mock(method='GET'))
        with AsyncHttpClientFetchPatcher(response=response):
            callback = mock.Mock()
            acs = AsyncContainerStart(container_id=uuid.uuid4().hex)
            acs.start(callback)
            callback.assert_called_once_with(False, acs)
            self.assertEqual(
                acs.start_failure_detail,
                type(acs).SFD_ERROR_STARTING_CONTAINER)

    def test_happy_path(self):
        response = mock.Mock(
            code=httplib.NO_CONTENT,
            body=None,
            time_info={},
            request_time=0.042,
            effective_url='http://www.bindle.com',
            request=mock.Mock(method='GET'))
        with AsyncHttpClientFetchPatcher(response=response):
            callback = mock.Mock()
            acs = AsyncContainerStart(container_id=uuid.uuid4().hex)
            acs.start(callback)
            callback.assert_called_once_with(True, acs)
            self.assertEqual(acs.start_failure_detail, type(acs).SFD_OK)


class AsyncContainerDeleteTestCase(unittest.TestCase):

    def test_ctr_without_async_state(self):
        container_id = uuid.uuid4().hex

        acd = AsyncContainerDelete(container_id)

        self.assertTrue(acd.container_id is container_id)
        self.assertIsNone(acd.async_state)

    def test_ctr_with_async_state(self):
        container_id = uuid.uuid4().hex
        async_state = uuid.uuid4().hex

        acd = AsyncContainerDelete(container_id, async_state)

        self.assertTrue(acd.container_id is container_id)
        self.assertTrue(acd.async_state is async_state)

    def test_delete_error(self):
        response = mock.Mock(
            code=httplib.NOT_FOUND,
            body=None,
            time_info={},
            request_time=0.042,
            effective_url='http://www.bindle.com',
            request=mock.Mock(method='GET'))
        with AsyncHttpClientFetchPatcher(response=response):
            callback = mock.Mock()
            acd = AsyncContainerDelete(container_id=uuid.uuid4().hex)
            acd.delete(callback)
            callback.assert_called_once_with(False, acd)
            self.assertEqual(
                acd.delete_failure_detail,
                type(acd).DFD_ERROR_DELETING_CONTAINER)

    def test_happy_path(self):
        response = mock.Mock(
            code=httplib.NO_CONTENT,
            body=None,
            time_info={},
            request_time=0.042,
            effective_url='http://www.bindle.com',
            request=mock.Mock(method='GET'))
        with AsyncHttpClientFetchPatcher(response=response):
            callback = mock.Mock()
            acd = AsyncContainerDelete(container_id=uuid.uuid4().hex)
            acd.delete(callback)
            callback.assert_called_once_with(True, acd)
            self.assertEqual(acd.delete_failure_detail, type(acd).DFD_OK)


class AsyncContainerStatusTestCase(unittest.TestCase):

    def test_ctr_without_async_state(self):
        container_id = uuid.uuid4().hex

        acs = AsyncContainerStatus(container_id)

        self.assertTrue(acs.container_id is container_id)
        self.assertIsNone(acs.async_state)

    def test_ctr_with_async_state(self):
        container_id = uuid.uuid4().hex
        async_state = uuid.uuid4().hex

        acs = AsyncContainerStatus(container_id, async_state)

        self.assertTrue(acs.container_id is container_id)
        self.assertTrue(acs.async_state is async_state)

    def test_error_fetching_container_status(self):
        response = mock.Mock(
            code=httplib.INTERNAL_SERVER_ERROR,
            body=None,
            time_info={},
            request_time=0.042,
            effective_url='http://www.bindle.com',
            request=mock.Mock(method='GET'))
        with AsyncHttpClientFetchPatcher(response=response):
            callback = mock.Mock()
            acs = AsyncContainerStatus(container_id=uuid.uuid4().hex)
            acs.fetch(callback)
            callback.assert_called_once_with(False, None, acs)
            self.assertEqual(
                acs.fetch_failure_detail,
                type(acs).SFD_ERROR_FETCHING_CONTAINER_STATUS)

    def test_waited_too_long_for_container_to_exit(self):
        responses = [mock.Mock(
            code=httplib.OK,
            body=json.dumps({
                'State': {
                    'FinishedAt': '0001-01-01T00:00:00Z',
                    'ExitCode': 0,
                },
            }),
            time_info={},
            request_time=0.042,
            effective_url='http://www.bindle.com',
            request=mock.Mock(method='GET'))] * 1000
        with AsyncHttpClientFetchPatcher(responses=responses):
            with AsyncActionIOLoopAddTimeoutPatcher():
                callback = mock.Mock()
                acs = AsyncContainerStatus(container_id=uuid.uuid4().hex)
                acs.fetch(callback)
                callback.assert_called_once_with(False, None, acs)
                self.assertEqual(acs.fetch_failure_detail, type(acs).SFD_WAITED_TOO_LONG)

    def test_happy_path(self):
        exit_code = 5
        response = mock.Mock(
            code=httplib.OK,
            body=json.dumps({
                'State': {
                    'FinishedAt': '9999-01-01T00:00:00Z',
                    'ExitCode': exit_code,
                },
            }),
            time_info={},
            request_time=0.042,
            effective_url='http://www.bindle.com',
            request=mock.Mock(method='GET'))
        with AsyncHttpClientFetchPatcher(response=response):
            callback = mock.Mock()
            acs = AsyncContainerStatus(container_id=uuid.uuid4().hex)
            acs.fetch(callback)
            callback.assert_called_once_with(True, exit_code, acs)
            self.assertEqual(acs.fetch_failure_detail, type(acs).SFD_OK)


class AsyncContainerLogsTestCase(unittest.TestCase):

    def test_ctr_without_async_state(self):
        container_id = uuid.uuid4().hex

        acl = AsyncContainerLogs(container_id)

        self.assertTrue(acl.container_id is container_id)
        self.assertIsNone(acl.async_state)

    def test_ctr_with_async_state(self):
        container_id = uuid.uuid4().hex
        async_state = uuid.uuid4().hex

        acl = AsyncContainerLogs(container_id, async_state)

        self.assertTrue(acl.container_id is container_id)
        self.assertTrue(acl.async_state is async_state)

    def test_container_not_found(self):
        response = mock.Mock(
            code=httplib.NOT_FOUND,
            body=None,
            time_info={},
            request_time=0.042,
            effective_url='http://www.bindle.com',
            request=mock.Mock(method='GET'))
        with AsyncHttpClientFetchPatcher(response=response):
            callback = mock.Mock()
            acl = AsyncContainerLogs(container_id=uuid.uuid4().hex)
            acl.fetch(callback)
            callback.assert_called_once_with(True, None, None, acl)
            self.assertEqual(
                acl.fetch_failure_detail,
                type(acl).FFD_CONTAINER_NOT_FOUND)

    def test_error_on_fetch(self):
        response = mock.Mock(
            code=httplib.INTERNAL_SERVER_ERROR,
            body=None,
            time_info={},
            request_time=0.042,
            effective_url='http://www.bindle.com',
            request=mock.Mock(method='GET'))
        with AsyncHttpClientFetchPatcher(response=response):
            callback = mock.Mock()
            acl = AsyncContainerLogs(container_id=uuid.uuid4().hex)
            acl.fetch(callback)
            callback.assert_called_once_with(False, None, None, acl)
            self.assertEqual(
                acl.fetch_failure_detail,
                type(acl).FFD_ERROR_FETCHING_CONTAINER_LOGS)

    def test_happy_path(self):
        header = '-' * 8
        stdout = 'something'
        stderr = 'out'
        # :TODO: sort out the stderr thing
        stderr = ''
        response = mock.Mock(
            code=httplib.OK,
            body=header + stdout + stderr,
            time_info={},
            request_time=0.042,
            effective_url='http://www.bindle.com',
            request=mock.Mock(method='GET'))
        with AsyncHttpClientFetchPatcher(response=response):
            callback = mock.Mock()
            acl = AsyncContainerLogs(container_id=uuid.uuid4().hex)
            acl.fetch(callback)
            callback.assert_called_once_with(True, stdout, stderr, acl)
            self.assertEqual(acl.fetch_failure_detail, type(acl).FFD_OK)
