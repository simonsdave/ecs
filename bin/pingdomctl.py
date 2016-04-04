#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""This script automates the process of setting up Pingdom
checks against an ECS deployment.

Helpful references:

    * https://www.pingdom.com/resources/api
    * https://www.pingdom.com/features/api/documentation/
"""

import httplib
import os
import re
import sys

import requests

"""quick def'n"""
_quick_check_name = 'ECS Quick'
_quick_check_url = '/v1.1/_health?quick=true'
_quick_check_resolution = 1


"""Name of the slow health check."""
_slow_check_name = 'ECS'
_slow_check_url = '/v1.1/_health?quick=false'
_slow_check_resolution = 5


"""Used to parse the create command."""
_create_action_reg_ex = re.compile(
    r'^(create|c|crt)$',
    re.IGNORECASE)


"""Used to parse the delete command."""
_delete_action_reg_ex = re.compile(
    r'^(delete|r|rm|del)$',
    re.IGNORECASE)


def _usage():
    """Write a high level usage message to stderr."""
    fmt = 'usage: %s <username> <password> <app key> [create|delete] ...\n'
    msg = fmt % os.path.split(sys.argv[0])[1]
    sys.stderr.write(msg)


def _does_check_exist(username, password, app_key, check_name):
    """determine if the check named ```check_name``` exists
    and if it does, return the check's id otherwise
    return ```None```.
    """
    auth = requests.auth.HTTPBasicAuth(username, password)

    headers = {
        'App-Key': app_key,
    }

    response = requests.get(
        'https://api.pingdom.com/api/2.0/checks',
        auth=auth,
        headers=headers)

    if response.status_code != httplib.OK:
        msg = 'Couldn''t get checks (%s)\n' % response.status_code
        sys.stderr.write(msg)
        return False

    checks = response.json().get('checks', [])
    for check in checks:
        if check.get('name', '') == check_name:
            return check.get('id', None)

    return None


def _create_check(pingdom_username,
                  pingdom_password,
                  pingdom_app_key,
                  check_name,
                  ecs_host,
                  url,
                  resolution,
                  ecs_key,
                  ecs_secret):
    """create pingdom check."""

    #
    # if the check already exists fail
    #
    if _does_check_exist(pingdom_username, pingdom_password, app_key, check_name):
        msg = 'Check ''%s'' already exists\n' % check_name
        sys.stderr.write(msg)
        return False

    #
    # create the quick check
    #
    auth = requests.auth.HTTPBasicAuth(pingdom_username, pingdom_password)

    headers = {
        'App-Key': pingdom_app_key,
    }

    body = {
        'name': check_name,
        'resolution': resolution,
        'type': 'http',
        'url': url,
        'auth': '%s:%s' % (ecs_key, ecs_secret),
        'encryption': 'true',
        'host': ecs_host,
    }

    response = requests.post(
        'https://api.pingdom.com/api/2.0/checks',
        auth=auth,
        headers=headers,
        data=body)
    if response.status_code != httplib.OK:
        fmt = 'Error creating check ''%s'' (%s)\n'
        msg = fmt % (check_name, response.status_code),
        sys.stderr.write(msg)
        return False

    return True


def _create_checks(pingdom_username, pingdom_password, pingdom_app_key, args):
    """create all pingdom checks."""

    if 3 != len(args):
        fmt = (
            'usage: %s <username> <password> <app key> create '
            '<host> <key> <secret>\n'
        )
        msg = fmt % os.path.split(sys.argv[0])[1]
        sys.stderr.write(msg)
        return False

    ecs_host = args[0]
    ecs_key = args[1]
    ecs_secret = args[2]

    rv_quick = _create_check(
        pingdom_username,
        pingdom_password,
        pingdom_app_key,
        _quick_check_name,
        ecs_host,
        _quick_check_url,
        _quick_check_resolution,
        ecs_key,
        ecs_secret)

    rv_slow = _create_check(
        pingdom_username,
        pingdom_password,
        pingdom_app_key,
        _slow_check_name,
        ecs_host,
        _slow_check_url,
        _slow_check_resolution,
        ecs_key,
        ecs_secret)

    return rv_quick and rv_slow


def _delete_check(pingdom_username, pingdom_password, pingdom_app_key, check_name):
    """delete pingdom checks."""

    check_id = _does_check_exist(
        pingdom_username,
        pingdom_password,
        pingdom_app_key,
        check_name)
    if not check_id:
        return True

    auth = requests.auth.HTTPBasicAuth(pingdom_username, pingdom_password)

    headers = {
        'App-Key': pingdom_app_key,
    }

    response = requests.delete(
        'https://api.pingdom.com/api/2.0/checks/%s' % check_id,
        auth=auth,
        headers=headers)
    if response.status_code != httplib.OK:
        msg_fmt = 'Error deleting check ''%s'' (%s)\n'
        msg = msg_fmt % (check_name, response.status_code)
        sys.stderr.write(msg)
        return False

    return True


def _delete_checks(pingdom_username, pingdom_password, pingdom_app_key, args):
    """delete pingdom checks."""

    if 0 != len(args):
        fmt = 'usage: %s <username> <password> <app key> delete\n'
        msg = fmt % os.path.split(sys.argv[0])[1]
        sys.stderr.write(msg)
        return False

    rv_quick = _delete_check(
        pingdom_username,
        pingdom_password,
        pingdom_app_key,
        _quick_check_name)

    rv_slow = _delete_check(
        pingdom_username,
        pingdom_password,
        pingdom_app_key,
        _slow_check_name)

    return rv_quick and rv_slow


if __name__ == '__main__':

    if len(sys.argv) < 5:
        _usage()
        sys.exit(1)

    username = sys.argv[1]
    password = sys.argv[2]
    app_key = sys.argv[3]

    action = sys.argv[4]
    if _create_action_reg_ex.match(action):
        action_return_value = _create_checks(
            username,
            password,
            app_key,
            sys.argv[5:])
    else:
        if _delete_action_reg_ex.match(action):
            action_return_value = _delete_checks(
                username,
                password,
                app_key,
                sys.argv[5:])
        else:
            _usage()
            sys.exit(1)

    sys.exit(0 if action_return_value else 1)
