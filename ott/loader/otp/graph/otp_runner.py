""" 
run graph builder or OTP server
"""
import sys

from ott.utils import otp_utils
from ott.utils import web_utils
from ott.utils import file_utils
from ott.utils.cache_base import CacheBase

import logging
log = logging.getLogger(__file__)


class OtpRunner(CacheBase):
    """
    run OTP graph
    """
    graphs = None

    def __init__(self):
        super(OtpRunner, self).__init__('otp')
        self.graphs = otp_utils.get_graphs(self)

    @classmethod
    def get_args(cls):
        """ run the OTP server

            examples:
               bin/otp_run -s call (run the call server)
               bin/otp_run -v test (run the vizualizer with the test graph)
        """
        parser = otp_utils.get_initial_arg_parser('otp_runner')
        parser.add_argument('--server', '-s',  required=False, action='store_true', help="run 'named' graph in server mode")
        parser.add_argument('--all',    '-a',  required=False, action='store_true', help="run all graphs in server mode")
        parser.add_argument('--version', '-v', required=False, default="*",       help="filter version (default is '1.x')")
        parser.add_argument('--viz',    '-vz', required=False, action='store_true', help="run 'named' graph with the vizualizer client")
        parser.add_argument('--mem',    '-lm', required=False, action='store_true', help="set the jvm heap memory for the graph")
        args = parser.parse_args()
        return args, parser

    @classmethod
    def start_server(cls, graph, java_mem=None):
        status = False

        #import pdb; pdb.set_trace()
        dir = graph.get('dir')
        ver = graph.get('version')
        otp_utils.mv_new_files_into_place(dir, otp_version=ver)

        print("running {}".format(graph))
        status = otp_utils.run_otp_server(otp_version=ver, graph_dir=dir, java_mem=java_mem, **graph)
        return status

    @classmethod
    def version(cls):
        r = OtpRunner()
        args, parser = r.get_args()

        def vprint(graph):
            version, commit = otp_utils.get_otp_version(graph['dir'])
            print("{0: <15} {1: <27} {2}".format(graph['name'], version, commit))

        if args.all or 'all' == args.name or 'a' == args.name:
            for g in r.graphs:
                vprint(g)
        else:
            g = otp_utils.find_graph(r.graphs, args.name)
            vprint(g)

    @classmethod
    def run(cls):
        success = False

        r = OtpRunner()
        args, parser = r.get_args()

        java_mem = "-Xmx1236m" if args.mem else None
        if args.all or 'all' == args.name or 'a' == args.name:
            success = True
            for z in r.graphs:
                s = cls.start_server(graph=z, java_mem=java_mem)
                if s is False:
                    success = False
        else:
            graph = otp_utils.find_graph(r.graphs, args.name)
            if args.server:
                success = cls.start_server(graph=graph, java_mem=java_mem)
            elif args.viz:
                success = otp_utils.vizualize_graph(graph.get('dir'), "2.x", java_mem=java_mem)
            else:
                print("PLEASE select a option to either serve or vizualize graph {}".format(graph.get('name')))
                parser.print_help()
        return success

    @classmethod
    def restart_new_graphs(cls):
        """
        search configured graph cache's, and if we find a Graph.obj-new, we'll move that into place and
        restart the otp instance
        """
        r = OtpRunner()
        args, parser = r.get_args()

        success = True
        for g in r.graphs:
            if args.version != "*" and args.version != g.get('version'):
                log.warning("skipping graph {} ({}), since cmdline says to filter version {}".format(g.get('name'), g.get('version'), args.version))
                continue

            graph_path = otp_utils.get_graph_path(g.get('dir'), otp_version=g.get('version'))
            new_path = file_utils.make_new_path(graph_path)
            if file_utils.exists(new_path):
                log.info("restarting instance '{}' ... deploying file {} as the new Graph.obj".format(g.get('name'), new_path))
                s = cls.start_server(graph=g)
                if s is False:
                    success = False
            else:
                log.warning("a 'new' graph for instance '{}' does not exist (e.g., {} doesn't exist) - no reason to restart ... skipping.".format(g.get('name'), new_path))
        return success

    @classmethod
    def static_server_cfg(cls):
        r = OtpRunner()
        port = r.config.get('port', 'web', '50080')
        dir = r.config.get('dir',  'web', 'ott/loader/otp/graph')
        return port, dir

    @classmethod
    def static_server(cls):
        """ start a static server where """
        success = False
        port, dir = OtpRunner.static_server_cfg()
        success = web_utils.background_web_server(dir, port)
        return success


def main(argv=sys.argv):
    # import pdb; pdb.set_trace()
    OtpRunner.run()


if __name__ == '__main__':
    main()
