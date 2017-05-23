import os
import sys
import unittest

from ott.loader.osm.osm_rename import OsmRename
from ott.utils import file_utils

class TestOsmRename(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_rename(self):
        #import pdb; pdb.set_trace()
        dir = file_utils.get_module_dir(self.__class__)
        osm_in = os.path.join(dir,  "test_data.osm")
        osm_out = os.path.join(dir, "test_renamed.osm")

        OsmRename.rename(osm_in, osm_out)
        #self.assertTrue()

