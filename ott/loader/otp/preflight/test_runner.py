import os
import sys
import time
import inspect
import logging
log = logging.getLogger(__file__)

from mako.template import Template

from ott.utils.config_util import ConfigUtil

from .test_suite import ListTestSuites


class TestRunner(object):
    """ Run .csv tests from ./tests/ by constructing a
        url to the trip planner, calling the url, then printing a report
    """
    this_module_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

    def __init__(self, port=8001, suite_dir=None, report_mako_path=None, date=None):
        """constructor builds the test runner
        """
        self.config = ConfigUtil(section='otp')
        domain = self.config.get('domain', def_val="127.0.0.1")

        ws = self.config.get('ws_url_path', def_val="/otp/routers/default/plan")
        ws_url  = "http://{}:{}{}".format(domain, port, ws)

        map = self.config.get('map_url_path', def_val="")
        map_url = "http://{}:{}{}".format(domain, port, map)

        if suite_dir is None:
            suite_dir = os.path.join(self.this_module_dir, "suites")
        if report_mako_path is None:
            report_mako_path = os.path.join(self.this_module_dir, 'templates', 'good_bad.html')

        self.report_template = Template(filename=report_mako_path)
        self.test_suites = ListTestSuites(ws_url=ws_url, map_url=map_url, suite_dir=suite_dir, date=date)

    def report(self, dir=None, report_name='otp_report.html'):
        """ render a pass/fail report
        """
        ret_val = None
        try:
            # step 1: mako render of the report
            #import pdb; pdb.set_trace()
            r = self.report_template.render(test_suites=self.test_suites.get_suites(), test_errors=self.test_suites.has_errors())
            ret_val = r

            # step 2: stream the report to a file
            report_path = report_name
            if dir:
                report_path = os.path.join(dir, report_name)
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

    @classmethod
    def test_graph_factory(cls, graph_dir, suite_dir, port=None, delay=1):
        ''' run graph tests against whatever server is running
        '''
        #import pdb; pdb.set_trace()
        suite_dir = "/java/DEV/loader/ott/loader/otp/tests/suites"
        ret_val = False
        log.info('GRAPH TESTS: Starting tests!')
        time.sleep(delay)
        t = TestRunner(port=port, suite_dir=suite_dir)
        t.test_suites.run()
        t.report(graph_dir)
        if t.test_suites.has_errors():
            log.info('GRAPH TESTS: There were errors!')
            ret_val = False
        else:
            log.info('GRAPH TESTS: Nope, no errors...')
            ret_val = True
        return ret_val


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
    main()
