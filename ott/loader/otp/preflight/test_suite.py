from ott.utils.config_util import ConfigUtil
from ott.utils.cache_base import CacheBase

from ott.utils import otp_utils
from ott.utils import date_utils
from ott.utils import object_utils

import os
import sys
import csv
import re

import time
import datetime
import logging
log = logging.getLogger(__file__)


MIN_SIZE_ITIN=1000

class TestResult:
    FAIL=000
    WARN=333
    PASS=111


class Test(object):
    """ Params for test, along with run capability -- Test object is typically built from a row in an .csv test suite 
    """

    def __init__(self, param_dict, line_number, ws_url, map_url, date=None):
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
        self.config = ConfigUtil(section='otp')

        self.is_valid        = True
        self.error_descript  = None

        self.result          = TestResult.FAIL
        self.response_time   = -1.0

        self.ws_url          = ws_url
        self.map_url         = map_url

        self.csv_line_number = line_number
        self.csv_params      = param_dict
        self.date            = date

        self.itinerary       = None
        self.otp_params      = ''
        self.map_params      = ''

        self.coord_from      = self.get_param('From')
        self.coord_to        = self.get_param('To')
        self.distance        = self.get_param('Max dist')
        self.mode            = self.get_param('Mode')
        self.optimize        = self.get_param('Optimize')
        self.service         = self.get_param('Service')
        self.time            = self.get_param('Time', strip_all_spaces=True)
        self.description     = self.get_param('Description/notes')
        self.expect_output   = self.get_param('Expected output')
        self.expect_duration = self.get_param('Expected trip duration')
        self.expect_distance = self.get_param('Expected trip distance')
        self.expect_num_legs = self.get_param('Expected number of legs', warn_not_avail=False)
        self.arrive_by       = self.get_param('Arrive by')
        self.depart_by       = self.get_param('Depart by')

        # post process the load ... make params and urls, etc...
        self.date = self.get_date_param(self.date)
        self.init_url_params()
        self.url_distance()
        self.url_mode()
        self.url_optimize()
        self.url_time()
        self.url_param('ignoreRealtimeUpdates', 'true')

    def did_test_pass(self):
        ret_val = False
        if self.result is not None and self.result is TestResult.PASS:
            ret_val = True
        return ret_val

    def get_param(self, name, def_val=None, strip_all_spaces=False, warn_not_avail=True):
        return object_utils.get_striped_dict_val(self.csv_params, name, def_val, strip_all_spaces, warn_not_avail)

    def append_note(self, note=None):
        if note:
            self.description = "{}{}".format(self.description, note)

    def test_otp_result(self, strict=True):
        """ regexp test of the itinerary output for certain strings
        """
        if self.itinerary is None:
            self.result = TestResult.FAIL if strict else TestResult.WARN
            self.error_descript = "test_otp: itinerary is null"
        else:
            if len(self.itinerary) < MIN_SIZE_ITIN:
                self.result = TestResult.FAIL if strict else TestResult.WARN
                self.error_descript = "test_otp: looks small at {} characters".format(len(self.itinerary))
            else:
                # result properly sized ... now look for matches to expected data, etc...
                # import pdb; pdb.set_trace()
                self.error_descript = "test_otp: size {} characters.".format(len(self.itinerary))
                self.test_expected_response(self.expect_output, strict)
                if self.expect_duration is not None and len(self.expect_duration) > 0:
                    # TODO: this is XML -- needs to be changed to either XML or JSON
                    durations = re.findall('<itinerary>.*?<duration>(.*?)</duration>.*?</itinerary>', self.itinerary) 
                    error = 0.2
                    high = float(self.expect_duration) * (1 + error)
                    low = float(self.expect_duration) * (1 - error)
                    for duration in durations:
                        if int(duration) > high or int(duration) < low:
                            self.result = TestResult.FAIL if strict else TestResult.WARN
                            self.error_descript += "test_otp: an itinerary duration was different than expected by more than {0}%.".format(error * 100)
                            break
                if self.expect_num_legs is not None and len(self.expect_num_legs) > 0:
                    try:
                        values = [int(i) for i in self.expect_num_legs.split('|')]
                        if len(values) != 2:
                            raise ValueError
                        min_legs = values[0]
                        max_legs = values[1]
                        # TODO: this is XML -- needs to be changed to either XML or JSON
                        all_legs = re.findall('<itinerary>.*?<legs>(.*?)</legs>.*?</itinerary>', self.itinerary)
                        for legs in all_legs:
                            num_legs = len(re.findall('<leg .*?>', legs))
                            if num_legs > max_legs or num_legs < min_legs:
                                self.result = TestResult.FAIL if strict else TestResult.WARN
                                self.error_descript += "test_otp: an itinerary returned was not between {0} and {1} legs.".format(min_legs, max_legs)
                                break
                    except ValueError:
                        self.error_descript += "expected number of legs test not in 'min|max' format."

        if self.result == TestResult.FAIL:
            log.warn(self.error_descript + "\n  " + self.get_ws_url())

        return self.result

    def test_expected_response(self, expected_output, strict):
        ret_val = False
        if expected_output is not None and len(expected_output) > 0:
            regres = re.search(expected_output, self.itinerary)
            if regres is None:
                self.result = TestResult.FAIL if strict else TestResult.WARN
                self.error_descript += " - couldn't find " + expected_output + " in otp response"
                ret_val = True
        return ret_val

    def init_url_params(self):
        """
        """
        self.otp_params = 'fromPlace={0}&toPlace={1}'.format(self.coord_from, self.coord_to)

        self.map_params = self.otp_params
        if self.coord_from is None or self.coord_from == '' or self.coord_to is None or self.coord_to == '':
            self.error_descript = "no from and/or to coordinate for the otp url (skipping test) - from:{} to:{}".format(self.coord_from, self.coord_to)
            if self.expect_output:
                log.warn(self.error_descript)
            self.is_valid = False

    def url_param(self, name, param, default=None):
        """
        """
        p = param if param else default
        if p:
            self.otp_params += '&{0}={1}'.format(name, p)
            self.map_params += '&{0}={1}'.format(name, p)

    def url_distance(self, dist=None):
        self.url_param('maxWalkDistance', dist, self.distance)
        self.url_param('Walk', dist, self.distance)

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

    def url_service_next_month_weekday(self):
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

    def depart_by_check(self):
        if self.depart_by == 'FALSE':
            self.is_valid = False

    def arrive_by_check(self):
        if self.arrive_by == 'FALSE':
            self.is_valid = False

    def call_otp(self, url=None):
        """ calls the trip web service
        """
        self.itinerary = None
        start = time.time()
        url = url if url else self.get_ws_url()
        self.itinerary = otp_utils.call_planner_svc(url)
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
    def make_url(cls, url, separater="?submit&module=planner"):
        ret_val = url
        if ret_val is None:
            ret_val = "ERROR ERROR ERROR in test_suite.py line 284 ERROR ERROR ERROR"
        else:
            if not ret_val.startswith('http'):
                ret_val = "http://{}".format(url)
            if "?" not in ret_val:
                ret_val = "{}{}".format(ret_val, separater)
        return ret_val

    def get_ws_url(self):
        # import pdb; pdb.set_trace()
        # OTP needs *BOTH* a date and time parameter ... if you only have time, the request will fail
        if "time=" in self.otp_params and "date=" not in self.otp_params:
            d = date_utils.today_str()
            self.url_param('date', d)
        return "{}&{}".format(self.make_url(self.ws_url), self.otp_params)

    def get_map_url(self):
        return "{}&{}&debug_layers=true".format(self.make_url(self.map_url), self.map_params)

    def get_ridetrimetorg_url(self):
        return "http://ride.trimet.org?submit&" + self.map_params


