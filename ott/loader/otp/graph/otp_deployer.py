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

    def update_graphs(self):
        """ update the graph, and other
        """
        ret_val = True
        for g in self.graphs:
            do_update = object_utils.is_force_update()

            # step 1: determine via the otp.v log if 'build' server has new otp.jar file
            if do_update is False:
                do_update = otp_utils.diff_vlog(build_svr, g['dir'])

            # step 2: grab new graph and api
            if do_update:
                if self.is_old_otp(g):
                    continue_update = self.update_new_otp()
                else:
                    continue_update = self.update_new_otp()

                # step 3: deploy new binaries
                if continue_update:
                    pass

        return ret_val

    @classmethod
    def deploy(cls):
        log.info("\nRunning otp_deployer.py on {0}\n".format(datetime.datetime.now()))
        d = OtpDeployer()
        d.update_graphs()

    @classmethod
    def scp(cls):
        s,h = web_utils.scp_client('maps7', 'otp')
        s.put('setup.py')
        s.get('test.txt')
        s.close()

def main():
    OtpDeployer.deploy()

if __name__ == '__main__':
    main()

