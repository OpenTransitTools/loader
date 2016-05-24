import os
import inspect
import sys
import time
import datetime
import logging
log = logging.getLogger(__file__)

import csv
import re
import socket
import urllib2
from mako.template import Template
from mako import exceptions

from ott.utils import file_utils
from ott.utils.config_util import ConfigUtil


class TestResult:
    FAIL=000
    WARN=333
    PASS=111


class Test(object):
    """ Params for test, along with run capability -- Test object is typically built from a row in an .csv test suite 
    """
    TestClass = None

    def __init__(self, param_dict, line_number, date=None):
        """ {
            OTP parmas:
              'From'
              'To'
              'Max dist'
              'Mode'
              'Optimize'
              'Service' - expects 'Saturday' or 'Sunday' or leave empty
              'Time'

            Test params:
              'Arrive by' - expects 'FALSE' if arrive by test should not be ran or leave empty
              'Depart by' - expects 'FALSE' if depart by test should not be ran or leave empty
              'Expected output'
              'Expected trip duration'
              'Expected trip distance'
              'Expected number of legs'

            Misc text:
              'Description/notes'
            }
        """
        #import pdb; pdb.set_trace()
        self.config = ConfigUtil(section='otp')
        self.port = self.config.get('port', def_val="80")
        self.host = self.config.get('host', def_val="http://maps7.trimet.org")

        self.csv_line_number = line_number
        self.csv_params      = param_dict
        self.date            = date

        self.itinerary       = None
        self.otp_params      = ''
        self.map_params      = ''
        self.is_valid        = True
        self.error_descript  = None
        self.result          = TestResult.FAIL

        self.coord_from      = self.get_param('From')
        self.coord_to        = self.get_param('To')
        self.distance        = self.get_param('Max dist')
        self.mode            = self.get_param('Mode')
        self.optimize        = self.get_param('Optimize')
        self.service         = self.get_param('Service')
        self.time            = self.get_param('Time')
        if self.time is not None and self.time.find(' ') > 0:
            self.time = self.time.replace(' ', '')

        self.description     = self.get_param('Description/notes')
        self.expect_output   = self.get_param('Expected output')
        self.expect_duration = self.get_param('Expected trip duration')
        self.expect_distance = self.get_param('Expected trip distance')
        self.expect_num_legs = self.get_param('Expected number of legs')
        self.arrive_by       = self.get_param('Arrive by')
        self.depart_by       = self.get_param('Depart by')

        if 'Expected number of legs' in param_dict:
            self.expect_num_legs = self.get_param('Expected number of legs')

        self.set_urls()
        self.init_url_params()
        self.date = self.get_date_param(self.date)

    def set_urls(self):
        p,m = self.make_urls(self.host, self.port)
        self.planner_url = p
        self.map_url = m

    @classmethod
    def make_urls(cls, host, port, path=""):
        http = ""
        if "http" not in host:
            http = "http://"
        planner_url = file_utils.envvar('OTP_URL', "{}{}:{}/{}".format(http, host, port, path))
        map_url = file_utils.envvar('OTP_MAP_URL', "{}{}/otp.html".format(http, host))
        return planner_url, map_url

    def get_param(self, name, def_val=None):
        ret_val = def_val
        try:
            p = self.csv_params[name]
            if p is not None and len(p) > 0:
                ret_val = p.strip()
        except:
            log.warn("WARNING: '{0}' was not found as an index in record {1}".format(name, self.csv_params))

        return ret_val

    def did_test_pass(self):
        ret_val = False
        if self.result is not None and self.result is TestResult.PASS:
            ret_val = True
        return ret_val

    def append_note(self, note=""):
        self.description += " " + note

    def call_otp(self, url=None):
        ''' calls the trip web service
        '''
        self.itinerary = None
        start = time.time()
        url = (url if url != None else self.get_planner_url())
        self.itinerary = self.static_call_otp(url)
        end = time.time()
        self.response_time = end - start
        log.info("call_otp: response time of {} second for url {}".format(self.response_time, url))
        log.debug(self.itinerary)
        if self.response_time <= 30:
            self.result = TestResult.PASS
        else:
            self.result = TestResult.WARN
            log.info("call_otp: :::NOTE::: response time took *longer than 30 seconds* for url {}".format(url))

    @classmethod
    def static_call_otp(cls, url, accept='application/xml'):
        ret_val = None
        try:
            socket.setdefaulttimeout(2000)
            log.debug("call_otp: OTP output for " + url)
            req = urllib2.Request(url, None, {'Accept':accept})
            res = urllib2.urlopen(req)
            log.debug("call_otp: OTP output for " + url)
            ret_val = res.read()
            res.close()
        except:
            log.warn('ERROR: could not get data from url (timeout?): {0}'.format(url))
        return ret_val

    def test_otp_result(self, strict=True):
        """ regexp test of the itinerary output for certain strings
        """
        if self.itinerary == None:
            self.result = TestResult.FAIL if strict else TestResult.WARN
            self.error_descript = "test_otp_result: itinerary is null"
            log.info(self.error_descript)
        else:
            if len(self.itinerary) < 1000:
                self.result = TestResult.FAIL if strict else TestResult.WARN
                self.error_descript = "test_otp_result: itinerary content looks small at " + str(len(self.itinerary)) + " characters."
                log.warn(self.error_descript)
            else:
                self.error_descript = "test_otp_result: itinerary content size is " + str(len(self.itinerary)) + " characters."
                log.info(self.error_descript)
                warn = False
                warn = self.test_expected_response(self.expect_output, warn, strict)
                if self.expect_duration is not None and len(self.expect_duration) > 0:
                    durations = re.findall('<itinerary>.*?<duration>(.*?)</duration>.*?</itinerary>', self.itinerary) 
                    error = 0.2
                    high = float(self.expect_duration) * (1 + error)
                    low = float(self.expect_duration) * (1 - error)
                    for duration in durations:
                        if int(duration) > high or int(duration) < low:
                            self.result = TestResult.FAIL if strict else TestResult.WARN
                            self.error_descript += "test_otp_result: an itinerary duration was different than expected by more than {0}%.".format(error * 100)
                            warn = True
                            break
                if self.expect_num_legs is not None and len(self.expect_num_legs) > 0:
                    try:
                        values = [int(i) for i in self.expect_num_legs.split('|')]
                        if len(values) != 2:
                            raise ValueError
                        min_legs = values[0]
                        max_legs = values[1]
                        all_legs = re.findall('<itinerary>.*?<legs>(.*?)</legs>.*?</itinerary>', self.itinerary)
                        for legs in all_legs:
                            num_legs = len(re.findall('<leg .*?>', legs))
                            if num_legs > max_legs or num_legs < min_legs:
                                self.result = TestResult.FAIL if strict else TestResult.WARN
                                self.error_descript += "test_otp_result: an itinerary returned was not between {0} and {1} legs.".format(min_legs, max_legs)
                                warn = True
                                break
                    except ValueError:
                        self.error_descript += "expected number of legs test not in 'min|max' format."
                        warn = True
                if warn:
                    log.warn(self.error_descript)

        return self.result

    def test_expected_response(self, expected_output, ret_val, strict):
        if expected_output is not None and len(expected_output) > 0:
            regres = re.search(expected_output, self.itinerary)
            if regres is None:
                self.result = TestResult.FAIL if strict else TestResult.WARN
                self.error_descript += "test_otp_result: couldn't find " + expected_output + " in otp response."
                ret_val = True
        return ret_val

    def get_planner_url(self):
        return "{0}&{1}".format(self.make_url(self.planner_url), self.otp_params)

    def get_map_url(self):
        purl = self.planner_url.split('/')[-1]
        return "{0}&purl=/{1}&{2}".format(self.make_url(self.map_url), purl, self.map_params)

    @classmethod
    def make_url(cls, url, separater="?submit"):
        ret_val = url
        if "?" not in url:
            ret_val = url + separater
        return ret_val

    def get_ridetrimetorg_url(self):
        return "http://ride.trimet.org?submit&" + self.map_params

    def init_url_params(self):
        """
        """
        self.otp_params = 'fromPlace={0}&toPlace={1}'.format(self.coord_from, self.coord_to)
        self.map_params = self.otp_params
        if self.coord_from == None or self.coord_from == '' or self.coord_to == None or self.coord_to == '':
            if self.coord_from != None or self.coord_to != None:
                self.error_descript = "no from and/or to coordinate for the otp url (skipping test) - from:{} to:{}".format(self.coord_from, self.coord_to)
                log.warn(self.error_descript)
            self.is_valid = False

    def url_param(self, name, param, default=None):
        """
        """
        p = (param if param != None else default)
        if p != None and p != '':
            self.otp_params += '&{0}={1}'.format(name, p)
            self.map_params += '&{0}={1}'.format(name, p)

    def url_distance(self, dist=None):
        self.url_param('maxWalkDistance', dist, self.distance)

    def url_mode(self, mode=None):
        self.url_param('mode', mode, self.mode)

    def url_optimize(self, opt=None):
        self.url_param('optimize', opt, self.optimize)

    def url_arrive_by(self, opt="true"):
        self.url_param('arriveBy', opt, self.optimize)

    def url_time(self, time=None):
        self.url_param('time', time, self.time)

    def url_time_7am(self):
        self.url_param('time', '7:00am')

    def url_time_12pm(self):
        self.url_param('time', '12:00pm')

    def url_time_5pm(self):
        self.url_param('time', '5:00pm')

    def url_service(self, svc=None):
        """
        """
        pass

    def get_date_param(self, date, fmt="%Y-%m-%d"):
        """ provide a default date (set to today) if no service provided...
        """
        if self.otp_params.find('date') < 0:
            if date is None:
                if self.service is None:
                    date = datetime.datetime.now().strftime(fmt)
                elif self.service == 'Saturday':
                    date = self.url_service_next_saturday()
                elif self.service == 'Sunday':
                    date = self.url_service_next_sunday()
                else:
                    date = datetime.datetime.now().strftime(fmt)
                    log.warn("service param '{0}' not valid, using todays date.".format(self.service))
            
            self.url_param('date', date)
        return date

    def url_service_next_weekday(self):
        """
        """
        pass

    def url_service_next_saturday(self):
        date = datetime.datetime.now()
        day = date.weekday()
        if day == 6:
            date = date+datetime.timedelta(days=6)
        else:
            date = date+datetime.timedelta(days=5-day)
        date = date.strftime("%Y-%m-%d")
        return date

    def url_service_next_sunday(self):
        date = datetime.datetime.now()
        day = date.weekday()
        date = date+datetime.timedelta(days=6-day)
        date = date.strftime("%Y-%m-%d")
        return date

    def url_service_next_month_weekday(self):
        """
        """
        pass

    def depart_by_check(self):
        if self.depart_by == 'FALSE':
            self.is_valid = False

    def arrive_by_check(self):
        if self.arrive_by == 'FALSE':
            self.is_valid = False


