import sys
from test_runner import *


class WsTest(Test):
    """ Nov 2018 -- TODO is this code used?
    """
    def __init__(self, param_dict, line_number, date=None):
        super(WsTest, self).__init__(param_dict, line_number, date)

    def set_urls(self):
        p,m = self.make_urls(self.host)
        self.planner_url = p
        self.map_url = m

    def get_date_param(self, date, fmt="%m-%d-%Y"):
        super(WsTest, self).get_date_param(date, fmt)

    def test_expected_response(self, expected_output, ret_val, strict):
        if expected_output and "interlineWithPreviousLeg" in expected_output:
            ret_val = super(WsTest, self).test_expected_response("thru-route", ret_val, strict)
        return ret_val

    @classmethod
    def make_urls(cls, host):
        #self.planner_url = "http://developer.trimet.org/ws/V1/trips/tripplanner"
        planner_url = "http://{0}/maps/tpws/V1/trips/tripplanner".format(host)
        map_url = "http://{0}/tmap.html?debug".format(host)
        return planner_url, map_url

    @classmethod
    def to_coord(cls, param):
        """ return cleaned param
        """
        ret_val = param
        p = param.split('::')
        if p and len(p) > 0:
            ret_val = p[0]
            if len(p) > 1:
                ret_val = p[1]
        return ret_val

    @classmethod
    def coord_or_name(cls, param, coord="Coord", place="Place"):
        """ return either 'Coord' or 'Place' based on whether string looks like a coord or name
        """
        ret_val = place
        try:
            p = param.split(',')
            if isinstance(p[0].strip(), float) and isinstance(p[1].strip(), float):
                ret_val = coord
        except:
            pass
        return place

    def get_map_url(self):
        return "{0}&{1}".format(self.make_url(self.map_url), self.map_params)

    def init_url_params(self):
        """
        """
        try:
            f = self.to_coord(self.coord_from)
            t = self.to_coord(self.coord_to)
            self.otp_params = 'appID=8846D83E8CEE8EBC2D177B591&from{0}={1}&to{2}={3}'.format(self.coord_or_name(f), f, self.coord_or_name(t), t)
            self.map_params = 'fromPlace={0}&toPlace={1}'.format(f, t)
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
