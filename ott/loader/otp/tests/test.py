import unittest


class TestTestSuite(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_suites_exist(self):
        # TODO ... not sure what we wre doing here, but it's wrong right now
        # from ott.loader.otp.preflight.test_runner import TestRunner
        # ts = TestRunner.get_test_suites()
        self.assertTrue(len(ts) > 0)
        pass