import os
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
    parser = otp_utils.get_initial_arg_parser('otp_test_runner')
    parser.add_argument('--hostname', '-hn', help="specify the hostname for the test url")
    parser.add_argument('--port',    '-p',   help="port")
    parser.add_argument('--filter',  '-f',   help="filter, ala -f Walk")
    parser.add_argument('--ws_path', '-ws',  help="OTP url path, ala 'prod' or '/otp/routers/default/plan'")
    parser.add_argument('--debug',   '-d',   help="run DEBUG suites", action='store_true')
    return parser


class TestRunner(object):
    """ Run .csv tests from ./tests/ by constructing a
        url to the trip planner, calling the url, then printing a report
    """
    this_module_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

    def __init__(self, hostname=None, ws_path=None, ws_port=None, app_path=None, app_port=None, suite_dir=None, filter=None, report_mako_path=None, date=None):
        """constructor builds the test runner
        """
        #import pdb; pdb.set_trace()
        # step 1: build OTP ws and map urls from config
        self.ws_url, self.app_url = otp_utils.get_test_urls_from_config(hostname, ws_path, ws_port, app_path, app_port)

        # step 2: set file and directory paths (suites dir contains .csv files defining tests)
        if suite_dir is None:
            suite_dir = os.path.join(self.this_module_dir, "suites")
        self.report_mako_path = report_mako_path
        if report_mako_path is None:
            self.report_mako_path = os.path.join(self.this_module_dir, 'templates', 'good_bad.html')

        # step 3: create mako template, and list of test suites
        self.report_template = Template(filename=self.report_mako_path)
        self.test_suites = ListTestSuites(ws_url=self.ws_url, map_url=self.app_url, suite_dir=suite_dir, date=date, filter=filter)

    def report(self, dir=None, report_name='otp_report.html'):
        """ render a test pass/fail report with mako
        """
        ret_val = None
        try:
            # step 1: mako render of the report
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
        msg = None
        try:
            t = time.strftime('%B %d, %Y (%A) %I:%M%p').lower().replace(" 0", " ")
            m = ""
            p = "PASSED"
            if self.test_suites.has_errors():
                p = "FAILED"
                m = self.test_suites.list_errors()
            msg = "OTP tests {} on {}\n{}\nOTP endpoint: {}".format(p, t, m, self.test_suites.ws_url)
            recipients = ConfigUtil(section='contact').get('emails')
            web_utils.simple_email(msg, recipients)
        except Exception, e:
            log.warn(e)
        finally:
            if msg:
                log.info(msg)

    @classmethod
    def test_graph_factory(cls, hostname=None, ws_path=None, ws_port=None, app_path=None, app_port=None, suite_dir=None, filter=None, graph_dir=None, delay=1):
        """ run graph tests against whatever server is running
            @see otp_builder.py: TestRunner.test_graph_factory(port=graph['port'], suite_dir=suite_dir, graph_dir=graph['dir'], delay=delay)
        """
        ret_val = False
        log.info('GRAPH TESTS: Starting tests!')
        time.sleep(delay)
        t = TestRunner(hostname, ws_path, ws_port, app_path, app_port, suite_dir=suite_dir, filter=filter)
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

    @classmethod
    def test_graph_factory_args(cls, args, suite_dir, graph_dir):
        """ uses cmd-line params from argparse """
        return cls.test_graph_factory(args.hostname, args.ws_path, args.port, suite_dir=suite_dir, filter=args.test_suite)

    @classmethod
    def test_graph_factory_config(cls, graph, suite_dir=None, delay=1):
        """ expect a graph def from the config .ini file to populate test params """
        port = graph.get('port')
        ws_path = graph.get('ws_path')
        ws_port = "80" if ws_path else port
        app_path = graph.get('app_path')
        app_port = "80" if app_path else port
        return cls.test_graph_factory(ws_path=ws_path, ws_port=ws_port, app_path=app_path, app_port=app_port,
                                      graph_dir=graph.get('dir'), suite_dir=suite_dir, filter=graph.get('filter'),
                                      delay=delay)


def main():
    parser = get_args_parser()
    args = parser.parse_args()

    dir = None
    if args.debug:
        # run the suites from the ../tests directory
        dir = os.path.join(TestRunner.this_module_dir, "..", "tests", "suites")

    graph = None
    if args.name:
        g = otp_utils.get_graphs_from_config()
        graph = otp_utils.find_graph(g, args.name)
    if graph:
        TestRunner.test_graph_factory_config(graph, suite_dir=dir)
    else:
        TestRunner.test_graph_factory_args(args, suite_dir=dir, graph_dir=dir)

if __name__ == '__main__':
    #test_email()
    main()


def test_email():
    """ this is a test routine for the email sender...
    """
    #import pdb; pdb.set_trace()
    t = TestRunner()
    t.send_email()

