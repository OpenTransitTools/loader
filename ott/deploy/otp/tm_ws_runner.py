import sys
from test_runner import *

class WsTest(Test):
    """ ...
    """
    def __init__(self, param_dict, line_number, date=None):
        super(WsTest, self).__init__(param_dict, line_number, date)

    def set_urls(self):
        #self.planner_url = "http://developer.trimet.org/ws/V1/trips/tripplanner"
        self.planner_url = "http://{0}/maps/tpws/V1/trips/tripplanner".format(self.host)
        self.map_url = "http://{0}/otp.html".format(self.host)

    @classmethod
    def to_coord(cls, param):
        p = param.split('::')
        return p[1]

    def init_url_params(self):
        """
        """
        f = self.to_coord(self.coord_from)
        t = self.to_coord(self.coord_to)
        self.otp_params = 'appID=8846D83E8CEE8EBC2D177B591&fromCoord={0}&toCoord={1}'.format(f, t)

Test.TestClass = WsTest

def main(argv=sys.argv):
    runner(argv)

if __name__ == '__main__':
    main()
