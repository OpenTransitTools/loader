from ott.utils import web_utils
from ott.utils import file_utils
from ott.utils import otp_utils
from ott.utils import object_utils

from .otp_builder import OtpBuilder

import shutil
import datetime
import logging
log = logging.getLogger(__file__)

JAR_NAME = "otp.jar"


class OtpDeployer(OtpBuilder):
    """ deploy OTP graphs source from the 'build' server (SVR)
    """
    force_update = False
    def __init__(self):
        super(OtpDeployer, self).__init__(dont_update=True)
        self.graphs = otp_utils.get_graphs(self)

    def update_new_otp(self):
        gok = web_utils.wget(URL_GRAPH, TMP_GRAPH, 1000000)
        aok = web_utils.wget(URL_API,   TMP_API,   1000000)
        return gok and aok

    def restart_new_otp(self):
        pass

    def update_old_otp(self):
        gok = web_utils.wget(URL_GRAPH, TMP_GRAPH, 1000000)
        aok = web_utils.wget(URL_API,   TMP_API,   1000000)
        jok = web_utils.wget(URL_JAR,   TMP_JAR,   1000000)
        return gok and aok

    def restart_old_otp(self):
        # step 3a: shut down the servers
        os.system("pkill -9 java")
        os.system("pkill -9 balance")
        time.sleep(10)

        # step 3b: backup the old stuff
        file_utils.bkup(GRAPH_FILE)
        file_utils.bkup(API_FILE)
        file_utils.bkup(VERSION_LOG)
        file_utils.bkup(JAR_FILE)

        # step 3c: moved the new stuff into place
        shutil.copy2(TMP_GRAPH, GRAPH_FILE)
        shutil.copy2(TMP_API,   API_FILE)
        shutil.copy2(TMP_JAR,   JAR_FILE)
        shutil.copy2(TMP_VERSION_LOG, VERSION_LOG)
        shutil.copy2(VERSION_LOG, HTDOCS_VLOG)

        # step 3d: if this is server looks like it's running the call center app, restart that
        if os.path.isfile("call_center/db/call_db.tar.gz"):
            subprocess.call(['call_center/run.sh'])

        # step 3e: restart the OTP server...
        # NOTE: 'ant' will start all 4 tomcat instances (large memory production servers),
        #       'ant test' only starts a single tomcat instance
        tomcat_cmd="ant"
        if sys_memory() < 20:
            tomcat_cmd="ant test"
        deploy_graph(tomcat_cmd)

    def update_graphs(self, build_svr, force_update=False):
        """ update the graph,  and other
        """
        ret_val = True
        for g in self.graphs:
            do_update = force_update

            # step 1: determine via the otp.v log if 'build' server has new otp.jar file
            if force_update is False:
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
        force_update = object_utils.is_force_update()
        d = OtpDeployer()
        d.update_graphs(force_update)

def main():
    OtpDeployer.deploy()

if __name__ == '__main__':
    main()