Test.TestClass = Test

class TestSuite(object):
    """ url
    """

    def __init__(self, dir, file, date=None):
        """
        """
        self.file_path = os.path.join(dir, file)
        self.name = file
        self.date = date
        self.params = []
        self.tests  = []
        self.failures = 0
        self.passes   = 0
        self.read()

    def read(self):
        """ read a .csv file, and save each row as a set of test params
        """
        file = open(self.file_path, 'r')
        reader = csv.DictReader(file)
        fn = reader.fieldnames
        for row in reader:
            self.params.append(row)

    @classmethod
    def prep_url(cls, t):
        t.url_distance()
        t.url_mode()
        t.url_optimize()
        t.url_time()

    def do_test(self, t, strict=True):
        self.prep_url(t)
        if t.is_valid:
            t.call_otp()
            time.sleep(1)
            t.test_otp_result(strict)
            self.tests.append(t);
            if t.result is TestResult.PASS:
                self.passes += 1
            elif t.result is TestResult.FAIL:
                log.info("test_suite: this test failed " + t.get_planner_url() + "\n")
                self.failures += 1
            sys.stdout.write(".")

    def run(self):
        """ iterate the list of tests from the .csv files, run the test (call otp), and check the output.
        """
        log.info("test_suite {0}: ******* date - {1} *******\n".format(self.name, datetime.datetime.now()))
        for i, p in enumerate(self.params):
            t = Test.TestClass(p, i+2, self.date)  # i+2 is the line number in the .csv file, accounting for the header
            t.depart_by_check()
            self.do_test(t)

            """ arrive by tests
            """
            t = Test.TestClass(p, i+2, self.date)
            t.url_arrive_by()
            t.append_note(" ***NOTE***: arrive by test ")
            t.arrive_by_check()
            self.do_test(t, False)

    def printer(self):
        """ iterate the list of tests from the .csv files and print the URLs
        """
        for i, p in enumerate(self.params):
            t = Test(p, i+2, self.date)  # i+2 is the line number in the .csv file, accounting for the header
            t.depart_by_check()
            self.prep_url(t)
            url = t.get_planner_url()
            if t.is_valid:
                print url

            """ arrive by tests
            """
            t = Test(p, i+2, self.date)
            t.url_arrive_by()
            t.append_note(" ***NOTE***: arrive by test ")
            t.arrive_by_check()
            url = t.get_planner_url()
            if t.is_valid:
                print url


