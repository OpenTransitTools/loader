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

    def find_graph(self, graph_name):
        ''' will build and test each of the graphs we have in self.graphs
        '''
        #import pdb; pdb.set_trace()
        ret_val = None
        for g in self.graphs:
            if graph_name in g['name']:
                ret_val = g
                break
        return ret_val

    def vizualize_graph(self, java_mem=None, graph_index=0):
        '''
        '''
        if graph_index >= len(self.graphs):
            graph_index = 0
        otp_utils.vizualize_graph(graph_dir=self.graphs[graph_index]['dir'], java_mem=java_mem)

    @classmethod
    def options(cls, argv):
        ''' main entry point for command line graph build app
        '''
        #import pdb; pdb.set_trace()
        java_mem = "-Xmx1236m" if "low_mem" in argv else None

        b = Run()
        if "svr" in argv:
            success = otp_utils.run_otp_server(java_mem=java_mem, **b.graphs[0])
        elif "viz" in argv:
            b.vizualize_graph(java_mem=java_mem)


def main(argv=sys.argv):
    Run.options(argv)

if __name__ == '__main__':
    main()
