"""This module contains all the request handlers for the
raw crawls service.
"""

import httplib
import logging

import tornado.web
import tor_async_util

import jsonschemas
from async_actions import AsyncEndToEndContainerRunner

_logger = logging.getLogger(__name__)


class CollectionRequestHandler(tor_async_util.RequestHandler):

    url_spec = r'/v1.0/tasks/?'

    # PDD = Post Debug Details
    PDD_BAD_REQUEST_BODY = 0x0001
    PDD_ERROR_CREATING_RAW_CRAWL = 0x0002
    PDD_BAD_RESPONSE_BODY = 0x0003

    @tornado.web.asynchronous
    def post(self):
        """This method implements the POST action on the /ecs endpoint."""
        schema = jsonschemas.create_raw_crawls_request
        request_body = self.get_json_request_body(schema=schema)
        if request_body is None:
            self.write_bad_request_response(type(self).PDD_BAD_REQUEST_BODY)
            self.finish()
            return

        docker_image = request_body['docker_image']
        tag = request_body['tag']
        cmd = request_body['cmd']
        acr = AsyncEndToEndContainerRunner(docker_image, tag, cmd)
        acr.create(self._on_acr_create_done)

    def _on_acr_create_done(self,
                            is_ok,
                            exit_code,
                            base64_encoded_stdout,
                            base64_encoded_stderr,
                            acr):
        if not is_ok:
            self.set_status(httplib.INTERNAL_SERVER_ERROR)
            self.add_debug_details(self.PDD_ERROR_CREATING_RAW_CRAWL)
            self.finish()
            return

        body = {
            'exitCode': exit_code,
            'base64EncodedStdOut': base64_encoded_stdout,
            'base64EncodedStdErr': base64_encoded_stderr,
        }

        schema = jsonschemas.create_raw_crawls_response
        if not self.write_and_verify(body, schema):
            self.set_status(httplib.INTERNAL_SERVER_ERROR)
            self.add_debug_details(self.PDD_BAD_RESPONSE_BODY)
            self.finish()
            return

        self.set_status(httplib.CREATED)
        self.finish()


class NoOpRequestHandler(tor_async_util.RequestHandler):

    url_spec = r'/v1.0/ecs/_noop'

    @tornado.web.asynchronous
    def get(self):
        tor_async_util.generate_noop_response(self)


class HealthRequestHandler(tor_async_util.RequestHandler):

    url_spec = r'/v1.0/_health'

    @tornado.web.asynchronous
    def get(self):
        tor_async_util.generate_health_check_response(self, tor_async_util.AsyncHealthCheck)
