"""This module contains all the request handlers for the
ephemeral container service.
"""

import base64
import httplib
import logging

import tornado.web
import tor_async_util

import jsonschemas
import async_actions

_logger = logging.getLogger(__name__)


class TasksRequestHandler(tor_async_util.RequestHandler):

    url_spec = r'/v1.0/tasks/?'

    # PDD = Post Debug Details
    PDD_BAD_REQUEST_BODY = 0x0001
    PDD_ERROR_CREATING_RAW_CRAWL = 0x0002
    PDD_BAD_RESPONSE_BODY = 0x0003

    @tornado.web.asynchronous
    def post(self):
        """This method implements the POST action on the /ecs endpoint."""
        request_body = self.get_json_request_body(schema=jsonschemas.create_tasks_request)
        if request_body is None:
            self.write_bad_request_response(type(self).PDD_BAD_REQUEST_BODY)
            self.finish()
            return

        creds = request_body.get('creds', {})
        acr = async_actions.AsyncEndToEndContainerRunner(
            request_body['docker_image'],
            request_body['tag'],
            request_body['cmd'],
            creds.get('email', None),
            creds.get('username', None),
            creds.get('password', None))
        acr.create(self._on_acr_create_done)

    def _on_acr_create_done(self, is_ok, exit_code, stdout, stderr, acr):
        if not is_ok:
            self.add_debug_details(self.PDD_ERROR_CREATING_RAW_CRAWL)
            self.write_error(httplib.INTERNAL_SERVER_ERROR)
            self.finish()
            return

        body = {
            'exitCode': exit_code,
            'stdout': base64.b64encode(stdout),
            'stderr': base64.b64encode(stderr),
        }

        if not self.write_and_verify(body, jsonschemas.create_tasks_response):
            self.add_debug_details(self.PDD_BAD_RESPONSE_BODY)
            self.write_error(httplib.INTERNAL_SERVER_ERROR)
            self.finish()
            return

        self.set_status(httplib.CREATED)
        self.finish()


class NoOpRequestHandler(tor_async_util.RequestHandler):

    url_spec = r'/v1.0/_noop'

    @tornado.web.asynchronous
    def get(self):
        tor_async_util.generate_noop_response(self)


class HealthRequestHandler(tor_async_util.RequestHandler):

    url_spec = r'/v1.0/_health'

    @tornado.web.asynchronous
    def get(self):
        tor_async_util.generate_health_check_response(self, async_actions.AsyncHealthChecker)
