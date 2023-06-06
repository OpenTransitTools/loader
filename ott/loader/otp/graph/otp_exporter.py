from ott.utils import web_utils
from ott.utils import file_utils
from ott.utils import otp_utils
from ott.utils import object_utils

from ott.utils.parse.cmdline import otp_cmdline

from .otp_builder import OtpBuilder

import os
import datetime
import logging
log = logging.getLogger(__file__)


class OtpExporter(OtpBuilder):
    """ deploy OTP graphs source from the 'build' server (SVR)
    """
    def __init__(self):
        super(OtpExporter, self).__init__(dont_update=True)
        self.graphs = otp_utils.get_graphs(self)

    def export_graphs(self, server_filter=None, graph_filter=None):
        """ copy new graphs from build server to configured set of production servers
            (basically scp Graph.obj-new, otp.v-new and otp.jar-new over to another server)
        """
        ret_val = True

        if self.graphs is None or len(self.graphs) < 1:
            log.info("no [otp] graphs configured in the .ini file")
            return ret_val

        # step A: grab config .ini (from app.ini) variables for the server(s) to scp OTP graphs to
        #         note, we need these server(s) to be 'known_hosts'
        user = self.config.get_json('user', section='deploy')
        servers = self.config.get_json('servers', section='deploy')
        otp_base_dir = self.config.get_json('otp_base_dir', section='deploy')

        def scp_graph(server, graph):
            """ sub-routine to scp Graph.obj-new, otp.v-new and (optionally) otp.jar-new over to
                a given server.  crazy part of this code is all the path (string) manipulation
                in step 1 below...
            """
            global ret_val

            graph_dir = otp_utils.config_graph_dir(graph, self.this_module_dir)
            server_dir = file_utils.append_to_path(otp_base_dir, graph.get('name'))

            # step 1: create file paths to *-new files locally, and also path where we'll scp these files
            log_v_path = otp_utils.get_vlog_file_path(graph_dir)
            log_v_new = file_utils.make_new_path(log_v_path)
            log_v_svr = file_utils.append_to_path(server_dir, os.path.basename(log_v_new), False)

            graph_path = otp_utils.get_graph_path(graph_dir, otp_version=graph.get('version'))
            graph_new = file_utils.make_new_path(graph_path)
            graph_svr = file_utils.append_to_path(server_dir, os.path.basename(graph_new), False)

            jar_path = otp_utils.get_otp_path(graph_dir)
            jar_new = file_utils.make_new_path(jar_path)
            jar_svr = file_utils.append_to_path(server_dir, os.path.basename(jar_new), False)

            # step 1b: these are the other OTP artifacts, like OSM, GTFS and JSON (config) files
            osm_paths = otp_utils.get_osm_paths(graph_dir)
            gtfs_paths = otp_utils.get_gtfs_paths(graph_dir)
            config_paths = otp_utils.get_config_paths(graph_dir)

            # step 2: we are going to attempt to scp Graph.obj-new over to the server(s)
            #         note: the server paths (e.g., graph_svr, etc...) are relative to the user's home account
            if file_utils.is_min_sized(graph_new):
                scp = None
                try:
                    log.info("scp {} over to {}@{}:{}".format(graph_new, user, server, graph_svr))
                    scp, ssh = web_utils.scp_client(host=server, user=user)
                    scp.put(graph_new, graph_svr)
                    scp.put(log_v_new, log_v_svr)
                    if file_utils.is_min_sized(jar_new):
                        scp.put(jar_new, jar_svr)
                    for p in osm_paths:
                        scp.put(p, server_dir)
                    for p in gtfs_paths:
                        scp.put(p, server_dir)
                    for p in config_paths:
                        scp.put(p, server_dir)
                except Exception as e:
                    log.warning(e)
                    ret_val = False
                finally:
                    if scp:
                        scp.close()

        # step B: loop thru each server, and scp a graph (and log and jar) to that server
        # import pdb; pdb.set_trace()
        for s in servers:
            if object_utils.is_not_match(server_filter, s):
                continue
            for g in self.graphs:
                if object_utils.is_not_match(graph_filter, g.get('name')):
                    continue
                scp_graph(server=s, graph=g)

        # step C: remove the -new files (so we don't keep deploying / scp-ing)
        for g in self.graphs:
            if object_utils.is_not_match(graph_filter, g.get('name')):
                continue
            otp_utils.rm_new(graph_dir=g.get('dir'), otp_version=g.get('version'))

        return ret_val

    @classmethod
    def export(cls):
        parser = cls.get_args()
        otp_cmdline.server_option(parser)
        args = parser.parse_args()

        log.info("\nRunning otp_exporter.py at {0}\n".format(datetime.datetime.now()))
        d = OtpExporter()
        d.export_graphs(server_filter=args.server, graph_filter=args.name)

    @classmethod
    def package_new(cls):
        """ convenience routine will take Graph.obj and simply copy it to Graph.obj-new
            intended to run manually if we need to export a graph by hand
        """
        args = cls.get_args('bin/otp_package_new', True)
        graph_filter = args.name

        log.info("\nPackage new\n".format())
        d = OtpExporter()
        for g in d.graphs:
            # step 0: do we filter this graph?
            if object_utils.is_not_match(graph_filter, g['name']):
                continue

            dir = g.get('dir', './')
            version = g.get('version', otp_utils.OTP_VERSION)

            # step 1: is otp.v doesn't exist or is a bit old, create it
            vlog_path = otp_utils.get_vlog_file_path(graph_dir=dir)
            if file_utils.exists(vlog_path) is False or file_utils.file_age(vlog_path) > 1:
                d.update_vlog(g)

            # step 2: package it...
            otp_utils.package_new(graph_dir=dir, otp_version=version)

    @classmethod
    def otp_v_new(cls):
        """ update otp.v """
        args = cls.get_args('bin/otp_v_new', True)
        graph_filter = args.name

        log.info("\nCreate new otp.v\n".format())
        d = OtpExporter()
        for g in d.graphs:
            if object_utils.is_not_match(graph_filter, g.get('name')):
                continue
            d.update_vlog(g)

    @classmethod
    def get_args(cls, prog_name='bin/otp-exporter', make_args=False):
        """
        make the cli argparse for OTP graph exporting
        """
        parser = otp_cmdline.base_parser(prog_name)
        ret_val = parser
        if make_args:
            ret_val = parser.parse_args()
        return ret_val


def main():
    # import pdb; pdb.set_trace()
    OtpExporter.export()


if __name__ == '__main__':
    main()

