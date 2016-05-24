import os
import inspect
import sys
import time
import logging
log = logging.getLogger(__file__)

from mako.template import Template
from mako import exceptions

from .test_suite import TestSuite


class TestRunner(object):
    """ Run .csv tests from ./tests/ by constructing a
        url to the trip planner, calling the url, then printing a report
    """
    this_module_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

    def __init__(self, report_template=None, date=None):
        """constructor builds the test runner
        """
        self.test_suites = self.get_test_suites(date)
        if report_template is None:
            report_template = os.path.join(self.this_module_dir, 'templates', 'good_bad.html')
        self.report_template = Template(filename=report_template)

    def run(self):
        """ execute tests
        """
        for ts in self.test_suites:
            ts.run()

    def printer(self):
        """ print test urls...
        """
        for ts in self.test_suites:
            ts.printer()

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

    def has_errors(self):
        ret_val = False
        for t in self.test_suites:
            if t.failures > 0 or t.passes <= 0:
                ret_val = True
                log.info("test_suite {0} has {1} error(s) and {2} passes".format(t, t.failures, t.passes))
        return ret_val

    @classmethod
    def get_suites_dir(cls, suites_name="suites"):
        this_module_dir = cls.this_module_dir
        suites_path = os.path.join(this_module_dir, suites_name)
        return suites_path

    @classmethod
    def get_test_suites(cls, date=None):
        test_suites = []
        dir = cls.get_suites_dir()
        files=os.listdir(dir)
        for f in files:
            if f.lower().endswith('.csv'):
                t = TestSuite(dir, f, date)
                test_suites.append(t)
        return test_suites

    @classmethod
    def test_graph(cls, graph_dir, url=None, delay=1):
        ''' run graph tests against whatever server is running
        '''
        ret_val = False
        log.info('GRAPH TESTS: Starting tests!')
        time.sleep(delay)
        t = TestRunner()
        t.run()
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
    if 'DEBUG' in argv:
        log.basicConfig(level=log.DEBUG)

    if 'STRESS' in argv:
        stress(argv)
    else:
        TestRunner.test_graph()

if __name__ == '__main__':
    main()
