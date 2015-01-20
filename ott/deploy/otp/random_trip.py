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
            p1 = s[0].replace(' ', '%20').replace('&', '%26').replace('#', '%23')
            p2 = s[1].replace(' ', '%20').replace('&', '%26').replace('#', '%23')
            p = params.format(p1, p2)
            u = planner_url + "?" + p
            self.url_list.append(u)

    def call_urls(self):
        for u in self.url_list:
            #import pdb; pdb.set_trace()
            itinerary = Test.static_call_otp(u)
            print u
            if itinerary:
                if len(itinerary) < 1000:
                    error_descript = "test_otp_result: itinerary content looks small at " + str(len(itinerary)) + " characters."
                    print error_descript
                if "Uncertain Location" in itinerary:
                    error_descript = "test_otp_result: itinerary had ambiguous geocode"
                    print error_descript
            else:
                print "Planner didn't return anything (null)..."

def zws_trips():
    s = Test.static_call_otp("http://maps7.trimet.org/maps/tpws/V1/trips/tripplanner?fromPlace=6236%20SE%20134TH%20AVE&toPlace=9341%20N%20FISKE%20AVE")
    print s

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
