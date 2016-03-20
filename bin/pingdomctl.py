#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""This script automates the process of setting up Pingdom
checks against an ECS deployment.

Helpful references:

    * https://www.pingdom.com/features/api/documentation/
"""

import httplib
import os
import re
import sys

import requests

"""Name of the quick health check."""
_quick_check_name = 'ECS Quick'


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


def _create_checks(username, password, app_key, args):
    """create pingdom checks."""

    if 3 != len(args):
        fmt = (
            'usage: %s <username> <password> <app key> create '
            '<host> <key> <secret>\n'
        )
        msg = fmt % os.path.split(sys.argv[0])[1]
        sys.stderr.write(msg)
        return False

    #
    # extract values from ```args```
    #
    host = args[0]
    key = args[1]
    secret = args[2]

    #
    # if the check already exists fail
    #
    if _does_check_exist(username, password, app_key, _quick_check_name):
        msg = 'Check ''%s'' already exists\n' % _quick_check_name
        sys.stderr.write(msg)
        return False

    #
    # create the quick check
    #
    auth = requests.auth.HTTPBasicAuth(username, password)

    headers = {
        'App-Key': app_key,
    }

    body = {
        'name': _quick_check_name,
        'resolution': 1,
        'type': 'http',
        'url': '/v1.0/_health?quick=true',
        'auth': '%s:%s' % (key, secret),
        'encryption': 'true',
        'host': host,
#        'port': 443,
    }

    response = requests.post(
        'https://api.pingdom.com/api/2.0/checks',
        auth=auth,
        headers=headers,
        data=body)
    if response.status_code != httplib.OK:
        fmt = 'Error creating Couldn''t get checks (%s)\n'
        msg = fmt % response.status_code
        sys.stderr.write(msg)
        return False

    return True


def _delete_checks(username, password, app_key, args):
    """delete pingdom checks."""

    if 0 != len(args):
        fmt = 'usage: %s <username> <password> <app key> delete\n'
        msg = fmt % os.path.split(sys.argv[0])[1]
        sys.stderr.write(msg)
        return False

    #
    # if the check doesn't exist it's a shortcut to success
    #
    check_id = _does_check_exist(
        username,
        password,
        app_key,
        _quick_check_name)
    if not check_id:
        return True

    #
    # delete the quick check
    #
    auth = requests.auth.HTTPBasicAuth(username, password)

    headers = {
        'App-Key': app_key,
    }

    response = requests.delete(
        'https://api.pingdom.com/api/2.0/checks/%s' % check_id,
        auth=auth,
        headers=headers)
    if response.status_code != httplib.OK:
        msg_fmt = 'Error deleting checks (%s)\n'
        msg = msg_fmt % response.status_code
        sys.stderr.write(msg)
        return False

    return True


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
