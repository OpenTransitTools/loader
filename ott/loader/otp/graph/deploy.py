import filecmp
import shutil

from ott.utils import exe_utils
from ott.utils import web_utils
from ott.loader.otp.graph.build import *

# constants
SVR = "http://maps10.trimet.org/"
TMP_DIR  = "/tmp/"
API_NAME = "opentripplanner-api-webapp.war"
JAR_NAME = "graph-builder.jar"
API_FILE = OTP_DIR + "webapps/" + API_NAME
JAR_FILE = OTP_DIR + "lib/"     + JAR_NAME

URL_GRAPH = SVR + GRAPH_NAME
URL_API   = SVR + API_NAME
URL_JAR   = SVR + JAR_NAME

TMP_VERSION_LOG = TMP_DIR + VLOG_NAME
TMP_GRAPH = TMP_DIR + GRAPH_NAME
TMP_API   = TMP_DIR + API_NAME
TMP_JAR   = TMP_DIR + JAR_NAME


def bkup_file(file):
    """ copy a file to a file--YYYY-MM-DD
    """
    try:
        if os.path.isfile(file):
            today = datetime.datetime.now().strftime("%Y-%m-%d")
            shutil.copy2(file, file + "--" + today)
    except:
        logging.warn('ERROR: could not copy file ' + file)


def diff_vlog(svr, vlog="otp.v"):
    """ return True if the files are different and need to be redeployed ...
    
        - grab vlog from remote server that builds new OTP graphs
        - compare it to our local vlog
        - send email if we can't find remote vlog...
    """
    ret_val = False
    
    # step 1: grab otp.v from build server
    url=svr + vlog
    ok = web_utils.wget(url, TMP_VERSION_LOG, 10)

    if not ok:
        # step 2: remote server doesn't have otp.v exposed ... send an error email...
        msg = "No vlog available at {0}".format(url)
        email(msg, msg)
        ret_val = False
    else:
        # step 3: make sure the otp.v we just downloaded has content ... if note, send an error email
        if not exists_and_sized(TMP_VERSION_LOG, 20):
            msg = "vlog file {0} (grabbed from {1}) isn't right ".format(TMP_VERSION_LOG, url)
            email(msg, msg)
            ret_val = False
        else:
            # step 4a: we currently don't have a vlog, so assume we don't have an existing OTP ... let's deploy new download...
            if not exists_and_sized(VERSION_LOG, 20):
                ret_val = True
                logging.info("{0} doesn't exist ... try to grab new OTP from {1} and deploy".format(VERSION_LOG, SVR))
            else:
                # step 4b: check if the vlog files are different...if so, we'll assume the remote is newer and start a new deploy...                
                if filecmp.cmp(TMP_VERSION_LOG, VERSION_LOG):
                    logging.info("{0} == {1} ... we're done, going to keep the current graph running".format(VERSION_LOG, TMP_VERSION_LOG))
                else:
                    ret_val = True
                    logging.info("{0} != {1} ... will try to grab new OTP from {2} and deploy".format(VERSION_LOG, TMP_VERSION_LOG, SVR))

    return ret_val


def update_graph():
    """ update the graph,  and other 
    """

    # step 1: see if our vlog is different (older) than the one from the build server
    if diff_vlog(SVR):

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
            bkup_file(GRAPH_FILE)
            bkup_file(API_FILE)
            bkup_file(VERSION_LOG)
            bkup_file(JAR_FILE)

            # step 3c: move the new stuff into place
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
    logging.basicConfig(level=logging.INFO)
    logging.info("\nRunning deploy.py on {0}\n".format(datetime.datetime.now()))
    update_graph()

if __name__ == '__main__':
    main()
