""" Run
"""
import os
import threading
import datetime
import logging
log = logging.getLogger(__file__)

from ott.utils.cache_base import CacheBase
from .. import tests_to_urls


class StressTests(CacheBase):
    """ stress test OTP
    """

    def __init__(self):
        super(StressTests, self).__init__('otp')

        parser = tests_to_urls.get_args_parser()
        parser.add_argument('--threads',     '-t',  type=int, default=10, help="number of threads")
        parser.add_argument('--number',      '-n',  type=int, help="number of iterations")
        parser.add_argument('--duration',    '-d',  type=int, help="length of time (seconds) to run (as opposed to --number of iterations)")
        parser.add_argument('--file_prefix', '-fp', default="stress", help="stress file prefix, ala : stress-1.txt")
        args = parser.parse_args()

        self.args = args
        self.url_hash = tests_to_urls.run(args)
        self.url_list = tests_to_urls.url_hash_to_list(self.url_hash)
        if args.number:
            self.iterations_stress_test(args.number)
        elif args.duration:
            self.duration_stress_test(args.duration)

    def launch_stress_tests(self, iteration_id, thread_id):
        for i, u in enumerate(self.url_list):
            out_file = self.make_response_file_path(thread_id=thread_id, iteration_id=iteration_id, test_number=i)
            print out_file

    def launch_threads_of_stress_tests(self, iteration_id):
        for i in range(self.args.threads):
            t = threading.Thread(target=self.launch_stress_tests, args=(iteration_id, i+1,))
            t.start()

    def make_response_file_path(self, iteration_id, test_number, thread_id=1):
        '''return a path to a the response file
        '''
        now = datetime.datetime.now()
        file_name = "{}-{:%m%d%y_%H%M}_{}-{}-{}.txt".format(self.args.file_prefix, now, thread_id, iteration_id, test_number)
        file_path = os.path.join(self.tmp_dir, file_name)
        return file_path

    def duration_stress_test(self, duration=5):
        now = datetime.datetime.now()
        end = now + datetime.timedelta(seconds=duration)
        i = 0
        while now < end:
            now = datetime.datetime.now()
            i += 1

    def iterations_stress_test(self, num_iterations):
        for i in range(num_iterations):
            self.launch_threads_of_stress_tests(iteration_id=i)

    def printer(self):
        tests_to_urls.printer(self.args, self.this_module_dir, self.url_hash)

    @classmethod
    def run(cls, force_print=False):
        success = True
        st = StressTests()
        if force_print or st.args.printer or (not st.args.number and not st.args.duration):
            st.printer()
        return success


def main():
    StressTests.run()

if __name__ == '__main__':
    main()