class TestSuite(object):
    """ this class corresponds to a single .csv 'test suite'
    """

    def __init__(self, suite_dir, file):
        self.suite_dir = suite_dir
        self.file = file
        self.file_path = os.path.join(suite_dir, file)
        self.name = file
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

    def do_test(self, t, strict=True, num_tries=5):
        if t.is_valid:
            for i in range(1, num_tries):
                t.call_otp()
                time.sleep(1)
                if t.itinerary and len(t.itinerary) > MIN_SIZE_ITIN:
                    break
                time.sleep(i)

            t.test_otp_result(strict)
            self.tests.append(t)
            if t.result is TestResult.PASS:
                self.passes += 1
            elif t.result is TestResult.FAIL:
                log.info("test_suite: this test failed " + t.get_ws_url() + "\n")
                self.failures += 1
            sys.stdout.write(".")

    def get_tests(self):
        return self.tests

    def run(self, ws_url, map_url, date=None, run_test=True):
        """ iterate the list of tests from the .csv files, run the test (call otp), and check the output.
        """
        # return values for both arrive and depart urls
        ret_val=[]

        log.info("test_suite {0}: ******* date - {1} *******\n".format(self.name, datetime.datetime.now()))
        for i, p in enumerate(self.params):
            t = Test(p, i+2, ws_url, map_url, date)
            if t.is_valid is False:
                continue

            t.depart_by_check()
            ret_val.append(t.get_ws_url())
            if run_test:
                self.do_test(t)

            """ arrive by tests
            """
            t = Test(p, i+2, ws_url, map_url, date)
            t.url_arrive_by()
            t.append_note(" ***NOTE***: arrive by test ")
            t.arrive_by_check()
            ret_val.append(t.get_ws_url())
            if run_test:
                self.do_test(t, False)
        return ret_val

    def printer(self, ws_url, map_url, date):
        ret_val = ""
        urls = self.run(ws_url, map_url, date, run_test=False)
        for u in urls:
            ret_val = ret_val + u + "\n"
        return ret_val


