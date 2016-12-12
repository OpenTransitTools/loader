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
from ott.utils import otp_utils

from ott.loader.otp.preflight.test_suite import ListTestSuites

def get_args_parser():
    parser = otp_utils.get_initial_arg_parser()
    parser.add_argument('--hostname', '-hn',  help="specify the hostname for the test url")
    parser.add_argument('--port',     '-p',   help="port")
    parser.add_argument('--ws_path',  '-ws',  help="OTP url path, ala 'prod' or '/otp/routers/default/plan'")
    parser.add_argument('--debug',    '-d',   help="run DEBUG suites", action='store_true')
    return parser

class TestRunner(object):
    """ Run .csv tests from ./tests/ by constructing a
        url to the trip planner, calling the url, then printing a report
    """
    this_module_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

    def __init__(self, hostname=None, port=None, suite_dir=None, report_mako_path=None, date=None, filter=None):
        """constructor builds the test runner
        """
        # step 1: build OTP ws and map urls from config
        self.ws_url, self.map_url = otp_utils.get_test_urls_from_config(hostname=hostname, port=port)

        # step 2: set file and directory paths (suites dir contains .csv files defining tests)
        if suite_dir is None:
            suite_dir = os.path.join(self.this_module_dir, "suites")
        self.report_mako_path = report_mako_path
        if report_mako_path is None:
            self.report_mako_path = os.path.join(self.this_module_dir, 'templates', 'good_bad.html')

        # step 3: create mako template, and list of test suites
        self.report_template = Template(filename=self.report_mako_path)
        self.test_suites = ListTestSuites(ws_url=self.ws_url, map_url=self.map_url, suite_dir=suite_dir, date=date, filter=filter)

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
    def test_graph_factory(cls, graph_dir, suite_dir, hostname=None, port=None, delay=1, filter=None):
        ''' run graph tests against whatever server is running
        '''
        #import pdb; pdb.set_trace()
        #suite_dir = "/java/DEV/loader/ott/loader/otp/tests/suites"
        ret_val = False
        log.info('GRAPH TESTS: Starting tests!')
        time.sleep(delay)
        t = TestRunner(hostname=hostname, port=port, suite_dir=suite_dir, filter=filter)
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


def main(argv=sys.argv):
    #import pdb; pdb.set_trace()

    parser = get_args_parser()
    args = parser.parse_args()

    dir = None
    if args.debug:
        #log.basicConfig(level=log.DEBUG)
        dir = os.path.join(TestRunner.this_module_dir, "..", "tests", "suites")

    TestRunner.test_graph_factory(graph_dir=dir, suite_dir=dir, hostname=args.hostname, filter=args.test_suite)

if __name__ == '__main__':
    #test_email()
    main()

def test_email():
    #import pdb; pdb.set_trace()
    t = TestRunner()
    t.send_email()

