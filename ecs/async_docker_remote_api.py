"""This module contains async actions against the Docker Remote API."""

import datetime
import httplib
import json
import logging

import tor_async_util
import tornado.httpclient
import tornado.ioloop

_logger = logging.getLogger(__name__)

remote_docker_api_endpoint = 'http://127.0.0.1:4243'

connect_timeout = 10.0

request_timeout = 5 * 60.0


def _write_http_client_response_to_log(response):
    tor_async_util.write_http_client_response_to_log(_logger, response, 'Remote Docker API')


class AsyncImagePuller(tor_async_util.AsyncAction):
    """Async'ly pull an image."""

    # PFD = Pull Failure Details
    PFD_OK = 0x0000
    PFD_ERROR = 0x0080
    PFD_ERROR_PULLING_IMAGE = PFD_ERROR | 0x0001

    def __init__(self, docker_image, tag, async_state=None):
        tor_async_util.AsyncAction.__init__(self, async_state)

        self.docker_image = docker_image
        self.tag = tag

        self.pull_failure_detail = None

        self._callback = None

    def pull(self, callback):
        assert self._callback is None
        self._callback = callback

        url_fmt = '%s/images/create?fromImage=%s&tag=%s'
        request = tornado.httpclient.HTTPRequest(
            url_fmt % (remote_docker_api_endpoint, self.docker_image, self.tag),
            method='POST',
            allow_nonstandard_methods=True,
            connect_timeout=connect_timeout,
            request_timeout=request_timeout,
            streaming_callback=self._on_chunk)
        http_client = tornado.httpclient.AsyncHTTPClient()
        http_client.fetch(request, callback=self._on_http_client_fetch_done)

    def _on_chunk(self, chunk):
        pass

    def _on_http_client_fetch_done(self, response):
        _write_http_client_response_to_log(response)

        if response.code != httplib.OK:
            self._call_callback(type(self).PFD_ERROR_PULLING_IMAGE)
            return

        self._call_callback(type(self).PFD_OK)

    def _call_callback(self, pull_failure_detail):
        assert self._callback is not None
        assert self.pull_failure_detail is None
        self.pull_failure_detail = pull_failure_detail
        is_ok = not bool(self.pull_failure_detail & type(self).PFD_ERROR)
        self._callback(is_ok, self)
        self._callback = None


class AsyncContainerRunner(tor_async_util.AsyncAction):
    """Async'ly run a container."""

    # RFD = Run Failure Details
    RFD_OK = 0x0000
    RFD_ERROR = 0x0080
    RFD_ERROR_CREATING_CONTAINER = RFD_ERROR | 0x0001
    RFD_ERROR_STARTING_CONTAINER = RFD_ERROR | 0x0002

    def __init__(self, docker_image, tag, cmd, async_state=None):
        tor_async_util.AsyncAction.__init__(self, async_state)

        self.docker_image = docker_image
        self.tag = tag
        self.cmd = cmd

        self.run_failure_detail = None

        self._container_id = None
        self._callback = None

    def run(self, callback):
        assert self._callback is None
        self._callback = callback

        body = {
            'Image': self.docker_image,
            'Tag': self.tag,
            'Cmd': self.cmd,
            'LogConfig': {
                'Type': 'json-file',
                'Config': {},
            },
        }

        headers = {
            'Content-Type': 'application/json',
        }

        request = tornado.httpclient.HTTPRequest(
            '%s/containers/create' % remote_docker_api_endpoint,
            method='POST',
            headers=tornado.httputil.HTTPHeaders(headers),
            body=json.dumps(body),
            connect_timeout=connect_timeout,
            request_timeout=request_timeout)
        http_client = tornado.httpclient.AsyncHTTPClient()
        http_client.fetch(
            request,
            callback=self._on_create_container_http_client_fetch_done)

    def _on_create_container_http_client_fetch_done(self, response):
        _write_http_client_response_to_log(response)

        if response.code != httplib.CREATED:
            self._call_callback(type(self).RFD_ERROR_CREATING_CONTAINER)
            return

        response_body = json.loads(response.body)
        self._container_id = response_body['Id']

        url_fmt = '%s/containers/%s/start'
        request = tornado.httpclient.HTTPRequest(
            url_fmt % (remote_docker_api_endpoint, self._container_id),
            method='POST',
            allow_nonstandard_methods=True,
            connect_timeout=connect_timeout,
            request_timeout=request_timeout)
        http_client = tornado.httpclient.AsyncHTTPClient()
        http_client.fetch(request, callback=self._on_start_container_http_client_fetch_done)

    def _on_start_container_http_client_fetch_done(self, response):
        _write_http_client_response_to_log(response)

        if response.code != httplib.NO_CONTENT:
            self._call_callback(type(self).RFD_ERROR_STARTING_CONTAINER)
            return

        self._call_callback(type(self).RFD_OK)

    def _call_callback(self, run_failure_detail):
        assert self._callback is not None
        assert self.run_failure_detail is None
        self.run_failure_detail = run_failure_detail
        is_ok = not bool(self.run_failure_detail & type(self).RFD_ERROR)
        self._callback(
            is_ok,
            self._container_id if is_ok else None,
            self)
        self._callback = None


