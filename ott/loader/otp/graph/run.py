""" Run
"""
import os
import sys
import time
import logging
log = logging.getLogger(__file__)

from ott.utils import otp_utils
from ott.utils import file_utils
from ott.utils import object_utils
from ott.utils.cache_base import CacheBase

from ott.loader.gtfs.gtfs_cache import GtfsCache
from ott.loader.osm.osm_cache import OsmCache


class Run(CacheBase):
    """ run OTP graph
    """
    graphs = None

    def __init__(self):
        super(Run, self).__init__('otp')
        self.graphs = otp_utils.get_graphs(self)

    @classmethod
    def get_args(cls):
        ''' database load command-line arg parser and help util...

            examples:
               bin/gtfs_fix SAM.zip -a -r -f "^86" -t "SAM"
               bin/gtfs_fix SMART.zip -a -r -f "^108" -t "SMART"
        '''
        import argparse
        parser = argparse.ArgumentParser(prog='otp-run', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
        parser.add_argument('name', help="Name of GTFS graph folder in the 'cache' run (e.g., TRIMET)")
        parser.add_argument('--server',     '-s', required=False, action='store_true', help="string (regex) to find in files")
        parser.add_argument('--viz',        '-v', required=False, action='store_true',  help="string to replace found regex strings")
        parser.add_argument('--mem', '-lm', '-m', required=False, action='store_true',  help="string to replace found regex strings")
        args = parser.parse_args()
        return args, parser

    @classmethod
    def run(cls):
        success = False

        r = Run()
        args, parser = r.get_args()

        graph = otp_utils.find_graph(r.graphs, args.name)
        java_mem = "-Xmx1236m" if args.mem else None
        if args.server:
            success = otp_utils.run_otp_server(java_mem=java_mem, **graph)
        elif args.viz:
            success = otp_utils.vizualize_graph(graph_dir=graph['dir'], java_mem=java_mem)
        else:
            print "PLEASE select a option to either serve or vizualize graph {}".format(graph['name'])
            parser.print_help()
        return success


def main(argv=sys.argv):
    Run.run()

if __name__ == '__main__':
    main()
