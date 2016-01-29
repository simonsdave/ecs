"""This module contains a collection of unit tests which
validate the ..async_actions module.
"""

import unittest
import uuid

from ..async_actions import AsyncEndToEndContainerRunner


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
