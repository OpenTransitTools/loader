import os
import sys
import time
import inspect
import logging
log = logging.getLogger(__file__)

from mako.template import Template

from ott.utils.config_util import ConfigUtil
from ott.utils import web_utils
from ott.utils import file_utils

from ott.loader.otp.preflight.test_suite import ListTestSuites


class TestRunner(object):
    """ Run .csv tests from ./tests/ by constructing a
        url to the trip planner, calling the url, then printing a report
    """
    this_module_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

    def __init__(self, port=8001, suite_dir=None, report_mako_path=None, date=None):
        """constructor builds the test runner
        """

        # step 1: build OTP ws and map urls from config
        self.config = ConfigUtil(section='otp')
        host = self.config.get('host', def_val=web_utils.get_hostname())

        ws = self.config.get('ws_url_path', def_val="/otp/routers/default/plan")
        self.ws_url = "http://{}:{}{}".format(host, port, ws)

        map = self.config.get('map_url_path', def_val="")
        self.map_url = "http://{}:{}{}".format(host, port, map)

        # step 2: set file and directory paths (suites dir contains .csv files defining tests)
        if suite_dir is None:
            suite_dir = os.path.join(self.this_module_dir, "suites")
        self.report_mako_path = report_mako_path
        if report_mako_path is None:
            self.report_mako_path = os.path.join(self.this_module_dir, 'templates', 'good_bad.html')

        # step 3: create mako template, and list of test suites
        self.report_template = Template(filename=self.report_mako_path)
        self.test_suites = ListTestSuites(ws_url=self.ws_url, map_url=self.map_url, suite_dir=suite_dir, date=date)

    def report(self, dir=None, report_name='otp_report.html'):
        """ render a test pass/fail report with mako
        """
        ret_val = None
        try:
            # step 1: mako render of the report
            #import pdb; pdb.set_trace()
            suites = self.test_suites.get_suites()

            r = self.report_template.render(test_suites=suites, test_errors=self.test_suites.has_errors())
            ret_val = r

            # step 2: stream the report to a file
            report_path = report_name
            if dir:
                report_path = os.path.join(dir, report_name)
            file_utils.mv(report_path, report_path + "-old")
            f = open(report_path, 'w')
            if r:
                f.write(r)
            else:
                f.write("Sorry, the template was null...")
            f.flush()
            f.close()
        except NameError, e:
            log.warn("This ERROR probably means your template has a variable not being sent down with render: {}".format(e))
        except Exception, e:
            log.warn(e)
        return ret_val

    def send_email(self):
        """ send email
        """
        try:
            t = time.strftime('%B %d, %Y (%A) %I:%M%p').lower().replace(" 0", " ")
            m = ""
            p = "PASSED"
            if self.test_suites.has_errors():
                p = "FAILED"
                m = self.test_suites.list_errors()
            msg = "OTP tests {} on {}\n{}\n".format(p, t, m)
            recipients = ConfigUtil(section='contact').get('emails')
            web_utils.simple_email(msg, recipients)
        except Exception, e:
            log.warn(e)

    @classmethod
    def test_graph_factory(cls, graph_dir, suite_dir, port=None, delay=1):
        ''' run graph tests against whatever server is running
        '''
        #import pdb; pdb.set_trace()
        #suite_dir = "/java/DEV/loader/ott/loader/otp/tests/suites"
        ret_val = False
        log.info('GRAPH TESTS: Starting tests!')
        time.sleep(delay)
        t = TestRunner(port=port, suite_dir=suite_dir)
        t.test_suites.run()
        t.report(graph_dir)
        if t.test_suites.has_errors():
            log.info('GRAPH TESTS: There were errors!')
            t.send_email()
            ret_val = False
        else:
            log.info('GRAPH TESTS: Nope, no errors...')
            ret_val = True
        return ret_val


def email():
    t = TestRunner()
    import pdb; pdb.set_trace()
    t.send_email()

def stress(argv):
    date = None
    if len(argv) > 2:
        date = argv[1]

    test_suites = TestRunner.get_test_suites(date)
    for ts in test_suites:
        ts.printer()

def main(argv=sys.argv):
    #import pdb; pdb.set_trace()
    dir = None
    if 'DEBUG' in argv:
        log.basicConfig(level=log.DEBUG)
        dir = os.path.join(TestRunner.this_module_dir, "..", "tests", "suites")

    if 'STRESS' in argv:
        stress(argv)
    else:
        TestRunner.test_graph_factory(suite_dir=dir)

if __name__ == '__main__':
    #email()
    main()
