import sys
from test_runner import *

class WsTest(Test):
    """ ...
    """
    def init_url_params(self):
        """
        """
        print "Foo"
        self.otp_params = 'fromPlace={0}&toPlace={1}'.format(self.coord_from, self.coord_to)
        if self.coord_from == None or self.coord_from == '' or self.coord_to == None or self.coord_to == '':
            if self.coord_from != None or self.coord_to != None:
                self.error_descript = "no from and/or to coordinate for the otp url (skipping test) - from:" + str(self.coord_from) + ' to:' + str(self.coord_to)
                logging.warn(self.error_descript)
            self.is_valid = False


Test.TestClass = WsTest

def main(argv=sys.argv):
    runner(argv)

if __name__ == '__main__':
    main()
