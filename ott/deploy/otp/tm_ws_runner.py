import sys
from test_runner import *

class WsTest(Test):
    """ ...
    """
    def __init__(self, param_dict, line_number, date=None):
        super(WsTest, self).__init__(param_dict, line_number, date)


    def init_url_params(self):
        """
        """
        self.otp_params = 'from={0}&to={1}'.format(self.coord_from, self.coord_to)


Test.TestClass = WsTest

def main(argv=sys.argv):
    runner(argv)

if __name__ == '__main__':
    main()
