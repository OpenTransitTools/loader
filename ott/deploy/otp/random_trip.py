import sys
from test_runner import *

class RandomTrip(Test):
    """ read in a .csv file full of points, and then output a set of test cases
    """
    def __init__(self, param_dict, line_number, date=None):
        super(RandomTrip, self).__init__(param_dict, line_number, date)

    def set_urls(self):
        #self.planner_url = "http://developer.trimet.org/ws/V1/trips/tripplanner"
        self.planner_url = "http://{0}/maps/tpws/V1/trips/tripplanner".format(self.host)
        self.map_url = "http://{0}/otp.html".format(self.host)

Test.TestClass = RandomTrip

def main(argv=sys.argv):
    runner(argv)

if __name__ == '__main__':
    main()
