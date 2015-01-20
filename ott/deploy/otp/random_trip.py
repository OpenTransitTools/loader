import sys
import random
import urllib

from ott.utils.parse import csv_reader

from tm_ws_runner import WsTest
from test_runner import Test

class RandomTrip():
    """ read in a .csv file full of points, and then output a set of test cases
    """
    def __init__(self):
        self.name_list = []
        self.url_list = []

        geotests = csv_reader.Csv.get_relative_dirname(__file__, "../../geocode/tests/geocodes.csv")
        csv_file = csv_reader.Csv('geocodes.csv', geotests)
        self.test_data = csv_file.open()
        for t in self.test_data:
            self.name_list.append(t['name'])

    def make_tests(self, planner_url, params="fromPlace={0}&toPlace={1}", num=500):
        for i in xrange(num):
            s = random.sample(self.name_list, 2)
            p = params.format(*s)
            u = planner_url + "?" + urllib.quote_plus(p)
            self.url_list.append(u)

    def call_urls(self):
        for u in self.url_list:
            Test.static_call_otp(u)

def ws_trips():
    h = WsTest.make_hostname()
    p,m = WsTest.make_urls(h)
    rt = RandomTrip()
    rt.make_tests(p)
    rt.call_urls()

def otp_trips():
    h = Test.make_hostname()
    p,m = Test.make_urls(h)
    rt = RandomTrip(p)
    rt.make_tests(p)
    rt.call_urls()

def main(argv=sys.argv):
    otp_trips()

if __name__ == '__main__':
    main()