class ListTestSuites(CacheBase):
    """ this class corresponds a list of TestSuites.  Created based on all .csv files in the base directory
    """

    def __init__(self, ws_url, map_url, suite_dir=None, date=None, filter=None):
        """ this class corresponds to a single .csv 'test suite'
        """
        #import pdb; pdb.set_trace()
        if suite_dir is None:
            suite_dir = self.sub_dir('suites')

        self.ws_url = ws_url
        self.map_url = map_url
        self.suite_dir = suite_dir
        self.date = date
        self.files = os.listdir(self.suite_dir)
        self.test_suites = []
        for f in self.files:
            if f.lower().endswith('.csv'):
                if filter and re.match('.*({})'.format(filter), f, re.IGNORECASE) is None:
                    continue
                t = TestSuite(self.suite_dir, f)
                self.test_suites.append(t)

    def has_errors(self):
        ret_val = False
        for t in self.test_suites:
            if t.failures > 0 or t.passes <= 0:
                ret_val = True
                break
        return ret_val

    def list_errors(self):
        ret_val = ""
        if self.has_errors():
            for t in self.test_suites:
                if t.failures > 0 or t.passes <= 0:
                    err = "test suite '{0}' has {1} error(s) and {2} passes\n".format(t.name, t.failures, t.passes)
                    ret_val = ret_val + err
                    log.info(err)
        return ret_val

    def get_suites(self):
        return self.test_suites

    def run(self):
        for ts in self.test_suites:
            ts.run(self.ws_url, self.map_url, self.date)

    def printer(self):
        ret_val = ""
        for ts in self.test_suites:
            ret_val = ret_val + ts.printer(self.ws_url, self.map_url, self.date)
        return ret_val

    def to_url_list(self):
        ret_val = []
        for ts in self.test_suites:
            urls = ts.run(self.ws_url, self.map_url, self.date, run_test=False)
            ret_val.extend(urls)
        return ret_val
