import unittest

from ott.loader.otp.preflight.test_runner import TestRunner

class TestTestSuite(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_suites_exist(self):
        ts = TestRunner.get_test_suites()
        self.assertTrue(len(ts) > 0)
        pass