import os
import sys
import unittest

from ott.loader.osm.osm_rename import OsmRename
from ott.utils import file_utils

class TestOsmRename(unittest.TestCase):

    def setUp(self):
        self.thisdir = file_utils.get_module_dir(self.__class__)
        self.osm_test_data = os.path.join(self.thisdir, "test_data.osm")
        self.osm_renamed_already = os.path.join(self.thisdir, "test_dont_rename_again.osm")
        pass

    def tearDown(self):
        pass

    def test_rename(self):
        osm_out = os.path.join(self.thisdir, "test_renamed.osm")
        OsmRename.rename(self.osm_test_data, osm_out)
        r = file_utils.grep(osm_out, "[North,South,East,West,Street,Avenue,Terrace,Road]")
        self.assertTrue(len(r) == 0)

    def test_rename_tag(self):
        osm_out = os.path.join(self.thisdir, "test_not_renamed.osm")
        OsmRename.rename(self.osm_renamed_already, osm_out)
        #self.assertTrue()

