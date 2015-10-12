import unittest
import os
import inspect

from ott.loader.gtfs.cache import Cache
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

    def test_same(self):
        pass

