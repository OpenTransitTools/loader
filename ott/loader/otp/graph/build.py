""" Run build.py weekly (or daily) on the test maps servers (e.g., maps6 / maps10).  I will
    download the latest gtfs.zip file, check to see if it's newer than the last version
    I downloaded, and if so, build a new OTP Graph.

    @see deploy.py, which is a companion script that runs on the production servers, and
    deploys a new OTP graph into production.
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
from ott.loader.gtfs.info  import Info
from ott.loader.otp.preflight.test_runner import TestRunner

# constants
GRAPH_NAME = "Graph.obj"
GRAPH_FAILD = GRAPH_NAME + "-failed-tests"
GRAPH_SIZE = 35000000
OSM_SIZE   = 5000000
OSM_NAME   = "or-wa"

VLOG_NAME  = "otp.v"
TEST_HTML  = "otp_report.html"


class Build(CacheBase):
    """ build an OTP graph
    """
    feeds       = None
    graphs      = None
    expire_days = 45

    graph_name = GRAPH_NAME
    graph_size = GRAPH_SIZE
    graph_failed = GRAPH_FAILD


    def __init__(self, force_update=False, dont_update=False):
        super(Build, self).__init__('otp')
        self.feeds  = self.config.get_json('feeds', section='gtfs')
        self.graphs = self.config_graph_dirs(force_update, dont_update)

    def config_graph_dirs(self, force_update=False, dont_update=False):
        ''' read the config for graph specs like graph dir and web port (for running OTP)
            this routine will gather config .json files, .osm files and gtfs .zips into the graph folder
        '''
        graphs = self.config.get_json('graphs')

        # check for config list of graphs ... create a default if nothing exists
        if graphs is None or len(graphs) == 0:
            graphs = [otp_utils.get_graph_details(None)]  # returns a default graph config

        # run thru the graphs and
        for g in graphs:
            dir = otp_utils.config_graph_dir(g, self.this_module_dir, force_update)
            filter = g.get('filter')
            if force_update or not dont_update:
                OsmCache.check_osm_file_against_cache(dir)
                GtfsCache.check_feeds_against_cache(self.feeds, dir, force_update, filter)
        return graphs

    def is_old_otp(self, graph):
        ret_val = False
        if graph and graph.get('old'):
            ## TODO look at graph to determine if we should buidl old otp
            v = graph.get('old')
            if len(v) > 0:
                ret_val = True
        return ret_val

    def build_and_test_graphs(self, java_mem=None, force_update=False):
        ''' will build and test each of the graphs we have in self.graphs
        '''
        #import pdb; pdb.set_trace()
        ret_val = True
        for g in self.graphs:
            success = self.build_graph(g['dir'], java_mem, force_update)
            if success:
                success = self.deploy_test_graph(graph=g, java_mem=java_mem, force_update=force_update)
                if success:
                    self.update_vlog(graph=g)
                else:
                    ret_val = False
                    log.warn("graph {} didn't pass it's tests".format(g['name']))
            else:
                ret_val = False
                log.warn("graph build failed for graph {}".format(g['name']))
        return ret_val

    def only_test_graphs(self, java_mem=None, force_update=False):
        ''' will test each of the graphs we have in self.graphs
        '''
        ret_val = True
        for g in self.graphs:
            success = self.deploy_test_graph(graph=g, java_mem=java_mem, force_update=force_update)
            if success:
                self.update_vlog(graph=g)
            else:
                ret_val = False
                log.warn("graph {} didn't pass it's tests".format(g['name']))
        return ret_val

    def build_graph(self, graph_dir, java_mem=None, force_update=False):
        ''' will rebuild the graph...
        '''
        success = True

        # step 1: set some params
        rebuild_graph = force_update

        # step 2: check graph file is fairly recent and properly sized
        graph_path = os.path.join(graph_dir, self.graph_name)
        if not file_utils.exists_and_sized(graph_path, self.graph_size, self.expire_days):
            rebuild_graph = True

        # step 3: check the cache files
        if file_utils.dir_has_newer_files(graph_path, graph_dir, include_filter=".jar,.json,.osm,.zip"):
            rebuild_graph = True

        # step 4: build graph is needed
        if rebuild_graph:
            success = False
            # step 5a: run the builder multiple times until we get a good looking Graph.obj
            for n in range(1, 21):
                log.info(" build attempt {0} of a new graph ".format(n))
                otp_utils.run_graph_builder(graph_dir, java_mem=java_mem)
                time.sleep(10)
                if file_utils.exists_and_sized(graph_path, self.graph_size, self.expire_days):
                    success = True
                    break
        return success

    def deploy_test_graph(self, graph, suite_dir=None, java_mem=None, force_update=False):
        '''
        '''
        #suite_dir="/java/DEV/loader/ott/loader/otp/tests/suites" # debug test reporting with small test suites
        success = otp_utils.run_otp_server(java_mem=java_mem, **graph)
        if success:
            success = TestRunner.test_graph_factory(graph_dir=graph['dir'], port=graph['port'], suite_dir=suite_dir, delay=60)
        return success

    def update_vlog(self, graph):
        """ print out gtfs feed(s) version numbers and dates to the otp.v log file
        """
        dir = graph.get('dir', self.cache_dir)
        feed_msg = Info.get_cache_vlog_msgs(dir, self.feeds, graph.get('filter'))
        file_utils.update_vlog(dir, feed_msg)

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
        java_mem = "-Xmx1236m" if "low_mem" in argv else None
        force_update = object_utils.is_force_update()

        b = Build(force_update)
        if "mock" in argv:
            feed_details = b.get_gtfs_feed_details()
            b.update_vlog(feed_details)
            b.mv_failed_graph_to_good()
        elif "svr" in argv:
            success = otp_utils.run_otp_server(java_mem=java_mem, **b.graphs[0])
        elif "test" in argv:
            b.only_test_graphs(java_mem=java_mem, force_update=force_update)
        elif "viz" in argv:
            b.vizualize_graph(java_mem=java_mem)
        else:
            b.build_and_test_graphs(java_mem=java_mem, force_update=force_update)


def xmain(argv=sys.argv):
    #import pdb; pdb.set_trace()
    b = Build(dont_update=True)
    for g in b.graphs:
        log.warn(g['name'])
        b.update_vlog(g)

def main(argv=sys.argv):
    #import pdb; pdb.set_trace()
    Build.options(argv)

if __name__ == '__main__':
    main()
