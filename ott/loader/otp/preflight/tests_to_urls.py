import sys

from ott.utils import otp_utils
from test_suite import ListTestSuites

def main(argv=sys.argv):
    ws_url, map_url = otp_utils.get_test_urls_from_config()
    lts = ListTestSuites(ws_url, map_url, None)
    lts.printer()

if __name__ == '__main__':
    main()
