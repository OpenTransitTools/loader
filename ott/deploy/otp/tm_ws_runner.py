import sys
from test_runner import *

class WsTest(Test):
    """ ...
    """
    def __init__(self, param_dict, line_number, date=None):
        super(WsTest, self).__init__(param_dict, line_number, date)

    def set_urls(self):
        p,m = self.make_urls(self.host)
        self.planner_url = p
        self.map_url = m

    @classmethod
    def make_urls(cls, host):
        #self.planner_url = "http://developer.trimet.org/ws/V1/trips/tripplanner"
        planner_url = "http://{0}/maps/tpws/V1/trips/tripplanner".format(host)
        map_url = "http://{0}/otp.html".format(host)
        return planner_url, map_url

    @classmethod
    def to_coord(cls, param):
        ret_val = None
        p = param.split('::')
        if p and len(p) > 0:
            ret_val = p[0]
            if len(p) > 1:
                ret_val = p[1]
        return ret_val

    def init_url_params(self):
        """
        """
        try:
            f = self.to_coord(self.coord_from)
            t = self.to_coord(self.coord_to)
            self.otp_params = 'appID=8846D83E8CEE8EBC2D177B591&fromCoord={0}&toCoord={1}'.format(f, t)
        except:
            print "**************************"
            print "Error: this might not be a test, but a comment "
            print self.__dict__
            print "**************************"
            print "\n\n"

Test.TestClass = WsTest

def main(argv=sys.argv):
    runner(argv)

if __name__ == '__main__':
    main()
