""" Run build.py weekly (or daily) on the test maps servers (e.g., maps6 / maps10).  I will
    download the latest gtfs.zip file, check to see if it's newer than the last version
    I downloaded, and if so, build a new OTP Graph.

    @see deploy.py, which is a companion script that runs on the production servers, and
    deploys a new OTP graph into production.
"""

import os
import inspect
import sys
import copy
import time
import traceback
import logging
import smtplib
import subprocess
import datetime

from ott.loader.gtfs.cache import Cache
from ott.loader.gtfs.info  import Info
from ott.loader.gtfs import utils as file_utils

# constants
GRAPH_NAME = "Graph.obj"
GRAPH_FAILD = GRAPH_NAME + "-failed-tests"
GRAPH_SIZE = 500000000
VLOG_NAME  = "otp.v"
TEST_HTML  = "otp_report.html"

class Build():
    """ build an OTP graph
    """
    graph_path = None
    build_cache_dir = None
    gtfs_zip_files = None

    graph_name = GRAPH_NAME
    graph_failed = GRAPH_FAILD
    graph_size = GRAPH_SIZE
    vlog_name  = VLOG_NAME
    test_html  = TEST_HTML
    graph_expire_days = 45

    def __init__(self, config=None, gtfs_zip_files=Cache.get_gtfs_feeds()):
        self.gtfs_zip_files = gtfs_zip_files
        self.build_cache_dir = self.get_build_cache_dir()
        self.graph_path = os.path.join(self.build_cache_dir, self.graph_name)

    def build_graph(self, force_rebuild=False):
        # step 1: set some params
        rebuild_graph = force_rebuild

        # step 2: check graph file is fairly recent and properly sized
        if not file_utils.exists_and_sized(self.graph_path, self.graph_size, self.graph_expire_days):
            rebuild_graph = True

        # step 3: check the cache files
        if self.check_gtfs_cache_files():
            rebuild_graph = True

        # step 4: print feed info
        feed_details = self.get_gtfs_feed_details()

        # step 5: build graph is needed
        if rebuild_graph:
            logging.info("rebuilding the graph")

    def check_gtfs_cache_files(self):
        ''' returns True if any gtfs files in the cache are out of date
        '''
        ret_val = False
        for g in self.gtfs_zip_files:
            # step 2a: check the cached feed for any updates
            url, name = Cache.get_url_filename(g)
            diff = Cache.cmp_file_to_cached(name, self.build_cache_dir)
            if diff.is_different():
                Cache.cp_cached_gtfs_zip(name, self.build_cache_dir)
                ret_val = True
        return ret_val

    def get_gtfs_feed_details(self):
        ''' returns updated [] with feed details
        '''
        ret_val = []
        for g in self.gtfs_zip_files:
            cp = copy.copy(g)
            gtfs_path = os.path.join(self.build_cache_dir, cp['name'])
            info = Info(gtfs_path)
            r = info.get_feed_date_range()
            v = info.get_feed_version()
            d = info.get_days_since_stats()
            cp['start'] = r[0]
            cp['end'] = r[1]
            cp['version'] = v
            cp['since'] = d[0]
            cp['until'] = d[1]
            ret_val.append(cp)
        return ret_val

    def run_graph_tests(self):
        ''' returns updated [] with feed details
        '''


    def mv_failed_graph_to_good(self):
        """ move the failed graph to prod graph name if prod graph doesn't exist and failed does exist
        """
        exists = os.path.exists(self.graph_path)
        if not exists:
            fail_path = os.path.join(self.build_cache_dir, self.graph_failed)
            exists = os.path.exists(fail_path)
            if exists:
                file_utils.mv(fail_path, self.graph_path)

    def update_vlog(self, feeds_details):
        """ print out gtfs feed(s) version numbers and dates to the otp.v log file
        """
        if feeds_details and len(feeds_details) > 0:
            msg = "\nUpdated graph on {} with GTFS feed(s):\n".format(datetime.datetime.now().strftime("%B %d, %Y @ %I:%M %p"))
            for f in feeds_details:
                msg += "  {} - date range {} to {} ({:>3} more calendar days), version {}\n".format(f['name'], f['start'], f['end'], f['until'], f['version'])
            vlog = os.path.join(self.build_cache_dir, self.vlog_name)
            f = open(vlog, 'a')
            f.write(msg)
            f.flush()
            f.close()

    @classmethod
    def get_build_cache_dir(cls, dir=None, def_name="cache"):
        ''' returns either dir (stupid check) or <current-directory>/$def_name
        '''
        ret_val = dir
        if dir is None:
            this_module_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
            ret_val = os.path.join(this_module_dir, def_name)
        file_utils.mkdir(ret_val)
        return ret_val

def main(argv):
    b = Build()
    if "mock" in argv:
        feed_details = b.get_gtfs_feed_details()
        b.update_vlog(feed_details)
        b.mv_failed_graph_to_good()
    elif "tests" in argv:
        b.run_graph_tests()
    else:
        b.build_graph()

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
