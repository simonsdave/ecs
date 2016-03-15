#!/usr/bin/env python
"""Mainline for the ECS."""

import logging
import optparse
import time

import tor_async_util
import tornado.httpclient
import tornado.httpserver
import tornado.web

from ecs.request_handlers import HealthRequestHandler
from ecs.request_handlers import NoOpRequestHandler
from ecs.request_handlers import TasksRequestHandler
from ecs.request_handlers import VersionRequestHandler
from ecs import async_docker_remote_api

_logger = logging.getLogger(__name__)


class _CommandLineParser(optparse.OptionParser):
    """Used to parse command line arguments."""

    def __init__(self):
        optparse.OptionParser.__init__(
            self,
            'usage: %prog [options]',
            description='This service implements ECS\' RESTful API')

        default = '~/.ecs/config'
        help = 'config - default = %s' % default
        self.add_option(
            '--config',
            action='store',
            dest='config',
            default=default,
            type='string',
            help=help)


if __name__ == '__main__':
    #
    # parse command line args ...
    #
    clp = _CommandLineParser()
    (clo, cla) = clp.parse_args()

    #
    # setup configuration ...
    #
    tor_async_util.Config.instance = tor_async_util.Config(clo.config)

    #
    # configure logging ...
    #
    config_section = 'ecs'

    logging_level = tor_async_util.Config.instance.get_logging_level(
        config_section,
        'log_level')

    logging.Formatter.converter = time.gmtime   # remember gmt = utc
    logging.basicConfig(
        level=logging_level,
        datefmt='%Y-%m-%dT%H:%M:%S',
        format='%(asctime)s.%(msecs)03d+00:00 %(levelname)s %(module)s %(message)s')

    #
    # configure tornado ...
    #
    tor_async_util.install_sigint_handler()

    async_http_client = 'tornado.curl_httpclient.CurlAsyncHTTPClient'
    max_concurrent_executing_http_requests = tor_async_util.Config.instance.get_int(
        config_section,
        'max_concurrent_executing_http_requests',
        10)
    tornado.httpclient.AsyncHTTPClient.configure(
        async_http_client,
        max_clients=max_concurrent_executing_http_requests)

    if not tor_async_util.is_libcurl_compiled_with_async_dns_resolver():
        msg = (
            'libcurl does not appear to have been '
            'compiled with async dns resolve which '
            'may result in timeouts on async requests'
        )
        _logger.warning(msg)

    handlers = [
        (
            TasksRequestHandler.url_spec,
            TasksRequestHandler
        ),
        (
            VersionRequestHandler.url_spec,
            VersionRequestHandler
        ),
        (
            NoOpRequestHandler.url_spec,
            NoOpRequestHandler
        ),
        (
            HealthRequestHandler.url_spec,
            HealthRequestHandler
        ),
    ]

    settings = {
        'default_handler_class': tor_async_util.DefaultRequestHandler,
    }

    app = tornado.web.Application(handlers=handlers, **settings)

    address = tor_async_util.Config.instance.get(
        config_section,
        'address',
        '127.0.0.1')
    port = tor_async_util.Config.instance.get_int(
        config_section,
        'port',
        8448)

    async_docker_remote_api.remote_docker_api_endpoint = tor_async_util.Config.instance.get(
        config_section,
        'docker_remote_api',
        'http://172.17.42.1:4243')

    #
    # log a startup message - note this is done before
    # starting the http listener in case the listener
    # throws an exception on startup in which case it
    # can be very useful for debugging the exception
    # to have this basic info available
    #
    fmt = (
        'read config from \'{config_file}[{config_section}]\', '
        'listening on http://{address}:{port:d} '
        'with logging level set to {logging_level} and '
        'talking to the Docker Remote API on {docker_remote_api}'
    )
    args = {
        'config_file': tor_async_util.Config.instance.config_file,
        'config_section': config_section,
        'address': address,
        'port': port,
        'logging_level': logging.getLevelName(logging.getLogger().getEffectiveLevel()),
        'docker_remote_api': async_docker_remote_api.remote_docker_api_endpoint,
    }
    _logger.info(fmt.format(**args))

    #
    # start listening for and processing requests ...
    #
    http_server = tornado.httpserver.HTTPServer(app, xheaders=True)
    http_server.listen(port, address=address)

    tornado.ioloop.IOLoop.instance().start()
