"""This module contains async actions."""

import logging
import uuid

import tor_async_util

import async_docker_remote_api

_logger = logging.getLogger(__name__)


class AsyncEndToEndContainerRunner(tor_async_util.AsyncAction):
    """Async'ly ...
    """

    # CFD = Create Failure Details
    CFD_OK = 0x0000
    CFD_ERROR = 0x0080
    CFD_ERROR_PULLING_IMAGE = CFD_ERROR | 0x0001
    CFD_IMAGE_NOT_FOUND = 0x0002
    CFD_ERROR_CREATING_CONTAINER = CFD_ERROR | 0x0003
    CFD_ERROR_STARTING_CONTAINER = CFD_ERROR | 0x0004
    CFD_WAITING_FOR_CONTAINER_TO_EXIT = CFD_ERROR | 0x0005
    CFD_ERROR_FETCHING_CONTAINER_LOGS = CFD_ERROR | 0x0006
    CFD_ERROR_DELETING_CONTAINER = CFD_ERROR | 0x0007

    def __init__(self,
                 docker_image,
                 cmd,
                 email,
                 username,
                 password,
                 async_state=None):
        tor_async_util.AsyncAction.__init__(self, async_state)

        self.docker_image = docker_image
        self.cmd = cmd
        self.email = email
        self.username = username
        self.password = password

        self.cid = uuid.uuid4().hex

        self.create_failure_detail = None

        self._container_id = None
        self._exit_code = None
        self._stdout = None
        self._stderr = None
        self._callback = None

    def create(self, callback):
        assert self._callback is None
        self._callback = callback

        fmt = '%s - attempting to pull image %s'
        _logger.info(fmt, self.cid, self.docker_image)
        aip = async_docker_remote_api.AsyncImagePull(
            self.docker_image,
            self.email,
            self.username,
            self.password)
        aip.pull(self._on_aip_pull_done)

    def _on_aip_pull_done(self, is_ok, is_image_found, api):
        if not is_ok:
            fmt = '%s - error pulling image %s'
            _logger.error(fmt, self.cid, self.docker_image)
            self._call_callback(type(self).CFD_ERROR_PULLING_IMAGE)
            return

        if not is_image_found:
            fmt = '%s - could not find image %s'
            _logger.info(fmt, self.cid, self.docker_image)
            self._call_callback(type(self).CFD_IMAGE_NOT_FOUND)
            return

        fmt = '%s - successfully pulled image %s'
        _logger.info(fmt, self.cid, self.docker_image)

        fmt = '%s - attempting to create container running %s - %s'
        _logger.info(fmt, self.cid, self.docker_image, self.cmd[0])
        acc = async_docker_remote_api.AsyncContainerCreate(
            self.docker_image,
            self.cmd)
        acc.create(self._on_acc_create_done)

    def _on_acc_create_done(self, is_ok, container_id, acc):
        if not is_ok:
            fmt = '%s - error creating container running %s - %s'
            _logger.error(fmt, self.cid, self.docker_image, self.cmd[0])
            self._call_callback(type(self).CFD_ERROR_CREATING_CONTAINER)
            return

        self._container_id = container_id

        fmt = '%s - successfully created container %s - %s - container ID = %s'
        _logger.info(fmt, self.cid, self.docker_image, self.cmd[0], self._container_id)

        fmt = '%s - attempting to start container - container ID = %s'
        _logger.info(fmt, self.cid, self._container_id)
        acs = async_docker_remote_api.AsyncContainerStart(self._container_id)
        acs.start(self._on_acs_start_done)

    def _on_acs_start_done(self, is_ok, acs):
        if not is_ok:
            fmt = '%s - error starting container - container ID = %s'
            _logger.error(fmt, self.cid, self._container_id)
            self._call_callback(type(self).CFD_ERROR_STARTING_CONTAINER)
            return

        fmt = '%s - successfully started container - container ID = %s'
        _logger.info(fmt, self.cid, self._container_id)

        fmt = '%s - attempting to get container\'s exit status - conatiner ID = %s'
        _logger.info(fmt, self.cid, self._container_id)
        acs = async_docker_remote_api.AsyncContainerStatus(self._container_id)
        acs.fetch(self._on_acs_fetch_done)

    def _on_acs_fetch_done(self, is_ok, exit_code, acew):
        if not is_ok:
            fmt = '%s - error getting container\'s exit status - conatiner ID = %s'
            _logger.error(fmt, self.cid, self._container_id)
            self._call_callback(type(self).CFD_WAITING_FOR_CONTAINER_TO_EXIT)
            return

        self._exit_code = exit_code

        fmt = '%s - got container\'s exit status (%d) - conatiner ID = %s'
        _logger.info(fmt, self.cid, self._exit_code, self._container_id)

        fmt = '%s - attempting to fetch container\'s logs - container ID = %s'
        _logger.info(fmt, self.cid, self._container_id)
        acl = async_docker_remote_api.AsyncContainerLogs(self._container_id)
        acl.fetch(self._on_acl_fetch_done)

    def _on_acl_fetch_done(self, is_ok, stdout, stderr, aclf):
        if not is_ok:
            fmt = '%s - error fetching container\'s logs - container ID = %s'
            _logger.error(fmt, self.cid, self._container_id)
            self._call_callback(type(self).CFD_ERROR_FETCHING_CONTAINER_LOGS)
            return

        self._stdout = stdout
        self._stderr = stderr

        fmt = '%s - successfully fetched container\'s logs - container ID = %s'
        _logger.info(fmt, self.cid, self._container_id)

        fmt = '%s - attempting to delete container - container ID = %s'
        _logger.info(fmt, self.cid, self._container_id)
        acd = async_docker_remote_api.AsyncContainerDelete(self._container_id)
        acd.delete(self._on_acd_delete_done)

    def _on_acd_delete_done(self, is_ok, adc):
        if not is_ok:
            fmt = '%s - error deleting container - container ID = %s'
            _logger.error(fmt, self.cid, self._container_id)
            self._call_callback(type(self).CFD_ERROR_DELETING_CONTAINER)
            return

        fmt = '%s - successfully deleted container - container ID = %s'
        _logger.info(fmt, self.cid, self._container_id)

        self._call_callback(type(self).CFD_OK, self._exit_code, self._stdout, self._stderr)

    def _call_callback(self, create_failure_detail, exit_code=None, stdout=None, stderr=None):
        assert self._callback is not None
        assert self.create_failure_detail is None
        self.create_failure_detail = create_failure_detail
        is_ok = not bool(self.create_failure_detail & type(self).CFD_ERROR)
        is_image_found = self.create_failure_detail != type(self).CFD_IMAGE_NOT_FOUND if is_ok else None
        self._callback(is_ok, is_image_found, exit_code, stdout, stderr, self)
        self._callback = None


class AsyncHealthChecker(tor_async_util.AsyncAction):
    """Async'ly check the service's health."""

    def __init__(self, is_quick, async_state=None):
        tor_async_util.AsyncAction.__init__(self, async_state)

        self.is_quick = is_quick

        self._callback = None

    def check(self, callback):
        assert self._callback is None
        self._callback = callback

        if self.is_quick:
            self._call_callback()
            return

        ahc = async_docker_remote_api.AsyncHealthChecker()
        ahc.check(self._on_docker_remote_api_ahc_fetch_done)

    def _on_docker_remote_api_ahc_fetch_done(self, details, ahc):
        self._call_callback({'docker remote api': details})

    def _call_callback(self, details=None):
        assert self._callback is not None
        self._callback(details, self)
        self._callback = None
