import sys
from ott.utils.parse import csv_reader

class RandomTrip():
    """ read in a .csv file full of points, and then output a set of test cases
    """
    def __init__(self, planner_url):
        geotests = csv_reader.Csv.get_relative_dirname(__file__, "../../geocode/tests/geocodes.csv")
        csv_file = csv_reader.Csv('geocodes.csv', geotests)
        test_data = csv_file.open()
        for t in test_data:
            print t


def ws_trips():
    from ws_test_runner import WsTest
    h = WsTest.make_hostname()
    p,m = WsTest.make_urls(h)
    rt = RandomTrip(p)

def otp_trips():
    from test_runner import Test
    h = Test.make_hostname()
    p,m = Test.make_urls(h)
    rt = RandomTrip(p)

def main(argv=sys.argv):
    otp_trips()

if __name__ == '__main__':
    main()