class TestRunner(object):
    """ Run .csv tests from ./tests/ by constructing a
        url to the trip planner, calling the url, then printing a report
    """
    this_module_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

    def __init__(self, report_template=None, date=None):
        """constructor builds the test runner
        """
        self.test_suites = self.get_test_suites(date)
        if report_template is None:
            report_template = os.path.join(self.this_module_dir, 'templates', 'good_bad.html')
        self.report_template = Template(filename=report_template)

    def run(self):
        """ execute tests
        """
        for ts in self.test_suites:
            ts.run()

    def printer(self):
        """ print test urls...
        """
        for ts in self.test_suites:
            ts.printer()

    def report(self, dir=None, report_name='otp_report.html'):
        """ render a pass/fail report
        """
        ret_val = None
        try:
            # step 1: mako render of the report
            host = "FIX ME"
            r = self.report_template.render(host, test_suites=self.test_suites, test_errors=self.has_errors())
            ret_val = r

            # step 2: stream the report to a file
            report_path = report_name
            if dir:
                report_path = os.path.join(dir, report_name)
            f = open(report_path, 'w')
            if r:
                f.write(r)
            else:
                f.write("Sorry, the template was null...")
            f.flush()
            f.close()
        except Exception, e:
            print exceptions.text_error_template().render()
        return ret_val

    def has_errors(self):
        ret_val = False
        for t in self.test_suites:
            if t.failures > 0 or t.passes <= 0:
                ret_val = True
                log.info("test_suite {0} has {1} error(s) and {2} passes".format(t, t.failures, t.passes))
        return ret_val

    @classmethod
    def get_suites_dir(cls, suites_name="suites"):
        this_module_dir = cls.this_module_dir
        suites_path = os.path.join(this_module_dir, suites_name)
        return suites_path

    @classmethod
    def get_test_suites(cls, date=None):
        test_suites = []
        dir = cls.get_suites_dir()
        files=os.listdir(dir)
        for f in files:
            if f.lower().endswith('.csv'):
                t = TestSuite(dir, f, date)
                test_suites.append(t)
        return test_suites

    @classmethod
    def test_graph(cls, graph_dir, delay=1):
        ''' run graph tests against whatever server is running
        '''
        ret_val = False
        log.info('GRAPH TESTS: Starting tests!')
        time.sleep(delay)
        t = TestRunner()
        t.run()
        t.report(graph_dir)
        if t.has_errors():
            log.info('GRAPH TESTS: There were errors!')
            ret_val = False
        else:
            log.info('GRAPH TESTS: Nope, no errors')
            ret_val = True
        return ret_val


def stress(argv):
    date = None
    if len(argv) > 2:
        date = argv[1]

    test_suites = TestRunner.get_test_suites(date)
    for ts in test_suites:
        ts.printer()

def main(argv=sys.argv):
    #import pdb; pdb.set_trace()
    if 'DEBUG' in argv:
        log.basicConfig(level=log.DEBUG)

    if 'STRESS' in argv:
        stress(argv)
    else:
        TestRunner.test_graph()

if __name__ == '__main__':
    main()
