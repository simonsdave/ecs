#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""This script explores how to calculate ECS availability.

Useful references:

    * https://www.pingdom.com/resources/api
    * https://www.pingdom.com/features/api/documentation/

Example usage

    sla.py \
        $PINGDOM_EMAIL \
        $PINGDOM_PASSWORD \
        $PINGDOM_APPKEY \
        "2016-04-30T09:00:00-05:00" \
        "2016-04-30T10:00:00-05:00" \
        "Cloudfeaster Website"
"""

import datetime
import httplib
import os
import sys

import dateutil.parser
import dateutil.tz
import requests


def _usage():
    """Write a high level usage message to stderr."""
    fmt = 'usage: %s <email> <password> <app key> <from> <to> <checkname>\n'
    msg = fmt % os.path.split(sys.argv[0])[1]
    sys.stderr.write(msg)


def _get_account_settings(email, password, app_key):
    auth = requests.auth.HTTPBasicAuth(email, password)

    headers = {
        'App-Key': app_key,
    }

    response = requests.get(
        'https://api.pingdom.com/api/2.0/settings',
        auth=auth,
        headers=headers)

    if response.status_code != httplib.OK:
        msg = 'Error getting account settings (%s)\n' % response.status_code
        sys.stderr.write(msg)
        return None

    return response.json()


def _get_account_timezone_offset_in_seconds(email, password, app_key):
    account_settings = _get_account_settings(email, password, app_key)
    if not account_settings:
        return None

    settings = account_settings.get('settings', {})
    timezone = settings.get('timezone', {})
    offset_in_minutes = timezone.get('offset', None)
    return offset_in_minutes * 60 if offset_in_minutes is not None else None


def _get_check_ids(email, password):
    auth = requests.auth.HTTPBasicAuth(email, password)

    headers = {
        'App-Key': app_key,
    }

    response = requests.get(
        'https://api.pingdom.com/api/2.0/checks',
        auth=auth,
        headers=headers)

    if response.status_code != httplib.OK:
        msg = 'Error getting check names (%s)\n' % response.status_code
        sys.stderr.write(msg)
        return None

    return {check['name']: check['id'] for check in response.json().get('checks', [])}


class Result(object):

    def __init__(self, timestamp_in_account_tz, is_ok, response_time_in_ms):
        object.__init__(self)

        self.timestamp_in_account_tz = timestamp_in_account_tz
        self.is_ok = is_ok
        self.response_time_in_ms = response_time_in_ms

    def __str__(self):
        return '%s / %s / %d' % (self.timestamp_in_account_tz, self.is_ok, self.response_time_in_ms)


def _get_check_results(email, password, check_id, from_here, to_here):
    # https://www.pingdom.com/resources/api#MethodGet+Raw+Check+Results
    # max 1000 results returned
    # 1 minute check resolution = 1440 results / day
    # 5 minute check resolution = 288 results / day
    auth = requests.auth.HTTPBasicAuth(email, password)

    headers = {
        'App-Key': app_key,
    }

    url = 'https://api.pingdom.com/api/2.0/results/%s?from=%s&to=%s' % (
        check_id,
        from_here,
        to_here,
    )

    response = requests.get(
        url,
        auth=auth,
        headers=headers)

    if response.status_code != httplib.OK:
        msg = 'Error getting check results (%s)\n' % response.status_code
        sys.stderr.write(msg)
        return None

    def _create_result(result):
        return Result(
            result.get('time', 0),
            result.get('status', '') == 'up',
            result.get('responsetime', 0))

    return [_create_result(result) for result in response.json().get('results', [])]


if __name__ == '__main__':

    if len(sys.argv) != 7:
        _usage()
        sys.exit(1)

    email = sys.argv[1]
    password = sys.argv[2]
    app_key = sys.argv[3]
    # 1994-11-05T08:15:30-05:00
    from_here = dateutil.parser.parse(sys.argv[4])
    to_here = dateutil.parser.parse(sys.argv[5])
    check_name = sys.argv[6]

    account_timezone_offset_in_seconds = _get_account_timezone_offset_in_seconds(
        email,
        password,
        app_key)
    if account_timezone_offset_in_seconds is None:
        sys.exit(2)
    account_tz = dateutil.tz.tzoffset(None, account_timezone_offset_in_seconds)

    # https://en.wikipedia.org/wiki/Unix_time
    epoch = datetime.datetime(1970, 1, 1, 0, 0, 0)
    epoch_utc_tz = epoch.replace(tzinfo=dateutil.tz.tzutc())
    epoch_account_tz = epoch_utc_tz.astimezone(account_tz)

    from_here = dateutil.parser.parse(sys.argv[4])
    from_here_account_tz = from_here.astimezone(account_tz)
    from_here_as_timestamp_account_tz = ((from_here_account_tz - epoch_account_tz).total_seconds())

    to_here = dateutil.parser.parse(sys.argv[5])
    to_here_account_tz = to_here.astimezone(account_tz)
    to_here_as_timestamp_account_tz = int((to_here_account_tz - epoch_account_tz).total_seconds())

    check_name_to_id = _get_check_ids(email, password)
    check_id = check_name_to_id.get(check_name, None)
    if check_id is None:
        msg = 'Error getting check ID for \'%s\'\n' % check_name
        sys.stderr.write(msg)
        sys.exit(2)

    results = _get_check_results(
        email,
        password,
        check_id,
        from_here_as_timestamp_account_tz,
        to_here_as_timestamp_account_tz)

    for result in results:
        when_account_tz = datetime.datetime.fromtimestamp(result.timestamp_in_account_tz)
        when_account_tz = when_account_tz.replace(tzinfo=account_tz)
        when_from_here_tz = when_account_tz.astimezone(from_here.tzinfo)
        print '%s %s %d' % (
            when_from_here_tz,
            1 if result.is_ok else 0,
            result.response_time_in_ms,
        )

    sys.exit(0)
