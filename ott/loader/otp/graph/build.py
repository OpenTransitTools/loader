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
        graphs = otp_utils.get_graphs(self)

        # check for config list of graphs ... create a default if nothing exists
        if graphs is None or len(graphs) == 0:
            graphs = [otp_utils.get_graph_details(None)]  # returns a default graph config

        # run thru the graphs and
        for g in graphs:
            dir = otp_utils.config_graph_dir(g, self.this_module_dir)
            filter = g.get('filter')
            if force_update or not dont_update:
                OsmCache.check_osm_file_against_cache(dir)
                GtfsCache.check_feeds_against_cache(self.feeds, dir, force_update, filter)
        return graphs

    def build_and_test_graphs(self, java_mem=None, force_update=False):
        ''' will build and test each of the graphs we have in self.graphs
        '''
        #import pdb; pdb.set_trace()
        ret_val = True
        for g in self.graphs:
            success, rebuilt = self.build_graph(g['dir'], java_mem, force_update)
            if success and rebuilt:
                success = self.test_graph(graph=g, java_mem=java_mem)
                ret_val = success
            elif not success:
                ret_val = False
                log.warn("graph build failed for graph {}".format(g['name']))
        return ret_val

    def only_test_graphs(self, java_mem=None, break_on_fail=False, start_server=True):
        ''' will test each of the graphs we have in self.graphs
        '''
        ret_val = True
        for g in self.graphs:
            success = self.test_graph(graph=g, java_mem=java_mem, start_server=start_server)
            if not success:
                ret_val = False
                if break_on_fail:
                    break
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
                time.sleep(60)
                if file_utils.exists_and_sized(graph_path, self.graph_size, self.expire_days):
                    success = True
                    break
                else:
                    log.warn("\n\nGRAPH DIDN'T BUILD ... WILL TRY TO BUILD AGAIN\n\n")
                    time.sleep(3)
        return success, rebuild_graph

    def test_graph(self, graph, suite_dir=None, java_mem=None, start_server=True):
        ''' will test a given graph against a suite of tests
        '''
        #suite_dir="/java/DEV/loader/ott/loader/otp/tests/suites" # debug test reporting with small test suites
        success = True
        delay = 1
        if start_server:
            success = otp_utils.run_otp_server(java_mem=java_mem, **graph)
            delay = 60
        if success:
            success = TestRunner.test_graph_factory(graph_dir=graph['dir'], port=graph['port'], suite_dir=suite_dir, delay=delay)
            if success:
                self.update_vlog(graph=graph)
            else:
                log.warn("graph {} didn't pass it's tests".format(graph['name']))
        else:
            log.warn("was unable to run OTP server for graph {}".format(graph['name']))
        return success

    def update_vlog(self, graph):
        """ print out gtfs feed(s) version numbers and dates to the otp.v log file
        """
        dir = graph.get('dir', self.cache_dir)
        feed_msg = Info.get_cache_msgs(dir, self.feeds, graph.get('filter'))
        otp_utils.append_vlog_file(dir, feed_msg)

    @classmethod
    def get_args(cls):
        ''' build a certain graph or just run tests (or no tests), etc...

            examples:
        '''
        import argparse
        parser = argparse.ArgumentParser(prog='otp-build', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
        parser.add_argument('name', default="all", help="Name of GTFS graph folder in the 'cache' build (e.g., 'all', 'prod', 'test' or 'call')")
        parser.add_argument('--test',       '-t',  action='store_true', help="to just run tests vs. building the graph")
        parser.add_argument('--no_tests',    '-n', action='store_true', help="build graph w/out testing")
        parser.add_argument('--force',       '-f', action='store_true', help="force a rebuild regardless of cache state and data update")
        parser.add_argument('--dont_update', '-d', action='store_true', help="don't update data regardless of state")
        parser.add_argument('--mock',        '-m', action='store_true', help="mock up the otp.v to make it look like the graph built and tested")
        parser.add_argument('--mem',        '-lm', action='store_true', help="should we run otp/java with smaller memory footprint?")
        parser.add_argument('--email',       '-e', help="email address(es) to be contacted if we can't build a graph, or the tests don't pass.")
        args = parser.parse_args()
        return args, parser

    @classmethod
    def build(cls):
        success = False

        build_success = True
        test_success = True
        server_success = True

        args, parser = Build.get_args()
        b = Build(force_update=args.force, dont_update=args.dont_update)
        java_mem = "-Xmx1236m" if args.mem else None

        if args.mock:
            feed_details = b.get_gtfs_feed_details()
            b.update_vlog(feed_details)
            b.mv_failed_graph_to_good()
            success = True
        else:
            if args.name != "all":
                graph = otp_utils.find_graph(b.graphs, args.name)
                if graph:
                    # either build and/or test a single named graph
                    if not args.test:
                        success, rebuilt = b.build_graph(graph['dir'], java_mem=java_mem, force_update=args.force)
                    if not args.no_tests:
                        success = b.test_graph(graph, java_mem=java_mem, start_server=args.force)
                else:
                    log.warn("I don't know how to build graph '{}'".format(args.name))
                    success = False
            else:
                # build and/or test all graphs in the config file
                if args.test:
                    success = b.only_test_graphs(java_mem=java_mem, start_server=args.force)
                else:
                    success = b.build_and_test_graphs(java_mem=java_mem, force_update=args.force)

        if args.email and (not success or args.force):
            #otp_utils.build_test_email(emails=args.email, build_status=build_success, test_status=test_success, server_status=server_success)
            otp_utils.send_build_test_email(args.email)

        return success


def main(argv=sys.argv):
    #import pdb; pdb.set_trace()
    Build.build()

if __name__ == '__main__':
    main()
