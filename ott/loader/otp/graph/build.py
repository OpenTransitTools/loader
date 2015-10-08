""" Run build.py weekly (or daily) on the test maps servers (e.g., maps6 / maps10).  I will
    download the latest gtfs.zip file, check to see if it's newer than the last version
    I downloaded, and if so, build a new OTP Graph.

    @see deploy.py, which is a companion script that runs on the production servers, and
    deploys a new OTP graph into production.
"""

import os
import sys
import time
import traceback
import logging
import smtplib
import subprocess
import datetime

# constants
GRAPH_NAME = "Graph.obj"
GRAPH_SIZE = 500000000
VLOG_NAME  = "otp.v"
TEST_HTML  = "otp_report.html"
HOME_DIR    = "/home/otp/"
HTDOCS_DIR  = HOME_DIR + "htdocs/"
HTDOCS_VLOG = HTDOCS_DIR + VLOG_NAME
DEPLOY_DIR  = HOME_DIR + "OtpDeployer/"
OTP_DIR     = DEPLOY_DIR + "otp/"
GRAPH_DIR   = OTP_DIR   + "graph/"
CLUSTER_DIR = OTP_DIR   + "cluster/"
GRAPH_FILE  = GRAPH_DIR + GRAPH_NAME
GRAPH_FAILD = GRAPH_DIR + GRAPH_NAME + "-failed-tests"
VERSION_LOG = GRAPH_DIR + VLOG_NAME
TEST_REPORT = GRAPH_DIR + TEST_HTML



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


def sys_memory(op="-g"):
    """ linux memory check...how much RAM do we have, defaults to gigs of RAM
    """
    ret_val = -111
    try:
        ret_val = int(os.popen("free " + op).readlines()[1].split()[1])
    except:
        ret_val = -111
    return ret_val


def check_gtfs(cmp):
    """ grab gtfs data, and see if its got new data (trigger for buiding a new graph)
        return True if we update the GTFS, and thus the graph needs to be updated
    """
    ret_val = False

    cmp.mk_tmp_dir()
    cmp.cd_tmp_dir()
    cmp.download_gtfs()
    old_cal, new_cal, old_info, new_info = cmp.unzip_calendar_and_info_files()
    sdays, edays = cmp.gtfs_calendar_age(new_cal)
    feed_version = cmp.get_new_feed_version()
    feed_dates   = cmp.get_new_feed_dates()
    is_same_gtfs = cmp.cmp_files(old_info, new_info)

    # warn about old GTFS data
    if sdays > 60 or edays < 30:
       msg = "{0} calendar started {1} days ago, and has {2} days remaining till expiration\nFeed Version: {3}, dates {4}".format(cmp.gtfs_url, sdays, edays, feed_version, feed_dates)
       logging.info(msg)
       email(msg, "GTFS data warning...is the data up-to-date?")

    if is_same_gtfs:
        logging.info('GTFS data is the same version: {0}'.format(feed_version))
    else:
        logging.info('gtfs files are different ... assume new download (version {0}; dates {1}) has newest schedule data, thus update gtfs cache...'.format(feed_version, feed_dates))
        cmp.update_gtfs()
        ret_val = True
    return ret_val, feed_version, feed_dates


def exists_and_sized(file, size=0):
    """ check whether the a file exists and is has some girth
    """
    exists = os.path.exists(file)
    if not exists:
        logging.info(" file {0} doesn't exist ".format(file))
    else:
        s = os.stat(file)
        if s.st_size < size:
            logging.info(" file {0} appears (at {1} bytes) is less than specified {2} bytes".format(file, s.st_size, size))
            exists = False
    return exists

def update_vlog(version, date_range):
    """ run tests on a graph
        return True if the tests cause any errors
    """
    u = "\nUpdated graph on {0} with GTFS version #{1}, date range: {2}\n".format(datetime.datetime.now(), version, date_range)
    f = open(VERSION_LOG, 'a')
    f.write(u)
    f.flush()
    f.close()

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

def mv_failed_graph_to_good():
    """ move the failed graph to prod graph name if prod graph doesn't exist and failed does exist
    """
    exists = os.path.exists(GRAPH_FILE)
    if not exists:
        exists = os.path.exists(GRAPH_FAILD)
        if exists:
            f="mv {0} {1}".format(GRAPH_FAILD, GRAPH_FILE)
            os.system(f)

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


def test_graph():
    """ run tests on a graph
        return True if the graph looks good and the tests didn't cause any errors
    """
    ret_val = True
    
    # step 1: run tests
    os.chdir(DEPLOY_DIR)
    template = DEPLOY_DIR + 'otpdeployer/templates/good_bad.html'
    t = TestRunner(template)
    t.run()

    # step 2: write a report
    f = open(TEST_REPORT, 'w')
    r = t.report()
    f.write(r)
    f.flush()
    f.close()

    # step 3: set return error status & send email when we see test errors
    if t.has_errors():
        ret_val = False
        msg = "Tests and graph logs: "
        for i in [6,10]:
            svr = "http://maps{0}.trimet.org".format(i)
            msg += "\n\n\t{0}/{1} \n\t{0}/otp.v".format(svr, TEST_HTML)
        email(msg, "OTP test errors")

    return ret_val

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

def real_build():
    logging.basicConfig(level=logging.INFO)
    logging.info("\nRunning build.py on {0}\n".format(datetime.datetime.now()))

    tests_failed = False
    new_gtfs = new_graph = True
    cmp = CompareTwoGtfsZipFiles()
    new_gtfs, version, date_range = check_gtfs(cmp)
    logging.info("\nIs new GTFS == {0}? Version #{1}.  Date range {2}\n".format(new_gtfs, version, date_range))
    new_graph = build_graph(new_gtfs)
    if new_graph:
        deploy_and_test_graph(version, date_range)

def mock_build(test=False):
    cmp = CompareTwoGtfsZipFiles()
    junk, version, date_range = check_gtfs(cmp)
    print version, date_range
    if test:
        deploy_and_test_graph(version, date_range)
    else:
        deploy_graph()
        update_vlog(version, date_range)

def xmain(argv):
    if "mock" in argv:
        mock_build("test" in argv)
        mv_failed_graph_to_good()
    else:
        real_build()

def main(argv):
    print "hi"

if __name__ == '__main__':
    main(sys.argv)
