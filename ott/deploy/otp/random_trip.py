import sys
import random
import urllib

from ott.utils.parse import csv_reader

from tm_ws_runner import WsTest
from test_runner import Test


def_header="Description/notes,From,To,Mode,Time,Service,Optimize,Max dist,Arrive by,Depart by,Expected output,Expected number of legs,Expected trip duration,Expected trip distance,Passes?"

class RandomTrip():
    """ read in a .csv file full of points, and then output a set of test cases
    """
    def __init__(self, num=500):
        self.name_list = []
        self.from_to_list = []

        geotests = csv_reader.Csv.get_relative_dirname(__file__, "../../geocode/tests/geocodes.csv")
        csv_file = csv_reader.Csv('geocodes.csv', geotests)
        self.test_data = csv_file.open()

        for t in self.test_data:
            self.name_list.append(t['name'])

        for i in xrange(num):
            s = random.sample(self.name_list, 2)
            self.from_to_list.append(s)

    @classmethod
    def escape(cls, s):
        return s.replace(' ', '%20').replace('&', '%26').replace('#', '%23')

    @classmethod
    def make_test_urls(cls, planner_url, from_to_list, params="fromPlace={0}&toPlace={1}"):
        url_list = []
        for p in from_to_list:
            p = params.format(cls.escape(p[0]), cls.escape(p[1]))
            u = planner_url + "?" + p
            url_list.append(u)
        return url_list

    @classmethod
    def make_suite_csv(cls, from_to_list, file_name=None, suite_header=def_header, suite_format="test {0},{1},{2},,4:40 PM,,,,,,leg,,,,"):
        print suite_header
        for i, p in enumerate(from_to_list):
            print suite_format.format(i+1, *p)

    def call_urls(self, url_list):
        for u in url_list:
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
    rt.make_suite_csv(rt.from_to_list)

def otp_trips():
    h = Test.make_hostname()
    p,m = Test.make_urls(h)
    rt = RandomTrip()
    rt.make_tests(p)
    rt.call_urls()

def main(argv=sys.argv):
    #otp_trips()
    ws_trips()

if __name__ == '__main__':
    main()
