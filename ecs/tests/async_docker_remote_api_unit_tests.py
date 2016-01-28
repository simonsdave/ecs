"""This module contains a collection of unit tests which
validate the ..async_docker_remote_api module.
"""

import unittest
import uuid

from ..async_actions import AsyncContainerStart


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
