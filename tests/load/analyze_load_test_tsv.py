#!/usr/bin/env python

import datetime
import re
import sys

import dateutil.parser
import numpy


class Response(object):

    responses = {}

    @classmethod
    def response_times_by_request_type(cls, request_type):
        return [response.response_time for response in cls.responses[request_type]]

    @classmethod
    def total_number_responses(cls):
        return sum([len(responses) for (response_type, responses) in cls.responses.iteritems()])

    def __init__(self, request_type, timestamp, status_code, response_time):
        object.__init__(self)

        self.timestamp = timestamp
        self.status_code = status_code
        self.response_time = response_time

        if request_type not in type(self).responses:
            type(self).responses[request_type] = []
        type(self).responses[request_type].append(self)


if __name__ == '__main__':
    reg_ex_pattern = (
        r'^\s*\[(?P<timestamp>.*)\].*:\s+(?P<request_type>.+)\t'
        r'(?P<locust_id>.+)\t+'
        r'(?P<status_code>\d+)\t'
        r'(?P<response_time>\d+\.\d+)\s*$'
    )
    reg_ex = re.compile(reg_ex_pattern)

    first_timestamp = datetime.datetime(2990, 1, 1)
    last_timestamp = datetime.datetime(1990, 1, 1)
    data = {}

    for line in sys.stdin:
        match = reg_ex.match(line)
        if match:
            timestamp = dateutil.parser.parse(match.group('timestamp'))
            request_type = match.group('request_type')
            status_code = match.group('status_code')
            response_time = float(match.group('response_time'))

            Response(request_type, timestamp, status_code, response_time)

            first_timestamp = min(timestamp, first_timestamp)
            last_timestamp = max(timestamp, last_timestamp)

    print '%d from %s to %s' % (
        Response.total_number_responses(),
        first_timestamp,
        last_timestamp,
    )
    percentiles = [50, 70, 90, 95, 99]
    for request_type in Response.responses.keys():
        print request_type
        responses = numpy.array(Response.response_times_by_request_type(request_type))
        print '-- %d (%.0f%%) %s' % (
            len(responses),
            round(100.0 * (len(responses) * 1.0) / Response.total_number_responses()),
            numpy.percentile(responses, percentiles),
        )
