#!/usr/bin/env python

import datetime
import optparse
import re
import sys

import dateutil.parser
import numpy
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.pyplot as plt


class Response(object):

    bucket_size_in_seconds = 30

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

    @property
    def seconds_since_start(self):
        return (self.timestamp - type(self).first_timestamp).total_seconds()

    @property
    def seconds_since_start_bucket(self):
        seconds_since_start = int(round(self.seconds_since_start, 0))
        return seconds_since_start - (seconds_since_start % type(self).bucket_size_in_seconds)


class Main(object):

    def numerical_analysis(self):
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

    def generate_graphs(self, graphs):
        with PdfPages(graphs) as pdf:
            request_types = Response.request_types()
            request_types.sort()

            for request_type in request_types:
                responses = Response.responses_for_request_type(request_type)

                response_times_in_buckets = {}
                for response in responses:
                    seconds_since_start_bucket = response.seconds_since_start_bucket
                    if seconds_since_start_bucket not in response_times_in_buckets:
                        response_times_in_buckets[seconds_since_start_bucket] = []
                    response_times_in_buckets[seconds_since_start_bucket].append(response.response_time)

                xs = response_times_in_buckets.keys()
                xs.sort()

                tabloid_width = 17
                tabloid_height = 11
                plt.figure(figsize=(tabloid_width, tabloid_height))

                handles = []

                ys = [min(response_times_in_buckets.get(x, [0])) for x in xs]
                handle, = plt.plot(xs, ys, label='min')
                handles.append(handle)

                percentiles = [90, 95, 99]
                for percentile in percentiles:
                    ys = [numpy.percentile(response_times_in_buckets.get(x, [0]), percentile) for x in xs]
                    handle, = plt.plot(xs, ys, label='%dth percentile' % percentile)
                    handles.append(handle)

                ys = [max(response_times_in_buckets.get(x, [0])) for x in xs]
                handle, = plt.plot(xs, ys, label='max')
                handles.append(handle)

                plt.legend(
                    handles=handles,
                    loc='upper center',
                    bbox_to_anchor=(0.5, -0.05),
                    ncol=len(handles),
                    fancybox=True,
                    shadow=True,
                    fontsize='large')
                plt.grid(True)
                plt.xlabel(
                    'Seconds Since Test Start',
                    fontsize='large',
                    fontweight='bold')
                plt.ylabel(
                    'Response Time\n(milliseconds)',
                    fontsize='large',
                    fontweight='bold')
                plt.title(
                    '%s\n' % request_type,
                    fontsize='xx-large',
                    fontweight='bold')
                pdf.savefig()
                plt.close()


class CommandLineParser(optparse.OptionParser):

    def __init__(self):
        optparse.OptionParser.__init__(
            self,
            'usage: %prog [options] <concurrency>',
            description='This utility analyzes load test results')

        self.add_option(
            '--graphs',
            action='store',
            dest='graphs',
            default=None,
            type='string',
            help='pdf file name for graphs')

    def parse_args(self, *args, **kwargs):
        (clo, cla) = optparse.OptionParser.parse_args(self, *args, **kwargs)
        if 0 != len(cla):
            self.error('invalid command line args')
        return (clo, cla)


if __name__ == '__main__':
    clp = CommandLineParser()
    (clo, cla) = clp.parse_args()

    main = Main()
    main.numerical_analysis()
    if clo.graphs:
        main.generate_graphs(clo.graphs)
