import unittest

from ott.loader.otp.tester.test_runner import TestRunner

class TestTestSuite(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_diff_calendar(self):
        ts = TestRunner.get_test_suites()
        self.assertTrue(len(ts) > 0)
        pass