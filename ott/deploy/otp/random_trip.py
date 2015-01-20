import sys
import random

from ott.utils.parse import csv_reader

class RandomTrip():
    """ read in a .csv file full of points, and then output a set of test cases
    """
    def __init__(self):
        geotests = csv_reader.Csv.get_relative_dirname(__file__, "../../geocode/tests/geocodes.csv")
        csv_file = csv_reader.Csv('geocodes.csv', geotests)
        self.test_data = csv_file.open()
        self.name_list = []
        for t in self.test_data:
            self.name_list.append(t['name'])

    def make_tests(self, planner_url, params="?fromPlace={0}&toPlace={1}", num=500):
        for i in xrange(num):
            s = random.sample(self.name_list, 2)
            print planner_url + params.format(*s)

def ws_trips():
    from tm_ws_runner import WsTest
    h = WsTest.make_hostname()
    p,m = WsTest.make_urls(h)
    rt = RandomTrip()
    rt.make_tests(p)

def otp_trips():
    from test_runner import Test
    h = Test.make_hostname()
    p,m = Test.make_urls(h)
    rt = RandomTrip(p)

def main(argv=sys.argv):
    otp_trips()

if __name__ == '__main__':
    main()
