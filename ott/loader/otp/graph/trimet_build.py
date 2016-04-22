from ott.loader.otp.graph.build import Build


class TriMetBuild(Build):
    """ build an OTP graph
    """
    @classmethod
    def factory(cls):
        return TriMetBuild()

    def deploy_graph(self):
        print "YO YO YO"

def main(argv):
    TriMetBuild.options(argv)

if __name__ == '__main__':
    main(sys.argv)


def build_graph(new_gtfs=True):
    """ build a new graph
        return True if the build encouters errors
    """
    ret_val = False

    exists = exists_and_sized(GRAPH_FILE, GRAPH_SIZE)
    if new_gtfs or not exists:
        for n in range(1, 21):
            if not ret_val:
                logging.info(" build attempt {0} of a new graph ".format(n))
                os.system("rm -f " + GRAPH_FILE)
                os.chdir(OTP_DIR)
                os.system("{0}/jdk/bin/java -Xmx4096m -jar lib/graph-builder.jar graph/graph-builder.xml".format(HOME_DIR))
                time.sleep(10)
                ret_val = exists_and_sized(GRAPH_FILE, GRAPH_SIZE)

    return ret_val


def deploy_graph(start_tomcat="ant test", sleep=60):
    """ deploy the new graph
        return True if the deployment encouters errors
    """
    exists = exists_and_sized(GRAPH_FILE, GRAPH_SIZE)
    if exists:
        logging.info(' deploying the graph ')
        os.chdir(CLUSTER_DIR)
        os.system("pkill -9 java")
        os.system("pkill -9 balance")
        time.sleep(10)
        os.system(start_tomcat)
        time.sleep(sleep)
    return exists

def deploy_and_test_graph(version=None, date_range=None):
    new_deploy = deploy_graph()
    if new_deploy:
        graph_passed_tests = test_graph()
        if not graph_passed_tests:
            graph_passed_tests = test_graph() # 2nd chance, just in case OTP wasn't ready the first time thru
        if version and date_range:
            if graph_passed_tests:
                update_vlog(version, date_range)
            else:
                f="mv {0} {1}".format(GRAPH_FILE, GRAPH_FAILD)
                logging.info(' tests failed with gtfs version {0}- parking the graph (e.g., {1})'.format(version, f))
                os.system(f)
        else:
            print "tests passed ? {0}".format(graph_passed_tests)

def email(msg, subject="Graph builder info...", mailfrom="build.py"):
    """ send an email to someone...
    """

    sender = 'purcellf@trimet.org'
    receivers = [sender]
    message = """ <purcellf@trimet.org>
To:  <mapfeedback@trimet.org>
Subject: {0}

""".format(subject)
    try:
        smtp_obj = smtplib.SMTP('localhost')
        smtp_obj.sendmail(sender, receivers, "From: " + mailfrom + message + msg)
        logging.info('MAIL: From: ' + mailfrom + message + msg)
    except:
        traceback.print_exc(file=sys.stdout)
        logging.warn('ERROR: could not send email')
