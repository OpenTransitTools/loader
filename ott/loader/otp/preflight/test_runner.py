import os
import sys
import time
import inspect
import logging
log = logging.getLogger(__file__)

from mako.template import Template
from mako import exceptions

from .test_suite import ListTestSuites


class TestRunner(object):
    """ Run .csv tests from ./tests/ by constructing a
        url to the trip planner, calling the url, then printing a report
    """
    this_module_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    base_url = None

    def __init__(self, base_url, dir=None, report_template=None, date=None):
        """constructor builds the test runner
        """
        if base_url:
            base_url = "http://127.0.0.1:55555"
        if dir is None:
            dir = os.path.join(self.this_module_dir, "suites")
        if report_template is None:
            report_template = os.path.join(self.this_module_dir, 'templates', 'good_bad.html')

        self.test_suites = ListTestSuites(base_url, dir, date)
        self.report_template = Template(filename=report_template)

    def report(self, dir=None, report_name='otp_report.html'):
        """ render a pass/fail report
        """
        ret_val = None
        try:
            # step 1: mako render of the report
            host = "FIX ME"
            r = self.report_template.render(host, test_suites=self.test_suites, test_errors=self.has_errors())
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
        except Exception, e:
            print exceptions.text_error_template().render()
        return ret_val

    @classmethod
    def test_graph(cls, graph_dir, suite_dir=None, base_url=None, delay=1):
        ''' run graph tests against whatever server is running
        '''
        import pdb; pdb.set_trace()
        ret_val = False
        log.info('GRAPH TESTS: Starting tests!')
        time.sleep(delay)
        t = TestRunner(base_url, suite_dir)
        t.test_suites.run()
        t.report(graph_dir)
        if t.has_errors():
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
        TestRunner.test_graph(suite_dir=dir)

if __name__ == '__main__':
    main()
