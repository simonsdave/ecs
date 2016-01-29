"""This module contains a collection of unit tests which
validate the ..async_docker_remote_api module.
"""

import unittest
import uuid

import mock

from ..async_docker_remote_api import AsyncContainerStart
from ..async_docker_remote_api import AsyncImagePull
from ..async_docker_remote_api import AsyncHealthChecker


class AsyncHealthCheckTestCase(unittest.TestCase):

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

    def test_quick_check(self):
        callback = mock.Mock()
        ahc = AsyncHealthChecker(True)
        ahc.check(callback)
        callback.assert_called_once_with(True, None, ahc)


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
