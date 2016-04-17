#!/usr/bin/env python

import datetime
import optparse
import re
import sys

import dateutil.parser
import numpy


class Response(object):

    responses = {}

    @classmethod
    def response_times_for_request_type(cls, request_type):
        return [response.response_time for response in cls.responses[request_type]]

    @classmethod
    def successes_for_request_type(cls, request_type):
        return [response for response in cls.responses[request_type] if response.success]

    @classmethod
    def failures_for_request_type(cls, request_type):
        return [response for response in cls.responses[request_type] if not response.success]

    @classmethod
    def total_number_responses(cls):
        return sum([len(responses) for (response_type, responses) in cls.responses.iteritems()])

    def __init__(self, request_type, timestamp, success, response_time):
        object.__init__(self)

        self.timestamp = timestamp
        self.success = success
        self.response_time = response_time

        if request_type not in type(self).responses:
            type(self).responses[request_type] = []
        type(self).responses[request_type].append(self)


class Main(object):

    def analyze(self):

        reg_ex_pattern = (
            r'^\s*\[(?P<timestamp>.*)\].*:\s+(?P<request_type>.+)\t'
            r'(?P<locust_id>.+)\t+'
            r'(?P<success>\d)\t'
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
                success = int(match.group('success'))
                response_time = float(match.group('response_time'))

                Response(request_type, timestamp, success, response_time)

                first_timestamp = min(timestamp, first_timestamp)
                last_timestamp = max(timestamp, last_timestamp)

        overall_title = '%d from %s to %s' % (
            Response.total_number_responses(),
            first_timestamp,
            last_timestamp,
        )
        print '=' * len(overall_title)
        print overall_title
        print '=' * len(overall_title)
        print ''

        percentiles = [50, 60, 70, 80, 90, 95, 99]
        fmt = '%-25s %5d %5d %3.0f%%' + ' %9.0f' * (1 + len(percentiles) + 1)
        request_types = Response.responses.keys()
        request_types.sort()

        title_fmt = '%-25s %5s %5s %4s' + '%10s' * (1 + len(percentiles) + 1)
        args = [
            'Request Type',
            'Ok',
            'Error',
            '',
            'Min',
        ]
        args.extend(percentiles)
        args.append('Max')
        title = title_fmt % tuple(args)
        print title
        print '-' * len(title)

        for request_type in request_types:
            # responses = numpy.array(Response.response_times_for_request_type(request_type))
            responses = Response.response_times_for_request_type(request_type)
            args = [
                request_type,
                len(Response.successes_for_request_type(request_type)),
                len(Response.failures_for_request_type(request_type)),
                round(100.0 * (len(responses) * 1.0) / Response.total_number_responses()),
                min(responses),
            ]
            args.extend(numpy.percentile(numpy.array(responses), percentiles))
            args.append(max(responses))
            print fmt % tuple(args)

        print ''
        print '=' * len(overall_title)


class CommandLineParser(optparse.OptionParser):

    def __init__(self):
        optparse.OptionParser.__init__(
            self,
            'usage: %prog [options] <concurrency>',
            description='This utility analyzes load test results')

    def parse_args(self, *args, **kwargs):
        (clo, cla) = optparse.OptionParser.parse_args(self, *args, **kwargs)
        if 0 != len(cla):
            self.error('invalid command line args')
        return (clo, cla)


if __name__ == '__main__':
    clp = CommandLineParser()
    (clo, cla) = clp.parse_args()

    main = Main()
    main.analyze()
