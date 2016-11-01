""" Run
"""
import sys
import time
import datetime
import logging
log = logging.getLogger(__file__)

from ott.utils.cache_base import CacheBase
from .. import tests_to_urls


class StressTests(CacheBase):
    """ stress test OTP
    """
    graphs = None

    def __init__(self):
        super(StressTests, self).__init__('otp')

        parser = tests_to_urls.get_args_parser()
        parser.add_argument('--threads',  '-t', default=10, help="number of threads")
        parser.add_argument('--number',   '-n', type=int, help="number of iterations")
        parser.add_argument('--duration', '-d', type=int, help="length of time (seconds) to run (as opposed to --number of iterations)")
        args = parser.parse_args()

        self.args = args
        self.url_hash = tests_to_urls.run(args)
        if args.number:
            self.iterations_stress_test(args.number)
        elif args.duration:
            self.duration_stress_test(args.duration)

    def duration_stress_test(self, duration=5):
        now = datetime.datetime.now()
        end = now + datetime.timedelta(seconds=duration)
        i = 0
        while now < end:
            now = datetime.datetime.now()
            i += 1
            print i

    def iterations_stress_test(self, num_iterations):
        for i in range(num_iterations):
            print i

    def printer(self, force=False):
        if force or self.args.printer or (not self.args.number and not self.args.duration):
            tests_to_urls.printer(self.args, self.this_module_dir, self.url_hash)

    @classmethod
    def run(cls):
        success = True
        st = StressTests()
        st.printer()
        return success


def main():
    StressTests.run()

if __name__ == '__main__':
    main()
