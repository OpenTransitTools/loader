""" Run
"""
import sys
import time
import logging
log = logging.getLogger(__file__)

from ott.utils import otp_utils
from ott.utils import web_utils
from ott.utils.cache_base import CacheBase


class Run(CacheBase):
    """ run OTP graph
    """
    graphs = None

    def __init__(self):
        super(Run, self).__init__('otp')
        self.graphs = otp_utils.get_graphs(self)

    @classmethod
    def get_args(cls):
        ''' run the OTP server

            examples:
               bin/otp_run -s call (run the call server)
               bin/otp_run -v test (run the vizualizer with the test graph)
        '''
        parser = otp_utils.get_initial_arg_parser()
        parser.add_argument('--server', '-s',  required=False, action='store_true', help="run 'named' graph in server mode")
        parser.add_argument('--all',    '-a',  required=False, action='store_true', help="run all graphs in server mode")
        parser.add_argument('--viz',    '-v',  required=False, action='store_true', help="run 'named' graph with the vizualizer client")
        parser.add_argument('--mem',    '-lm', required=False, action='store_true', help="set the jvm heap memory for the graph")
        args = parser.parse_args()
        return args, parser

    @classmethod
    def run(cls):
        #import pdb; pdb.set_trace()
        success = False

        r = Run()
        args, parser = r.get_args()

        graph = otp_utils.find_graph(r.graphs, args.name)
        java_mem = "-Xmx1236m" if args.mem else None
        if args.all or 'all' == args.name or 'a' == args.name:
            success = True
            for z in r.graphs:
                print "running {}".format(z)
                time.sleep(2)
                s = otp_utils.run_otp_server(java_mem=java_mem, **z)
                if s == False:
                    success = False
        elif args.server:
            success = otp_utils.run_otp_server(java_mem=java_mem, **graph)
        elif args.viz:
            success = otp_utils.vizualize_graph(graph_dir=graph['dir'], java_mem=java_mem)
        else:
            print "PLEASE select a option to either serve or vizualize graph {}".format(graph['name'])
            parser.print_help()
        return success

    @classmethod
    def static_server_cfg(cls):
        r = Run()
        port = r.config.get('port', 'web', '50080')
        dir  = r.config.get('dir',  'web', 'ott/loader/otp/graph')
        return port, dir

    @classmethod
    def static_server(cls):

        ''' start a static server where
        '''
        success = False
        port, dir = Run.static_server_cfg()
        success = web_utils.background_web_server(dir, port)
        return success

def main(argv=sys.argv):
    Run.run()

if __name__ == '__main__':
    main()
