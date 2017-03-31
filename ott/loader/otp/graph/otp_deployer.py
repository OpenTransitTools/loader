from ott.utils import web_utils
from ott.utils import file_utils
from ott.utils import otp_utils

from .otp_builder import OtpBuilder

import os
import datetime
import logging
log = logging.getLogger(__file__)


class OtpDeployer(OtpBuilder):
    """ deploy OTP graphs source from the 'build' server (SVR)
    """
    def __init__(self):
        super(OtpDeployer, self).__init__(dont_update=True)
        self.graphs = otp_utils.get_graphs(self)

    def deploy_graphs(self):
        """ copy new graphs from build server to configured set of production servers
            (basically scp Graph.obj-new, otp.v-new and otp.jar-new over to another server)
        """
        ret_val = True

        def scp_graph(server, user, graph_dir, server_dir, graph=None):
            """ sub-routine to scp Graph.obj-new, otp.v-new and (optionally) otp.jar-new over to
                a given server.  crazy part of this code is all the path (string) manipulation
                in step 1 below...
            """
            global ret_val

            # step 1: create file paths to *-new files locally, and also path where we'll scp these files
            log_v_path = otp_utils.get_vlog_file_path(graph_dir)
            log_v_new = file_utils.make_new_path(log_v_path)
            log_v_svr = file_utils.append_to_path(server_dir, os.path.basename(log_v_new), False)

            graph_path = otp_utils.get_graph_path(graph_dir)
            graph_new = file_utils.make_new_path(graph_path)
            graph_svr = file_utils.append_to_path(server_dir, os.path.basename(graph_new), False)

            jar_path = otp_utils.get_otp_path(graph_dir)
            jar_new = file_utils.make_new_path(jar_path)
            jar_svr = file_utils.append_to_path(server_dir, os.path.basename(jar_new), False)

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
                except Exception, e:
                    log.warn(e)
                    ret_val = False
                finally:
                    if scp:
                        scp.close()

        # step A: grab config .ini (from app.ini) variables for the server(s) to scp OTP graphs to
        #         note, we need these server(s) to be 'known_hosts'
        user = self.config.get_json('user', section='deploy')
        servers = self.config.get_json('servers', section='deploy')
        svr_base_dir = self.config.get_json('svr_base_dir', section='deploy')

        # step B: loop thru each server, and scp a graph (and log and jar) to that server
        for s in servers:
            for g in self.graphs:
                dir = otp_utils.config_graph_dir(g, self.this_module_dir)
                svr_dir = file_utils.append_to_path(svr_base_dir, g['name'])
                scp_graph(server=s, user=user, graph_dir=dir, server_dir=svr_dir, graph=g)

        # step C: remove the -new files (so we don't keep deploying / scp-ing)
        for g in self.graphs:
            otp_utils.rm_new(graph_dir=g['dir'])

        return ret_val

    @classmethod
    def deploy(cls):
        log.info("\nRunning otp_deployer.py at {0}\n".format(datetime.datetime.now()))
        d = OtpDeployer()
        d.deploy_graphs()

    @classmethod
    def package_new(cls):
        """ convenience routine will take Graph.obj and simply copy it to Graph.obj-new
            intended to run manually if we need to export a graph by hand
        """
        log.info("\nPackage new\n".format())
        d = OtpDeployer()
        for g in d.graphs:
            # step 1: is otp.v doesn't exist, create it
            vlog_path = otp_utils.get_vlog_file_path(graph_dir=g['dir'])
            if file_utils.exists(vlog_path) is False:
                d.update_vlog(g)

            # step 2: package it...
            otp_utils.package_new(graph_dir=g['dir'])


def main():
    # import pdb; pdb.set_trace()
    OtpDeployer.deploy()

if __name__ == '__main__':
    main()

