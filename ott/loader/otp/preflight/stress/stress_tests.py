""" Run
"""
import sys
import time
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
        args = parser.parse_args()
        tests_to_urls.printer(args, self.this_module_dir)

    @classmethod
    def run(cls):
        success = True
        st = StressTests()
        return success

    @classmethod
    def printer(cls):
        success = True
        st = StressTests()
        return success


def main():
    StressTests.run()

if __name__ == '__main__':
    main()
