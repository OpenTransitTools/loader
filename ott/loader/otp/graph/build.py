""" Run build.py weekly (or daily) on the test maps servers (e.g., maps6 / maps10).  I will
    download the latest gtfs.zip file, check to see if it's newer than the last version
    I downloaded, and if so, build a new OTP Graph.

    @see deploy.py, which is a companion script that runs on the production servers, and
    deploys a new OTP graph into production.
"""
import os
import sys
import copy
import time
import datetime
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


class B(object):
    osm_name   = OSM_NAME
    osm_size   = OSM_SIZE
    vlog_name  = VLOG_NAME
    test_html  = TEST_HTML

    # step 4: print feed info
    #    feed_details = self.get_gtfs_feed_details()


    def get_gtfs_feed_details(self):
        ''' returns updated [] with feed details
        TODO: refacotr
        '''
        ret_val = []
        try:
            for g in self.feeds:
                cp = copy.copy(g)
                gtfs_path = os.path.join(self.cache_dir, cp['name'])
                info = Info(gtfs_path)
                vlog = info.get_feed_vlog_info(cp['name'])
                cp.update(vlog)
                ret_val.append(cp)
        except Exception, e:
            log.warn(e)
            self.report_error("GTFS files are in a questionable state")
        return ret_val

    def run_graph_tests(self):
        ''' returns updated [] with feed details
        '''
        t = TestRunner()
        t.run()
        t.report(self.cache_dir)
        if t.has_errors():
            log.info('GRAPH TESTS: There were errors!')
        else:
            log.info('GRAPH TESTS: Nope, no errors')

    def mv_failed_graph_to_good(self):
        """ move the failed graph to prod graph name if prod graph doesn't exist and failed does exist
        """
        exists = os.path.exists(self.graph_path)
        if not exists:
            fail_path = os.path.join(self.cache_dir, self.graph_failed)
            exists = os.path.exists(fail_path)
            if exists:
                file_utils.mv(fail_path, self.graph_path)

    def update_asset_log(self):
        ''' TODO see if this is needed to inventory OSM and GTFS
            note that we do some inventorying in vlog
        '''

    def update_vlog(self, feeds_details):
        """ print out gtfs feed(s) version numbers and dates to the otp.v log file
        """
        if feeds_details and len(feeds_details) > 0:
            msg = "\nUpdated graph on {} with GTFS feed(s):\n".format(datetime.datetime.now().strftime("%B %d, %Y @ %I:%M %p"))
            for f in feeds_details:
                msg += "  {} - date range {} to {} ({:>3} more calendar days), version {}\n".format(f['name'], f['start'], f['end'], f['until'], f['version'])
            vlog = os.path.join(self.cache_dir, self.vlog_name)
            f = open(vlog, 'a')
            f.write(msg)
            f.flush()
            f.close()

    def report_error(self, msg):
        ''' override me to do things like emailing error reports, etc... '''
        log.error(msg)


class Build(CacheBase):
    """ build an OTP graph
    """
    feeds       = None
    graphs      = None
    expire_days = 45

    graph_name = GRAPH_NAME
    graph_size = GRAPH_SIZE
    graph_failed = GRAPH_FAILD

    def __init__(self, force_update=False):
        super(Build, self).__init__('otp')
        self.feeds  = self.config.get_json('feeds', section='gtfs')
        self.graphs = self.config_graph_dirs(force_update)

    def config_graph_dirs(self, force_update=False):
        ''' read the config for graph specs like graph dir and web port (for running OTP)
            this routine will gather config .json files, .osm files and gtfs .zips into the graph folder
        '''
        graphs = self.config.get_json('graphs')

        # check for config list of graphs ... create a default if nothing exists
        if graphs is None or len(graphs) == 0:
            graphs = [otp_utils.get_graph_details(None)]  # returns a default graph config

        # run thru the graphs and
        for g in graphs:
            dir = otp_utils.config_graph_dir(g, self.this_module_dir)
            filter = g.get('filter', None)
            OsmCache.check_osm_file_against_cache(dir)
            GtfsCache.check_feeds_against_cache(self.feeds, dir, force_update, filter)

        return graphs

    def build_and_test_graphs(self, java_mem=None, force_update=False):
        ''' will build and test each of the graphs we have in self.graphs
        '''
        ret_val = True
        for g in self.graphs:
            success = self.build_graph(g['dir'], java_mem, force_update)
            if success:
                otp_utils.run_otp_server(g['dir'], g['port'], java_mem)
                success = self.run_graph_tests()
                if success:
                    self.update_vlog()
                    self.update_asset_log()
                else:
                    ret_val = False
                    log.warn("graph {} didn't pass it's tests".format(g['name']))
            else:
                ret_val = False
                log.warn("graph build failed for graph {}".format(g['name']))
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
        if file_utils.dir_has_newer_files(graph_path, graph_dir):
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
        elif "test" in argv:
            b.deploy_test_graph(java_mem=java_mem)
            b.run_graph_tests()
        elif "build" in argv:
            b.run_graph_builder(java_mem=java_mem)
            b.deploy_test_graph(java_mem=java_mem)
        elif "dep" in argv:
            b.deploy_test_graph(java_mem=java_mem)
        elif "viz" in argv:
            b.vizualize_graph(java_mem=java_mem)
        else:
            b.build_and_test_graphs(force_update=force_update, java_mem=java_mem)


def main(argv=sys.argv):
    #import pdb; pdb.set_trace()
    Build.options(argv)

if __name__ == '__main__':
    main()
