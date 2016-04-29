#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""This script explores how to calculate ECS availability.

Useful references:

    * https://www.pingdom.com/resources/api
    * https://www.pingdom.com/features/api/documentation/
"""

import httplib
import os
import sys

import dateutil.parser
import dateutil.tz
import requests


def _usage():
    """Write a high level usage message to stderr."""
    fmt = 'usage: %s <username> <password> <app key> <from> <to>\n'
    msg = fmt % os.path.split(sys.argv[0])[1]
    sys.stderr.write(msg)


def _get_account_settings(username, password, app_key):
    auth = requests.auth.HTTPBasicAuth(username, password)

    headers = {
        'App-Key': app_key,
    }

    response = requests.get(
        'https://api.pingdom.com/api/2.0/settings',
        auth=auth,
        headers=headers)

    if response.status_code != httplib.OK:
        msg = 'Errir getting account settings (%s)\n' % response.status_code
        sys.stderr.write(msg)
        return None

    return response.json()


def _get_timezone_offset(username, password, app_key):
    account_settings = _get_account_settings(username, password, app_key)
    if not account_settings:
        return None

    settings = account_settings.get('settings', {})
    timezone = settings.get('timezone', {})
    return timezone.get('offset', None)


if __name__ == '__main__':

    if len(sys.argv) != 7:
        _usage()
        sys.exit(1)

    username = sys.argv[1]
    password = sys.argv[2]
    app_key = sys.argv[3]
    # 1994-11-05T08:15:30-05:00
    from_here = dateutil.parser.parse(sys.argv[4])
    to_here = dateutil.parser.parse(sys.argv[5])

    # datetime.datetime.fromtimestamp(1461763264)

    timezone_offset_in_minutes = _get_timezone_offset(username, password, app_key)
    timezone_offset_in_seconds = _get_timezone_offset(username, password, app_key)
    account_tz = dateutil.tz.tzoffset(None, timezone_offset_in_seconds)

    from_here = dateutil.parser.parse(sys.argv[4])
    from_here = from_here.astimezone(account_tz)

    to_here = dateutil.parser.parse(sys.argv[5])
    to_here = to_here.astimezone(account_tz)

    sys.exit(0)
