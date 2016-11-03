""" Run
"""
import os
import threading
import datetime
from time import sleep
import logging
log = logging.getLogger(__file__)

from ott.utils.cache_base import CacheBase
from ott.utils import web_utils
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
        parser.add_argument('--search',      '-s',  default="", help="find this string in all stress test reponses")
        parser.add_argument('--file_prefix', '-fp', default="stress", help="stress file prefix, ala : stress-1.txt")
        args = parser.parse_args()

        self.args = args
        self.url_hash = tests_to_urls.run(args)
        self.url_list = tests_to_urls.url_hash_to_list(self.url_hash)

        if args.number or args.duration:
            self.run_stress_tests()

    def run_stress_tests(self):
        ''' run stress tests by calling the servers
        '''
        #import pdb; pdb.set_trace()

        self.threads = []
        self.num_tests = 0
        self.num_failures = 0

        # step 1: get start time
        self.start_time = datetime.datetime.now()

        # step 2: launch some threads to execute our tests
        for i in range(self.args.threads):
            if self.args.number:
                t = threading.Thread(target=self.iterations_stress_test, args=(self.args.number, i+1,))
            elif self.args.duration:
                t = threading.Thread(target=self.duration_stress_test,   args=(self.args.number, i+1,))

            self.threads.append(t)
            t.start()

        # step 3: wait for threads to finish
        for t in self.threads:
            t.join()

        # step 4: print out some stats
        self.end_time = datetime.datetime.now()
        if self.num_tests > 0:
            succeses = self.num_tests - self.num_failures
            if succeses > 0:
                t = self.end_time - self.start_time
                tps = float(succeses) / float(t.seconds)
                print "TESTS: {}\nFAILURES : {}\nSECONDS: {}\nSUCCESSFUL TESTS PER SECOND: {}\n".format(self.num_tests, self.num_failures, t.seconds, tps)
            else:
                print "TESTS: {}\nFAILURES : {}\nSECONDS: {}:".format(self.num_tests, self.num_failures, t.seconds)

    def duration_stress_test(self, duration=5, thread_id=1):
        ''' duration stress will run for a given amount of time
        '''
        now = datetime.datetime.now()
        end = now + datetime.timedelta(seconds=duration)
        i = 0
        while now < end:
            now = datetime.datetime.now()
            self.launch_stress_tests(iteration_id=i+1, thread_id=thread_id)
            i += 1

    def iterations_stress_test(self, num_iterations, thread_id=1):
        ''' iteration stress will run a specified amount of time
        '''
        for i in range(num_iterations):
            self.launch_stress_tests(iteration_id=i+1, thread_id=thread_id)

    def launch_stress_tests(self, iteration_id, thread_id):
        ''' run thru the test suite urls and call the service, blah...
        '''
        for i, u in enumerate(self.url_list):
            response = web_utils.get_response(u, show_info=True)
            #sleep(0.05)
            self.num_tests += 1
            if response is None or len(response) < 1:
                response = "RESPONSE WAS NONE!!!"
            if "requestParameters" not in response or "plan" not in response or "itineraries" not in response:
                self.num_failures += 1
                out_file = self.make_response_file_path(thread_id=thread_id, iteration_id=iteration_id, test_number=i)
                web_utils.write_url_response_file(out_file, u, response)

    def make_response_file_path(self, iteration_id, test_number, thread_id=1):
        '''return a path to a the response file
        '''
        now = datetime.datetime.now()
        file_name = "{}-{:%m%d%y_%H%M}_{}-{}-{}.txt".format(self.args.file_prefix, now, thread_id, iteration_id, test_number)
        file_path = os.path.join(self.tmp_dir, file_name)
        return file_path

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
