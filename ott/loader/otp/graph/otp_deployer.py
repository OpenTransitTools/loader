from ott.utils import web_utils
from ott.utils import file_utils
from ott.utils import otp_utils
from ott.utils import object_utils

from .otp_builder import OtpBuilder

import shutil
import time
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

        def scp(self, svr, user):
            s, h = web_utils.scp_client(svr, user)
            s.put('setup.py')
            s.close()

        user = self.config.get_json('user', section='deploy')
        servers = self.config.get_json('servers', section='deploy')
        for f in servers:
            for g in self.graphs:
                dir = otp_utils.config_graph_dir(g, self.this_module_dir)
                print f, user, dir

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

