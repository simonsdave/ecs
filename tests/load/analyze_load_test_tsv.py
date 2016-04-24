#!/usr/bin/env python

import datetime
import optparse
import re
import sys

import dateutil.parser
import numpy
import matplotlib.pyplot as plt


class Response(object):

    first_timestamp = datetime.datetime(2990, 1, 1)
    last_timestamp = datetime.datetime(1990, 1, 1)

    responses = []

    responses_by_request_type = {}

    responses_by_locust_id = {}

    @classmethod
    def request_types(cls):
        return cls.responses_by_request_type.keys()

    @classmethod
    def responses_for_request_type(cls, request_type):
        return cls.responses_by_request_type[request_type]

    @classmethod
    def response_times_for_request_type(cls, request_type):
        return [response.response_time for response in cls.responses_by_request_type[request_type]]

    @classmethod
    def successes_for_request_type(cls, request_type):
        return [response for response in cls.responses_by_request_type[request_type] if response.success]

    @classmethod
    def failures_for_request_type(cls, request_type):
        return [response for response in cls.responses_by_request_type[request_type] if not response.success]

    @classmethod
    def number_of_locusts(cls):
        return len(cls.responses_by_locust_id.keys())

    @classmethod
    def total_number_responses(cls):
        return len(cls.responses)

    def __init__(self, locust_id, request_type, timestamp, success, response_time):
        object.__init__(self)

        self.locust_id = locust_id
        self.request_type = request_type
        self.timestamp = timestamp
        self.success = success
        self.response_time = response_time

        type(self).responses.append(self)

        if self.request_type not in type(self).responses_by_request_type:
            type(self).responses_by_request_type[self.request_type] = []
        type(self).responses_by_request_type[self.request_type].append(self)

        if locust_id not in type(self).responses_by_locust_id:
            type(self).responses_by_locust_id[locust_id] = {}
        if self.request_type not in type(self).responses_by_locust_id[locust_id]:
            type(self).responses_by_locust_id[locust_id][self.request_type] = []
        type(self).responses_by_locust_id[locust_id][self.request_type].append(self)

        type(self).first_timestamp = min(self.timestamp, type(self).first_timestamp)
        type(self).last_timestamp = max(self.timestamp, type(self).last_timestamp)


class Main(object):

    def __init__(self, generate_graphs):
        object.__init__(self)

        self._generate_graphs = generate_graphs

    def analyze(self):

        reg_ex_pattern = (
            r'^\s*\[(?P<timestamp>.*)\].*:\s+'
            r'(?P<request_type>.+)\t'
            r'(?P<locust_id>.+)\t+'
            r'(?P<success>\d)\t'
            r'(?P<response_time>\d+\.\d+)\s*$'
        )
        reg_ex = re.compile(reg_ex_pattern)

        for line in sys.stdin:
            match = reg_ex.match(line)
            if match:
                timestamp = dateutil.parser.parse(match.group('timestamp'))
                locust_id = match.group('locust_id')
                request_type = match.group('request_type')
                success = int(match.group('success'))
                response_time = float(match.group('response_time'))

                Response(locust_id, request_type, timestamp, success, response_time)

        overall_title = '%d @ %d from %s to %s' % (
            Response.total_number_responses(),
            Response.number_of_locusts(),
            Response.first_timestamp,
            Response.last_timestamp,
        )
        print '=' * len(overall_title)
        print overall_title
        print '=' * len(overall_title)
        print ''

        """
        for (locust_id, responses_by_request_type) in Response.responses_by_locust_id.iteritems():
            print '%s' % locust_id
            for (request_type, responses) in responses_by_request_type.iteritems():
                print '-- %s %d' % (request_type, len(responses))
            print ''
        """

        percentiles = [50, 60, 70, 80, 90, 95, 99]
        fmt = '%-25s %5d %5d %3.0f%%' + ' %9.0f' * (1 + len(percentiles) + 1)
        request_types = Response.request_types()
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

        if self._generate_graphs:
            request_type = 'Tasks-Happy-Path'
            responses = Response.responses_for_request_type(request_type)
            y = [response.response_time for response in responses]
            x = [(response.timestamp - Response.first_timestamp).total_seconds() for response in responses]
            plt.plot(x, y)
            plt.xlabel('Seconds')
            plt.ylabel('Response Time\n(milliseconds)')
            plt.title(request_type)
            plt.savefig('/vagrant/foo.png')


class CommandLineParser(optparse.OptionParser):

    def __init__(self):
        optparse.OptionParser.__init__(
            self,
            'usage: %prog [options] <concurrency>',
            description='This utility analyzes load test results')

        self.add_option(
            '-g',
            '--generate-graphs',
            action='store_true',
            default=False,
            dest='generate_graphs')

    def parse_args(self, *args, **kwargs):
        (clo, cla) = optparse.OptionParser.parse_args(self, *args, **kwargs)
        if 0 != len(cla):
            self.error('invalid command line args')
        return (clo, cla)


if __name__ == '__main__':
    clp = CommandLineParser()
    (clo, cla) = clp.parse_args()

    main = Main(clo.generate_graphs)
    main.analyze()
