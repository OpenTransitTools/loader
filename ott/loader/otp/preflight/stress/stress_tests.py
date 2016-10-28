""" Run
"""
import sys
import time
import logging
log = logging.getLogger(__file__)

from ott.utils import otp_utils
from ott.utils import web_utils
from ott.utils.cache_base import CacheBase


class StressTests(CacheBase):
    """ stress test OTP
    """
    graphs = None

    def __init__(self):
        super(StressTests, self).__init__('otp')


    @classmethod
    def run(cls):
        return success


def main():
    StressTests.run()

if __name__ == '__main__':
    main()
