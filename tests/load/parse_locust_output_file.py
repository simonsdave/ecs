#!/usr/bin/env python

import optparse
import re
import sys


class Main(object):

    def parse_data(self):
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
                timestamp = match.group('timestamp')
                locust_id = match.group('locust_id')
                request_type = match.group('request_type')
                success = int(match.group('success'))
                response_time = float(match.group('response_time'))

                print '%s\t%s\t%d\t%s\t%s' % (
                    timestamp,
                    request_type,
                    success,
                    locust_id,
                    response_time,
                )

        return 0


class CommandLineParser(optparse.OptionParser):

    def __init__(self):
        optparse.OptionParser.__init__(
            self,
            'usage: %prog [options]',
            description='This utility parses locust load test results')

    def parse_args(self, *args, **kwargs):
        (clo, cla) = optparse.OptionParser.parse_args(self, *args, **kwargs)
        if 0 != len(cla):
            self.error('invalid command line args')
        return (clo, cla)


if __name__ == '__main__':
    clp = CommandLineParser()
    (clo, cla) = clp.parse_args()

    main = Main()
    exit_code = main.parse_data()
    sys.exit(exit_code)
