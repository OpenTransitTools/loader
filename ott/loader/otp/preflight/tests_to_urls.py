import sys

from ott.utils import otp_utils
from test_suite import ListTestSuites

def to_urls(name, hostname, port, dir, filter):
    ws_url, map_url = otp_utils.get_test_urls_from_config(hostname=hostname, port=port)
    lts = ListTestSuites(ws_url=ws_url, map_url=map_url, suite_dir=dir, filter=filter)
    lts.printer()

def main():
    parser = otp_utils.get_initial_arg_parser()
    parser.add_argument('--hostname', '-hn', '-d', help="specify the hostname for the test url")
    args = parser.parse_args()

    graphs = otp_utils.get_graphs_from_config()
    if args.name == "all":
        for g in graphs:
            to_urls(g['name'], args.hostname, g['port'])
    else:
        g = otp_utils.find_graph(graphs, args.name)
        print g
        if g:
            to_urls(g['name'], args.hostname, g['port'], g['dir'], args.test_suite)
        else:
            print "couldn't find graph {}".format(args.name)

if __name__ == '__main__':
    main()
