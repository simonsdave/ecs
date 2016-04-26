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
    def _bucket_size_in_seconds(self):
        total_number_seconds_in_test = (type(self).last_timestamp - type(self).first_timestamp).total_seconds()
        total_number_of_buckets_so_things_look_ok = 100
        return total_number_seconds_in_test / total_number_of_buckets_so_things_look_ok

    @property
    def seconds_since_start_bucket(self):
        seconds_since_start = int(round(self.seconds_since_start, 0))
        return seconds_since_start - (seconds_since_start % self._bucket_size_in_seconds)


class Main(object):

    def load_data(self):
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

    def numerical_analysis(self):
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

        percentiles = [50, 60, 70, 80, 90, 95, 99]
        fmt = '%-25s %5d %5d %9.4f' + '%9.0f' * (2 + len(percentiles) + 1)
        request_types = Response.request_types()
        request_types.sort()

        title_fmt = '%-25s %5s %5s ' + '%9s' * (3 + len(percentiles) + 1)
        args = [
            'Request Type',
            'Ok',
            'Error',
            'm',
            'b',
            'Min',
        ]
        args.extend(percentiles)
        args.append('Max')
        title = title_fmt % tuple(args)
        print title
        print '-' * len(title)

        for request_type in request_types:
            responses = Response.responses_for_request_type(request_type)
            seconds_since_start = [response.seconds_since_start for response in responses]
            response_times = [response.response_time for response in responses]
            m, b = numpy.polyfit(seconds_since_start, response_times, 1)
            args = [
                request_type,
                len(Response.successes_for_request_type(request_type)),
                len(Response.failures_for_request_type(request_type)),
                m,
                b,
                min(response_times),
            ]
            args.extend(numpy.percentile(numpy.array(response_times), percentiles))
            args.append(max(response_times))
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

                column_labels = ['m', 'b']
                row_labels = []
                cells = []

                m_fmt = '%.4f'
                b_fmt = '%.0f'

                ys = [min(response_times_in_buckets.get(x, [0])) for x in xs]
                m, b = numpy.polyfit(xs, ys, 1)
                cells.append([m_fmt % m, b_fmt % b])
                row_labels.append('min')
                handle, = plt.plot(xs, ys, label='min')
                handles.append(handle)

                percentiles = [90, 99]
                for percentile in percentiles:
                    ys = [numpy.percentile(response_times_in_buckets.get(x, [0]), percentile) for x in xs]
                    m, b = numpy.polyfit(xs, ys, 1)
                    cells.append([m_fmt % m, b_fmt % b])
                    row_labels.append(str(percentile))
                    handle, = plt.plot(xs, ys, label='%dth percentile' % percentile)
                    handles.append(handle)

                ys = [max(response_times_in_buckets.get(x, [0])) for x in xs]
                m, b = numpy.polyfit(xs, ys, 1)
                cells.append([m_fmt % m, b_fmt % b])
                row_labels.append('max')
                handle, = plt.plot(xs, ys, label='max')
                handles.append(handle)

                plt.table(
                    colWidths=[0.1] * 3,
                    cellText=cells,
                    rowLabels=row_labels,
                    rowLoc='right',
                    colLabels=column_labels,
                    loc='center right')
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

                hours, remainder = divmod((Response.last_timestamp - Response.first_timestamp).total_seconds(), 3600)
                minutes, _ = divmod(remainder, 60)
                title = '%s\n(%.0f%% of %d requests @ %d concurrency for %d hours %d minutes)\n' % (
                    request_type.replace('-', ' '),
                    (len(responses) * 100.0) / Response.total_number_responses(),
                    Response.total_number_responses(),
                    Response.number_of_locusts(),
                    hours,
                    minutes)
                plt.title(
                    title,
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
    main.load_data()
    main.numerical_analysis()
    if clo.graphs:
        main.generate_graphs(clo.graphs)
