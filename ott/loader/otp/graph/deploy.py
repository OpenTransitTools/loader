import shutil
import logging
log = logging.getLogger(__file__)

from ott.utils import web_utils
from ott.utils import file_utils
from ott.utils import otp_utils
from ott.loader.otp.graph.build import *

from .build import Build

# constants
SVR = "http://maps7.trimet.org/"
TMP_DIR  = "/tmp/"
JAR_NAME = "graph-builder.jar"

class Deploy(Build):
    """ deploy OTP graphs source from the 'build' server (SVR)
    """
    force_update = False
    def __init__(self, force_update=False):
        super(Deploy, self).__init__(dont_update=True)
        self.force_update = force_update

    def update_graph(self):
        """ update the graph,  and other
        """

        # step 1: see if our vlog is different (older) than the one from the build server
        if otp_utils.diff_vlog(SVR):

            # step 2: grab new graph and api
            gok = web_utils.wget(URL_GRAPH, TMP_GRAPH, 1000000)
            aok = web_utils.wget(URL_API,   TMP_API,   1000000)
            jok = web_utils.wget(URL_JAR,   TMP_JAR,   1000000)

            # step 3: deploy new binaries
            if gok and aok:
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


def main():
    log.info("\nRunning deploy.py on {0}\n".format(datetime.datetime.now()))
    update_graph()

if __name__ == '__main__':
    main()
