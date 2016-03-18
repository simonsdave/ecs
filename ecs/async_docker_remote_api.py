"""This module contains async actions against the Docker Remote API."""

import base64
import datetime
import httplib
import json
import logging

import semantic_version
import tor_async_util
import tornado.httpclient
import tornado.ioloop

_logger = logging.getLogger(__name__)

remote_docker_api_endpoint = 'http://172.17.42.1:4243'

connect_timeout = 10.0

request_timeout = 5 * 60.0


def _write_http_client_response_to_log(response):
    tor_async_util.write_http_client_response_to_log(
        _logger,
        response,
        'Remote Docker API')


class AsyncHealthChecker(tor_async_util.AsyncAction):
    """Async'ly check the health of the Docker Remote API."""

    def __init__(self, async_state=None):
        tor_async_util.AsyncAction.__init__(self, async_state)

        self._callback = None

    def check(self, callback):
        assert self._callback is None
        self._callback = callback

        request = tornado.httpclient.HTTPRequest(
            '%s/version' % remote_docker_api_endpoint,
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
            details = {
                'connectivity': False,
            }
            self._call_callback(details)
            return

        response_body = json.loads(response.body)

        api_version = semantic_version.Version(response_body['ApiVersion'], partial=True)
        min_api_version = semantic_version.Version('1.18', partial=True)
        max_api_version = semantic_version.Version('1.20', partial=True)
        api_version_ok = (min_api_version <= api_version) and (api_version <= max_api_version)
        details = {
            'connectivity': True,
            'api version': api_version_ok,
        }
        self._call_callback(details)

    def _call_callback(self, details):
        assert self._callback is not None
        self._callback(details, self)
        self._callback = None


class AsyncImagePull(tor_async_util.AsyncAction):
    """Async'ly pull an image."""

    # PFD = Pull Failure Details
    PFD_OK = 0x0000
    PFD_ERROR = 0x0080
    PFD_ERROR_PULLING_IMAGE = PFD_ERROR | 0x0001
    PFD_IMAGE_NOT_FOUND = 0x0002

    def __init__(self,
                 docker_image,
                 tag,
                 email=None,
                 username=None,
                 password=None,
                 async_state=None):
        tor_async_util.AsyncAction.__init__(self, async_state)

        self.docker_image = docker_image
        self.tag = tag
        self.email = email
        self.username = username
        self.password = password

        self.pull_failure_detail = None

        self._image_not_found = False

        self._callback = None

    def pull(self, callback):
        assert self._callback is None
        self._callback = callback

        headers = {}

        if self.email:
            fmt = '{"username":"%s","password":"%s","auth":"","email":"%s"}'
            x_registry_auth_as_str = fmt % (
                self.username,
                self.password,
                self.email,
            )
            headers['X-Registry-Auth'] = base64.b64encode(x_registry_auth_as_str)

        url_fmt = '%s/images/create?fromImage=%s&tag=%s'
        request = tornado.httpclient.HTTPRequest(
            url_fmt % (remote_docker_api_endpoint, self.docker_image, self.tag),
            method='POST',
            headers=headers,
            allow_nonstandard_methods=True,
            connect_timeout=connect_timeout,
            request_timeout=request_timeout,
            streaming_callback=self._on_chunk)
        http_client = tornado.httpclient.AsyncHTTPClient()
        http_client.fetch(request, callback=self._on_http_client_fetch_done)

    def _on_chunk(self, chunk):
        #
        # network connectivity can generate a "no such host" error
        # that we'll choose to interpret as the requested image could
        # not be found
        #
        if 'no such host' in chunk:
            self._image_not_found = True
            return

        #
        # the not found error will be raised by the docker remote
        # API under one of two conditions 1/ the image really can't
        # be found or 2/ the request isn't authorized to access
        # the image
        #
        expected_error = '%s:%s not found' % (self.docker_image, self.tag)
        if expected_error in chunk:
            self._image_not_found = True
            return

        #
        # invalid image names generate a message that starts with
        # 'Invalid namespace name' or 'Invalid repository name' and
        # we'll treat this as an image
        # not found
        #
        if 'Invalid namespace name' in chunk:
            self._image_not_found = True
            return

        if 'Invalid repository name' in chunk:
            self._image_not_found = True
            return

        if 'repository name component must match' in chunk:
            self._image_not_found = True
            return

    def _on_http_client_fetch_done(self, response):
        _write_http_client_response_to_log(response)

        #
        # see '_on_chunk()' for the comments on why this is the
        # first statement to be executed in this method
        #
        if self._image_not_found:
            self._call_callback(type(self).PFD_IMAGE_NOT_FOUND)
            return

        if response.code != httplib.OK:
            self._call_callback(type(self).PFD_ERROR_PULLING_IMAGE)
            return

        self._call_callback(type(self).PFD_OK)

    def _call_callback(self, pull_failure_detail):
        assert self._callback is not None
        assert self.pull_failure_detail is None
        self.pull_failure_detail = pull_failure_detail
        is_ok = not bool(self.pull_failure_detail & type(self).PFD_ERROR)
        is_image_found = self.pull_failure_detail != type(self).PFD_IMAGE_NOT_FOUND if is_ok else None
        self._callback(is_ok, is_image_found, self)
        self._callback = None


class AsyncContainerCreate(tor_async_util.AsyncAction):
    """Async'ly create a container."""

    # CFD = Create Failure Details
    CFD_OK = 0x0000
    CFD_ERROR = 0x0080
    CFD_ERROR_CREATING_CONTAINER = CFD_ERROR | 0x0001

    def __init__(self, docker_image, tag, cmd, async_state=None):
        tor_async_util.AsyncAction.__init__(self, async_state)

        self.docker_image = docker_image
        self.tag = tag
        self.cmd = cmd

        self.create_failure_detail = None

        self._callback = None

    def create(self, callback):
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
            self._call_callback(type(self).CFD_ERROR_CREATING_CONTAINER)
            return

        response_body = json.loads(response.body)
        self._call_callback(type(self).CFD_OK, response_body['Id'])

    def _call_callback(self, create_failure_detail, container_id=None):
        assert self._callback is not None
        assert self.create_failure_detail is None
        self.create_failure_detail = create_failure_detail
        is_ok = not bool(self.create_failure_detail & type(self).CFD_ERROR)
        self._callback(is_ok, container_id, self)
        self._callback = None


class AsyncContainerStart(tor_async_util.AsyncAction):
    """Async'ly start a container."""

    # SFD = Start Failure Details
    SFD_OK = 0x0000
    SFD_ERROR = 0x0080
    SFD_ERROR_STARTING_CONTAINER = SFD_ERROR | 0x0001

    def __init__(self, container_id, async_state=None):
        tor_async_util.AsyncAction.__init__(self, async_state)

        self.container_id = container_id

        self.start_failure_detail = None

        self._callback = None

    def start(self, callback):
        assert self._callback is None
        self._callback = callback

        url_fmt = '%s/containers/%s/start'
        request = tornado.httpclient.HTTPRequest(
            url_fmt % (remote_docker_api_endpoint, self.container_id),
            method='POST',
            allow_nonstandard_methods=True,
            connect_timeout=connect_timeout,
            request_timeout=request_timeout)
        http_client = tornado.httpclient.AsyncHTTPClient()
        http_client.fetch(request, callback=self._on_http_client_fetch_done)

    def _on_http_client_fetch_done(self, response):
        _write_http_client_response_to_log(response)

        if response.code != httplib.NO_CONTENT:
            self._call_callback(type(self).SFD_ERROR_STARTING_CONTAINER)
            return

        self._call_callback(type(self).SFD_OK)

    def _call_callback(self, start_failure_detail):
        assert self._callback is not None
        assert self.start_failure_detail is None
        self.start_failure_detail = start_failure_detail
        is_ok = not bool(self.start_failure_detail & type(self).SFD_ERROR)
        self._callback(is_ok, self)
        self._callback = None


class AsyncContainerDelete(tor_async_util.AsyncAction):
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


class AsyncContainerStatus(tor_async_util.AsyncAction):
    """Async'ly wait for a container to exit and return the
    container's status.
    """

    # SFD = Status Failure Details
    SFD_OK = 0x0000
    SFD_ERROR = 0x0080
    SFD_ERROR_FETCHING_CONTAINER_STATUS = SFD_ERROR | 0x0001
    SFD_WAITED_TOO_LONG = SFD_ERROR | 0x0002

    def __init__(self, container_id, async_state=None):
        tor_async_util.AsyncAction.__init__(self, async_state)

        self.container_id = container_id

        self.fetch_failure_detail = None

        self._wait_times_in_ms = [250] * 4 * 10 + [1000] * 50 + [2000] * 30
        self._callback = None

    def fetch(self, callback):
        assert self._callback is None
        self._callback = callback

        self._fetch()

    def _fetch(self):
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
            self._call_callback(type(self).SFD_ERROR_FETCHING_CONTAINER_STATUS)
            return

        response_body = json.loads(response.body)
        state = response_body['State']
        if state['FinishedAt'] != '0001-01-01T00:00:00Z':
            self._call_callback(type(self).SFD_OK, state['ExitCode'])
            return

        if not self._wait_times_in_ms:
            self._call_callback(type(self).SFD_WAITED_TOO_LONG)
            return

        tornado.ioloop.IOLoop.current().add_timeout(
            datetime.timedelta(0, self._wait_times_in_ms.pop(0) / 1000.0, 0),
            self._fetch)

    def _call_callback(self, fetch_failure_detail, exit_code=None):
        assert self._callback is not None
        assert self.fetch_failure_detail is None
        self.fetch_failure_detail = fetch_failure_detail
        is_ok = not bool(self.fetch_failure_detail & type(self).SFD_ERROR)
        self._callback(is_ok, exit_code, self)
        self._callback = None


class AsyncContainerLogs(tor_async_util.AsyncAction):
    """Async'ly fetch a container's stdout and stderr.

    See API reference

        https://docs.docker.com/engine/reference/api/docker_remote_api_v1.18/#get-container-logs

    The implementation of this method is more complex that it should be
    because I was too lazy to figure out how to interpret the 8-byte header
    in the response.

    content type = application/octet-stream
    see https://github.com/docker/docker/issues/8223
    """

    # FFD = Delete Failure Details
    FFD_OK = 0x0000
    FFD_ERROR = 0x0080
    FFD_SOFT_ERROR = 0x0040
    FFD_CONTAINER_NOT_FOUND = FFD_SOFT_ERROR | 0x0001
    FFD_ERROR_FETCHING_CONTAINER_LOGS = FFD_ERROR | 0x0002

    def __init__(self, container_id, async_state=None):
        tor_async_util.AsyncAction.__init__(self, async_state)

        self.container_id = container_id

        self.fetch_failure_detail = None

        self._callback = None
        self._stdout = None
        self._stderr = None

    def fetch(self, callback):
        assert self._callback is None
        self._callback = callback

        self._fetch_logs(True, False)
        self._fetch_logs(False, True)

    def _fetch_logs(self, stdout, stderr):
        url = '%s/containers/%s/logs?stdout=%d&stderr=%d&timestamps=0&tail=all' % (
            remote_docker_api_endpoint,
            self.container_id,
            1 if stdout else 0,
            1 if stderr else 0,
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

        if response.code == httplib.NOT_FOUND:
            self._call_callback(type(self).FFD_CONTAINER_NOT_FOUND)
            return

        if response.code != httplib.OK:
            self._call_callback(type(self).FFD_ERROR_FETCHING_CONTAINER_LOGS)
            return

        self._call_callback(
            type(self).FFD_OK,
            response.body[8:] if 'stdout=1' in response.effective_url else None,
            response.body[8:] if 'stderr=1' in response.effective_url else None)

    def _call_callback(self, fetch_failure_detail, stdout=None, stderr=None):
        if self._callback is None:
            return

        self._stdout = stdout if stdout is not None else self._stdout
        self._stderr = stderr if stderr is not None else self._stderr

        self.fetch_failure_detail = fetch_failure_detail
        is_ok = not bool(self.fetch_failure_detail & type(self).FFD_ERROR)
        is_soft_error = bool(self.fetch_failure_detail & type(self).FFD_SOFT_ERROR)
        if not is_ok or is_soft_error or (self._stdout is not None and self._stderr is not None):
            self._callback(is_ok, self._stdout, self._stderr, self)
            self._callback = None
