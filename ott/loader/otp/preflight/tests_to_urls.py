import sys

from ott.utils import otp_utils
from test_suite import ListTestSuites

def to_urls(name, port):
    ws_url, map_url = otp_utils.get_test_urls_from_config(port=port)
    lts = ListTestSuites(ws_url, map_url, None)
    lts.printer()

def main(argv=sys.argv):
    parser = otp_utils.get_initial_arg_parser()
    args = parser.parse_args()

    graphs = otp_utils.get_graphs_from_config()
    if args.name == "all":
        for g in graphs:
            to_urls(g['name'], g['port'])
    else:
        g = otp_utils.find_graph(graphs, args.name)
        print g
        if g:
            to_urls(g['name'], g['port'])
        else:
            print "couldn't find graph {}".format(args.name)

if __name__ == '__main__':
    main()
