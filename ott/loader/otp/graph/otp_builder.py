""" Run build.py weekly (or daily) on the test maps servers (e.g., maps6 / maps10).  I will
    download the latest gtfs.zip file, check to see if it's newer than the last version
    I downloaded, and if so, build a new OTP Graph.

    @see deploy.py, which is a companion script that runs on the production servers, and
    deploys a new OTP graph into production.
"""
from ott.utils import otp_utils
from ott.utils import file_utils
from ott.utils.cache_base import CacheBase

from ott.loader.gtfs.gtfs_cache import GtfsCache
from ott.osm.osm_cache import OsmCache
from ott.osm.stats.osm_info import OsmInfo
from ott.loader.gtfs.gtfs_info import GtfsInfo
from ott.loader.otp.preflight.test_runner import TestRunner

import os
import sys
import time
import logging
log = logging.getLogger(__file__)


class OtpBuilder(CacheBase):
    """ build an OTP graph
    """
    feeds = None
    graphs = None
    expire_days = 45

    graph_name = otp_utils.GRAPH_NAME
    graph_size = 35000000
    graph_failed = graph_name + "-failed-tests"

    def __init__(self, force_update=False, dont_update=False):
        super(OtpBuilder, self).__init__('otp')
        self.feeds = self.config.get_json('feeds', section='gtfs')
        self.graphs = self.config_graph_dirs(force_update, dont_update)

    def config_graph_dirs(self, force_update=False, dont_update=False):
        """ read the config for graph specs like graph dir and web port (for running OTP)
            this routine will gather config .json files, .osm files and gtfs .zips into the graph folder
        """
        graphs = otp_utils.get_graphs(self)

        # check for config list of graphs ... create a default if nothing exists
        if force_update and (graphs is None or len(graphs) == 0):
            graphs = [otp_utils.get_graph_details(None)]  # returns a default graph config

        # run thru the graphs and
        if graphs:
            for g in graphs:
                graph_dir = otp_utils.config_graph_dir(g, self.this_module_dir)
                filter = g.get('filter')
                if force_update or not dont_update:
                    OsmCache.check_osm_file_against_cache(graph_dir)
                    GtfsCache.check_feeds_against_cache(self.feeds, graph_dir, force_update, filter)
        return graphs

    def update_vlog(self, graph):
        """ print out gtfs feed(s) version numbers and dates to the otp.v log file
        """
        graph_dir = graph.get('dir', self.cache_dir)
        gtfs_msg = GtfsInfo.get_cache_msgs(graph_dir, self.feeds, graph.get('filter'))
        osm_msg = OsmInfo.get_cache_msgs(graph_dir)
        otp_utils.append_vlog_file(graph_dir, gtfs_msg + osm_msg)

    def build_graph(self, graph_dir, java_mem=None, force_update=False):
        """ will rebuild the graph...
        """
        success = True

        # step 1: set some params
        rebuild_graph = force_update

        # step 2: check graph file is fairly recent and properly sized
        graph_path = os.path.join(graph_dir, self.graph_name)
        if not file_utils.exists_and_sized(graph_path, self.graph_size):
            rebuild_graph = True

        # step 3: check the cache files
        if file_utils.dir_has_newer_files(graph_path, graph_dir, offset_minutes=60, include_filter=".jar,.json,.osm,.zip"):
            rebuild_graph = True

        # step 4: build graph is needed
        if rebuild_graph:
            success = False

            # step 4b: run the builder multiple times until we get a good looking Graph.obj
            for n in range(1, 5):
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
        """ will test a given graph against a suite of tests
        """
        success = True
        delay = 1
        if start_server:
            success = otp_utils.run_otp_server(java_mem=java_mem, graph_dir=graph['dir'], **graph)
            delay = 60
        if success:
            success = TestRunner.test_graph_factory_config(graph, suite_dir=suite_dir, delay=delay)
            if not success:
                log.warn("graph {} didn't pass it's tests".format(graph['name']))
        else:
            log.warn("was unable to run OTP server for graph {}".format(graph['name']))
        return success


    def build_and_test_graphs(self, java_mem=None, force_update=False, start_server=True, graph_filter=None):
        """ will build and test each of the graphs we have in self.graphs
        """
        ret_val = True
        if self.graphs:

            # step 1: loop thru all graph configs ... building and testing new graphs
            for g in self.graphs:

                # step 1b: if we're filtering graphs by name, only run that specific graph
                if graph_filter and g['name'] != graph_filter: continue

                # step 2: build this graph
                success, rebuilt = self.build_graph(g['dir'], java_mem, force_update)

                # step 3: test the successfully built new graph (restarting a new OTP server for the graph)
                if success and rebuilt and not g.get('skip_tests'):
                    success = self.test_graph(graph=g, java_mem=java_mem, start_server=start_server)
                    ret_val = success

                # step 3b: failed to build the graph ... send a warning
                elif not success:
                    ret_val = False
                    log.warn("graph build failed for graph {}".format(g['name']))

                # step 4: so we rebuilt the graph and any testing that was done was also a success...
                if rebuilt:

                    # step 4b: update the vlog and package the graph as new
                    if success:
                        self.update_vlog(graph=g)
                        otp_utils.package_new(graph_dir=g['dir'], graph_name=self.graph_name)

                    # step 4c: shut down any graph that
                    if g.get('post_shutdown'):
                        otp_utils.kill_otp_server(g['dir'])
        return ret_val

    def only_test_graphs(self, java_mem=None, break_on_fail=False, start_server=True, graph_filter=None):
        """ will test each of the graphs we have in self.graphs
        """
        ret_val = True
        if self.graphs:
            for g in self.graphs:
                if graph_filter and g['name'] != graph_filter: continue
                success = self.test_graph(graph=g, java_mem=java_mem, start_server=start_server)
                if not success:
                    ret_val = False
                    if break_on_fail:
                        break
        return ret_val

    @classmethod
    def build(cls):
        """ effectively the main routine for building new graphs from the command line """
        success = False

        # step 1: config the builder system
        args, parser = OtpBuilder.get_args()
        b = OtpBuilder(force_update=args.force, dont_update=args.dont_update)
        java_mem = "-Xmx1236m" if args.mem else None

        if args.mock:
            # step 2: just going to much with the vlogs, etc... as a mock build & test
            graph = otp_utils.find_graph(b.graphs, args.name)
            b.update_vlog(graph)
            success = True
        else:
            # step 3: we're going to try and build 1 or all graphs in the config

            # step 3a: are we being asked to filter only one graph to build and/or test ?
            graph_filter = None
            if args.name != "all":
                graph = otp_utils.find_graph(b.graphs, args.name)
                if graph:
                    graph_filter = args.name
                else:
                    graph_filter = "unknown graph"
                    log.warn("I don't know how to build graph '{}'".format(args.name))

            # step 3b: build and/or test one or all graphs in the config file (won't do anything with an "unknown" graph name
            if args.test:
                success = b.only_test_graphs(java_mem=java_mem, start_server=not args.dont_restart, graph_filter=graph_filter)
            else:
                success = b.build_and_test_graphs(java_mem=java_mem, force_update=args.force, start_server=not args.dont_restart, graph_filter=graph_filter)

        if args.email and (not success or args.force):
            otp_utils.send_build_test_email(args.email)

        return success

    @classmethod
    def get_args(cls):
        """ make the cli argparse for OTP graph building and testing
        """
        parser = otp_utils.get_initial_arg_parser('otp-builder')
        parser.add_argument('--test',        '-t', action='store_true', help="to just run tests vs. building the graph")
        parser.add_argument('--no_tests',    '-n', action='store_true', help="build graph w/out testing")
        parser.add_argument('--force',       '-f', action='store_true', help="force a rebuild regardless of cache state and data update")
        parser.add_argument('--dont_update', '-d', action='store_true', help="don't update data regardless of state")
        parser.add_argument('--dont_restart',      action='store_true', help="don't restart OTP when testing new graphs, etc...")
        parser.add_argument('--mock',        '-m', action='store_true', help="mock up the otp.v to make it look like the graph built and tested")
        parser.add_argument('--mem',        '-lm', action='store_true', help="should we run otp/java with smaller memory footprint?")
        parser.add_argument('--email',       '-e', help="email address(es) to be contacted if we can't build a graph, or the tests don't pass.")

        args = parser.parse_args()
        return args, parser


def main(argv=sys.argv):
    # import pdb; pdb.set_trace()
    OtpBuilder.build()


if __name__ == '__main__':
    main()
