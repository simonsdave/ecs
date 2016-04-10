"""This module contains a collection of unit tests which
validate ..main
"""

from ConfigParser import ConfigParser
import logging
import os
import sys
import tempfile
import unittest

import mock
import tornado.httpserver

from ..main import Main
from .. import async_docker_remote_api


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


class IsLibcurlCompiledWithAsyncDNSResolverPatcher(Patcher):
    """This context manager provides an easy way to install a
    patch allowing the caller to determine the behavior of
    tor_async_util.is_libcurl_compiled_with_async_dns_resolver().
    """

    def __init__(self, response):

        def the_patch(*args, **kwargs):
            return response

        patcher = mock.patch(
            'tor_async_util.is_libcurl_compiled_with_async_dns_resolver',
            the_patch)

        Patcher.__init__(self, patcher)


class TornadoIOLoopInstancePatcher(Patcher):

    def __init__(self):

        def the_patch(*args, **kwargs):
            pass

        assert type(tornado.ioloop.IOLoop.instance()) == tornado.platform.epoll.EPollIOLoop

        patcher = mock.patch(
            'tornado.platform.epoll.EPollIOLoop.start',
            the_patch)

        Patcher.__init__(self, patcher)


class TornadoHttpServerListenPatcher(Patcher):

    def __init__(self):

        def the_patch(*args, **kwargs):
            pass

        patcher = mock.patch(
            'tornado.httpserver.HTTPServer.listen',
            the_patch)

        Patcher.__init__(self, patcher)


class ServiceConfigFile(object):

    def __init__(self, section):
        object.__init__(self)

        self.section = section

        self.address = '1.1.1.1'
        self.port = 5555
        self.logging_level = logging.DEBUG
        self.max_concurrent_executing_http_requests = 250
        self.docker_remote_api = 'http://2.2.2.2:6666'
        self.docker_remote_api_connect_timeout = 50
        self.docker_remote_api_request_timeout = 500

        self.filename = None

    def __str__(self):
        return str(self.filename)

    def __enter__(self):
        assert self.filename is None

        cp = ConfigParser()
        cp.add_section(self.section)

        cp.set(self.section, 'address', self.address)
        cp.set(self.section, 'port', self.port)
        cp.set(self.section, 'log_level', logging.getLevelName(self.logging_level))
        cp.set(self.section, 'max_concurrent_executing_http_requests', self.max_concurrent_executing_http_requests)
        cp.set(self.section, 'docker_remote_api', self.docker_remote_api)
        cp.set(self.section, 'docker_remote_api_connect_timeout', self.docker_remote_api_connect_timeout)
        cp.set(self.section, 'docker_remote_api_request_timeout', self.docker_remote_api_request_timeout)

        self.filename = tempfile.mktemp()
        with open(self.filename, 'w+') as fp:
            cp.write(fp)

        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self.filename:
            if os.path.exists(self.filename):
                os.unlink(self.filename)
                self.filename = None


class SysDotArgcPatcher(object):

    def __init__(self, sys_dot_argv):
        object.__init__(self)

        self.sys_dot_argv = sys_dot_argv
        self._old_sys_dot_argv = None

    def __enter__(self):
        assert self._old_sys_dot_argv is None

        self._old_sys_dot_argv = None
        sys.argv = self.sys_dot_argv

        return self

    def __exit__(self, exc_type, exc_value, traceback):
        sys.argv = self._old_sys_dot_argv
        self._old_sys_dot_argv = None


class MainTestCase(unittest.TestCase):

    def test_libcurl_async_dns_resolver(self):
        main = Main()
        with ServiceConfigFile(main.config_section) as service_config_file:
            sys_dot_arv = [
                'service',
                '--config=%s' % service_config_file.filename,
            ]
            with SysDotArgcPatcher(sys_dot_arv):
                with TornadoHttpServerListenPatcher():
                    with TornadoIOLoopInstancePatcher():
                        with IsLibcurlCompiledWithAsyncDNSResolverPatcher(True):
                            main.configure()
                        with IsLibcurlCompiledWithAsyncDNSResolverPatcher(False):
                            main.configure()

    def test_configuration(self):
        main = Main()
        with ServiceConfigFile(main.config_section) as service_config_file:

            self.assertNotEqual(
                service_config_file.address,
                main.address)

            self.assertNotEqual(
                service_config_file.port,
                main.port)

            self.assertNotEqual(
                service_config_file.logging_level,
                main.logging_level)

            self.assertNotEqual(
                service_config_file.max_concurrent_executing_http_requests,
                main.max_concurrent_executing_http_requests)

            self.assertNotEqual(
                service_config_file.docker_remote_api,
                async_docker_remote_api.docker_remote_api_endpoint)

            self.assertNotEqual(
                service_config_file.docker_remote_api_connect_timeout,
                async_docker_remote_api.connect_timeout)

            self.assertNotEqual(
                service_config_file.docker_remote_api_request_timeout,
                async_docker_remote_api.request_timeout)

            sys_dot_arv = [
                'service',
                '--config=%s' % service_config_file.filename,
            ]
            with SysDotArgcPatcher(sys_dot_arv):
                with TornadoHttpServerListenPatcher():
                    with TornadoIOLoopInstancePatcher():
                        main.configure()

                        self.assertEqual(
                            service_config_file.address,
                            main.address)

                        self.assertEqual(
                            service_config_file.port,
                            main.port)

                        self.assertEqual(
                            service_config_file.logging_level,
                            main.logging_level)

                        self.assertEqual(
                            service_config_file.max_concurrent_executing_http_requests,
                            main.max_concurrent_executing_http_requests)

                        self.assertEqual(
                            service_config_file.docker_remote_api,
                            async_docker_remote_api.docker_remote_api_endpoint)

                        self.assertEqual(
                            service_config_file.docker_remote_api_connect_timeout,
                            async_docker_remote_api.connect_timeout)

                        self.assertEqual(
                            service_config_file.docker_remote_api_request_timeout,
                            async_docker_remote_api.request_timeout)

    def test_happy_path(self):
        main = Main()
        with ServiceConfigFile(main.config_section) as service_config_file:
            sys_dot_arv = [
                'service',
                '--config=%s' % service_config_file.filename,
            ]
            with SysDotArgcPatcher(sys_dot_arv):
                with TornadoHttpServerListenPatcher():
                    with TornadoIOLoopInstancePatcher():
                        main.configure()
                        main.listen()
