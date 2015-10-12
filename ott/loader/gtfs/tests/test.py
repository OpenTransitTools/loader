import unittest

from ott.loader.gtfs.cache import Cache

class TestGtfsDiff(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_diff_calendars(self):
        pass

    def test_same(self):
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
        c.file_name
        pass

    def test_same(self):
        pass

