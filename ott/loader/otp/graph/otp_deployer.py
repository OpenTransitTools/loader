from ott.utils import web_utils
from ott.utils import file_utils
from ott.utils import otp_utils

from .otp_builder import OtpBuilder

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

        def scp_graph(server, user, graph_dir):
            #import pdb; pdb.set_trace()

            log_v = otp_utils.get_vlog_file_path(graph_dir)
            graph = otp_utils.get_graph_path(graph_dir)
            jar = otp_utils.get_otp_path(graph_dir)

            if file_utils.exists(log_v) and file_utils.is_min_sized(graph):
                s = None
                try:
                    log.info("scp {} over to {}@{}".format(graph, user, server))
                    s, h = web_utils.scp_client(host=server, user=user)
                    s.put(graph)
                    s.put(log_v)
                    if file_utils.is_min_sized(jar):
                        s.put(jar)
                except Exception, e:
                    log.warn(e)
                finally:
                    if s:
                        s.close()

        user = self.config.get_json('user', section='deploy')
        servers = self.config.get_json('servers', section='deploy')
        for s in servers:
            for g in self.graphs:
                dir = otp_utils.config_graph_dir(g, self.this_module_dir)
                scp_graph(server=s, user=user, graph_dir=dir)

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

