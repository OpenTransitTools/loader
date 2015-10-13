import os
import inspect
import unittest

from ott.loader.gtfs.cache import Cache
from ott.loader.gtfs.info import Info
from ott.loader.gtfs.diff import Diff

class TestGtfsDiff(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_diff_calendar(self):
        #import pdb; pdb.set_trace()
        this_module_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
        gtfsA = os.path.join(this_module_dir, "gtfsA.zip")
        gtfsB = os.path.join(this_module_dir, "gtfsB.zip")
        d = Diff(gtfsA, gtfsB)
        self.assertTrue(d.is_different())
        pass

    def test_diff_info(self):
        this_module_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
        gtfsA = os.path.join(this_module_dir, "gtfsB.zip")
        gtfsB = os.path.join(this_module_dir, "gtfsC.zip")
        d = Diff(gtfsA, gtfsB)
        self.assertTrue(d.is_different())
        pass

    def test_same(self):
        this_module_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
        gtfsA = os.path.join(this_module_dir, "gtfsB.zip")
        gtfsB = os.path.join(this_module_dir, "gtfsB.zip")
        d = Diff(gtfsA, gtfsB)
        self.assertFalse(d.is_different())
        pass


class TestGtfsCache(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_cache(self):
        url="https://developers.google.com/transit/gtfs/examples/sample-feed.zip"
        name="google.zip"
        c = Cache(url, name)
        self.assertTrue(os.path.exists(c.file_path))


class TestGtfsInfo(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_basic_info(self):
        this_module_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
        gtfsA = os.path.join(this_module_dir, "gtfsA.zip")

        i = Info(gtfsA)

        fi = i.get_feed_info()
        fi_match = ('20150927', '20160305', 'TriMet', '20150927-20151006-0140')
        self.assertEqual(fi, fi_match)

        fi = i.get_date_range_of_calendar_dates()
        fi_match = ('20070604', '20070604', 1, 1)
        self.assertEqual(fi, fi_match)

        fi = i.get_feed_version()
        fi_match = "20150927-20151006-0140"
        self.assertEqual(fi, fi_match)

        r = i.get_calendar_range()
        self.assertTrue(r[0] > 3000)
        self.assertTrue(r[1] < -3000)
        self.assertTrue(i.is_gtfs_out_of_date())