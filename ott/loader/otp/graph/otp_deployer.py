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

        def scp(svr, user):
            s, h = web_utils.scp_client(svr, user)
            s.put('setup.py')
            s.close()

        def scp(server, user, graph_dir):
            log_v = otp_utils.get_vlog_file_path(graph_dir)
            graph = otp_utils.get_graph_path(graph_dir)
            jar = otp_utils.get_otp_path(graph_dir)

            if file_utils.exists(log_v) and file_utils.is_min_sized(graph):
                print server, user, graph, log_v
                if file_utils.is_min_sized(jar):
                    print server, user, jar

        user = self.config.get_json('user', section='deploy')
        servers = self.config.get_json('servers', section='deploy')
        for s in servers:
            for g in self.graphs:
                dir = otp_utils.config_graph_dir(g, self.this_module_dir)
                scp(server=s, user=user, graph_dir=dir)

        return ret_val

    @classmethod
    def deploy(cls):
        log.info("\nRunning otp_deployer.py on {0}\n".format(datetime.datetime.now()))
        d = OtpDeployer()
        d.deploy_graphs()

def main():
    OtpDeployer.deploy()

if __name__ == '__main__':
    main()