class AsyncContainerDeleter(tor_async_util.AsyncAction):
    """Async'ly delete a container."""

    # RFD = Delete Failure Details
    DFD_OK = 0x0000
    DFD_ERROR = 0x0080
    DFD_ERROR_DELETING_CONTAINER = DFD_ERROR | 0x0001

    def __init__(self, container_id, async_state=None):
        tor_async_util.AsyncAction.__init__(self, async_state)

        self.container_id = container_id

        self.delete_failure_detail = None

        self._callback = None

    def delete(self, callback):
        assert self._callback is None
        self._callback = callback

        request = tornado.httpclient.HTTPRequest(
            '%s/containers/%s' % (remote_docker_api_endpoint, self.container_id),
            method='DELETE',
            connect_timeout=connect_timeout,
            request_timeout=request_timeout)
        http_client = tornado.httpclient.AsyncHTTPClient()
        http_client.fetch(
            request,
            callback=self._on_http_client_fetch_done)

    def _on_http_client_fetch_done(self, response):
        _write_http_client_response_to_log(response)

        if response.code != httplib.NO_CONTENT:
            self._call_callback(type(self).DFD_ERROR_DELETING_CONTAINER)
            return

        self._call_callback(type(self).DFD_OK)

    def _call_callback(self, delete_failure_detail):
        assert self._callback is not None
        assert self.delete_failure_detail is None
        self.delete_failure_detail = delete_failure_detail
        is_ok = not bool(self.delete_failure_detail & type(self).DFD_ERROR)
        self._callback(is_ok, self)
        self._callback = None


class AsyncContainerExitWaiter(tor_async_util.AsyncAction):
    """Async'ly wait for a container to exit."""

    # RFD = Delete Failure Details
    WFD_OK = 0x0000
    WFD_ERROR = 0x0080
    WFD_ERROR_FETCHING_CONTAINER_STATUS = WFD_ERROR | 0x0001
    WFD_WAITED_TOO_LONG = WFD_ERROR | 0x0002

    def __init__(self, container_id, wait_times_in_ms=None, async_state=None):
        tor_async_util.AsyncAction.__init__(self, async_state)

        self.container_id = container_id
        self.wait_times_in_ms = wait_times_in_ms if wait_times_in_ms else [250] * 4 * 10 + [1000] * 50 + [2000] * 30

        self.wait_failure_detail = None

        self._callback = None

    def wait(self, callback):
        assert self._callback is None
        self._callback = callback

        self._wait()

    def _wait(self):
        request = tornado.httpclient.HTTPRequest(
            '%s/containers/%s/json' % (remote_docker_api_endpoint, self.container_id),
            method='GET',
            connect_timeout=connect_timeout,
            request_timeout=request_timeout)
        http_client = tornado.httpclient.AsyncHTTPClient()
        http_client.fetch(
            request,
            callback=self._on_http_client_fetch_done)

    def _on_http_client_fetch_done(self, response):
        _write_http_client_response_to_log(response)

        if response.code != httplib.OK:
            self._call_callback(type(self).WFD_ERROR_FETCHING_CONTAINER_STATUS)
            return

        response_body = json.loads(response.body)
        state = response_body['State']
        if state['FinishedAt'] != '0001-01-01T00:00:00Z':
            self._call_callback(type(self).WFD_OK, state['ExitCode'])
            return

        if not self.wait_times_in_ms:
            self._call_callback(type(self).WFD_WAITED_TOO_LONG)
            return

        tornado.ioloop.IOLoop.current().add_timeout(
            datetime.timedelta(0, self.wait_times_in_ms.pop(0) / 1000.0, 0),
            self._wait)

    def _call_callback(self, wait_failure_detail, exit_code=None):
        assert self._callback is not None
        assert self.wait_failure_detail is None
        self.wait_failure_detail = wait_failure_detail
        is_ok = not bool(self.wait_failure_detail & type(self).WFD_ERROR)
        self._callback(is_ok, exit_code, self)
        self._callback = None


class AsyncContainerLogFetcher(tor_async_util.AsyncAction):
    """Async'ly fetch a container's stdout and stderr.

    See API reference

        https://docs.docker.com/engine/reference/api/docker_remote_api_v1.18/#get-container-logs
    """

    # FFD = Delete Failure Details
    FFD_OK = 0x0000
    FFD_ERROR = 0x0080
    FFD_ERROR_FETCHING_CONTAINER_LOGS = FFD_ERROR | 0x0001

    def __init__(self, container_id, async_state=None):
        tor_async_util.AsyncAction.__init__(self, async_state)

        self.container_id = container_id

        self.fetch_failure_detail = None

        self._callback = None

    def fetch(self, callback):
        assert self._callback is None
        self._callback = callback

        url = '%s/containers/%s/logs?stdout=1&stderr=1&timestamps=0&tail=all' % (
            remote_docker_api_endpoint,
            self.container_id,
        )
        request = tornado.httpclient.HTTPRequest(
            url,
            method='GET',
            connect_timeout=connect_timeout,
            request_timeout=request_timeout)
        http_client = tornado.httpclient.AsyncHTTPClient()
        http_client.fetch(
            request,
            callback=self._on_http_client_fetch_done)

    def _on_http_client_fetch_done(self, response):
        _write_http_client_response_to_log(response)

        if response.code != httplib.OK:
            self._call_callback(type(self).FFD_ERROR_FETCHING_CONTAINER_LOGS)
            return

        # content type = application/octet-stream
        # https://github.com/docker/docker/issues/8223
        self._call_callback(type(self).FFD_OK, response.body[8:], '')

    def _call_callback(self, fetch_failure_detail, stdout=None, stderr=None):
        assert self._callback is not None
        assert self.fetch_failure_detail is None
        self.fetch_failure_detail = fetch_failure_detail
        is_ok = not bool(self.fetch_failure_detail & type(self).FFD_ERROR)
        self._callback(is_ok, stdout, stderr, self)
        self._callback = None
