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
        """ update the graph, and other
        """
        ret_val = True

        def scp_graph(server, user, graph_dir, server_dir):

            # step 1: create file paths to *-new files locally, and also path where we'll scp these files
            log_v_path = otp_utils.get_vlog_file_path(graph_dir)
            log_v_new = file_utils.make_new_path(log_v_path)
            log_v_svr = file_utils.append_to_path(server_dir, os.path.basename(log_v_new), False)

            graph_path = otp_utils.get_graph_path(graph_dir)
            graph_new = file_utils.make_new_path(graph_path)

            jar_path = otp_utils.get_otp_path(graph_dir)
            jar_new = file_utils.make_new_path(jar_path)

            if file_utils.exists(log_v_new):
                scp, ssh = web_utils.scp_client(host=server, user=user)
                scp.put(log_v_new, log_v_svr)
                return

            if file_utils.exists(log_v_new) and file_utils.is_min_sized(graph_new):
                scp = None
                try:
                    log.info("scp {} over to {}@{}:{}".format(graph_new, user, server, graph_svr))
                    scp, ssh = web_utils.scp_client(host=server, user=user)
                    scp.put(graph)
                    scp.put(log_v)
                    if file_utils.is_min_sized(jar_new):
                        scp.put(jar)
                except Exception, e:
                    log.warn(e)
                finally:
                    if scp:
                        scp.close()

        # import pdb; pdb.set_trace()
        user = self.config.get_json('user', section='deploy')
        servers = self.config.get_json('servers', section='deploy')
        svr_base_dir = self.config.get_json('svr_base_dir', section='deploy')
        for s in servers:
            for g in self.graphs:
                dir = otp_utils.config_graph_dir(g, self.this_module_dir)
                svr_dir = file_utils.append_to_path(svr_base_dir, g['name'])
                scp_graph(server=s, user=user, graph_dir=dir, server_dir=svr_dir)

        return ret_val

    @classmethod
    def deploy(cls):
        log.info("\nRunning otp_deployer.py on {0}\n".format(datetime.datetime.now()))
        d = OtpDeployer()
        d.deploy_graphs()

    @classmethod
    def package_new(cls):
        log.info("\nPackage new\n".format())
        d = OtpDeployer()
        for g in d.graphs:
            otp_utils.package_new(dir=g['dir'])


def main():
    OtpDeployer.deploy()

if __name__ == '__main__':
    main()

