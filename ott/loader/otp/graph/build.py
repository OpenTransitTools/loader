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

from ott.utils import exe_utils
from ott.utils import file_utils
from ott.utils import object_utils
from ott.utils.cache_base import CacheBase

from ott.loader.gtfs.gtfs_cache import GtfsCache
from ott.loader.osm.osm_cache import OsmCache
from ott.loader.gtfs.info  import Info
from ott.loader.otp import otp_utils
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
    otp_path   = None
    feeds      = None
    graphs     = None

    graph_failed = GRAPH_FAILD
    graph_name = GRAPH_NAME
    graph_size = GRAPH_SIZE
    osm_name   = OSM_NAME
    osm_size   = OSM_SIZE
    vlog_name  = VLOG_NAME
    test_html  = TEST_HTML
    expire_days = 45

    def __init__(self, force_update=False):
        super(Build, self).__init__('otp')
        self.feeds  = self.config.get_json('feeds', section='gtfs')
        self.graphs = self.config_graph_dirs(force_update)

    def config_graph_dirs(self, force_update=False):
        ''' read the config for graph specs like graph dir and web port (for running OTP)
            this routine will gather config .json files, .osm files and gtfs .zips into the graph folder
        '''
        #import pdb; pdb.set_trace()
        graphs = self.config.get_json('graphs')
        if graphs is None or len(graphs) == 0:
            graphs = [otp_utils.get_graph_details(graphs)]

        for g in graphs:
            dir = otp_utils.config_graph_dir(g, self.this_module_dir)
            filter = g.get('filter', None)
            OsmCache.check_osm_file_against_cache(dir)
            GtfsCache.check_feeds_against_cache(self.feeds, dir, force_update, filter)

        return graphs

    def build_and_test_graphs(self, force_update=False, java_mem=None):
        ''' will rebuild the graph...
        '''


    def build_and_test_graph(self, force_update=False, java_mem=None):
        ''' will rebuild the graph...
        '''
        success = True

        # step 1: set some params
        rebuild_graph = force_update

        # step 2: check graph file is fairly recent and properly sized
        if not file_utils.exists_and_sized(self.graph_path, self.graph_size, self.expire_days):
            rebuild_graph = True

        # step 3: check the cache files
        # graph_date = file_utils.file_date(graph_path)
        if False: # file_utils.dir_has_newer_files(graph_date, graph_dir)
            rebuild_graph = True

        # step 4: print feed info
        feed_details = self.get_gtfs_feed_details()

        # step 5: build graph is needed
        if rebuild_graph:
            success = False
            # step 5a: run the builder multiple times until we get a good looking Graph.obj
            for n in range(1, 21):
                log.info(" build attempt {0} of a new graph ".format(n))
                self.run_graph_builder(java_mem=java_mem)
                time.sleep(10)
                if file_utils.exists_and_sized(self.graph_path, self.graph_size, self.expire_days):
                    success = True
                    break

            # step 5b: test the graph
            if success:
                self.deploy_test_graph(java_mem=java_mem)
                success = self.run_graph_tests()
                if success:
                    self.update_vlog()
                    self.update_asset_log()
                    success = True
        return success

    def deploy_test_graph(self, sleep=75, java_mem=None):
        ''' launch the server in a separate process ... then sleep for 75 seconds to give the server time to load the data
        '''
        file_utils.cd(self.this_module_dir)
        cmd='-server -jar {} --port {} --router "" --graphs {}'.format(self.otp_path, self.port, self.cache_dir)
        exe_utils.run_java(cmd, fork=True, big_xmx=java_mem)
        time.sleep(sleep)

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
                r = info.get_feed_date_range()
                v = info.get_feed_version()
                d = info.get_days_since_stats()
                cp['start'] = r[0]
                cp['end'] = r[1]
                cp['version'] = v
                cp['since'] = d[0]
                cp['until'] = d[1]
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

    @classmethod
    def factory(cls):
        return Build()

    @classmethod
    def options(cls, argv):
        ''' main entry point for command line graph build app
        '''
        java_mem = None
        if "low_mem" in argv:
            java_mem = "-Xmx1236m"

        b = cls.factory()
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
            b.build_and_test_graph(force_update=object_utils.is_force_update(), java_mem=java_mem)


def main(argv=sys.argv):
    #import pdb; pdb.set_trace()
    #Build.options(argv)
    b = Build.factory()

if __name__ == '__main__':
    main()
