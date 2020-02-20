import os
from ott.utils import file_utils
from ott.loader.gtfs.files import Files
from ott.utils.cache_base import CacheBase

import logging
log = logging.getLogger(__file__)


class Routes(CacheBase):
    """
    export routes data from gtfs data
    """
    def __init__(self):
        super(Routes, self).__init__(section='geocoder')
        self.gtfs_file = self.config.get('gtfs_zip', def_val="TRIMET.zip")
        self.routes_path = self.make_pelias_csv(self.gtfs_file)
        self.csv_file = self.config.get('routes_csv', def_val="TRIMET-routes.csv")
        self.csv_path = os.path.join(self.cache_dir, self.csv_file)

    def make_pelias_csv(self, gtfs_file, file_name="routes.txt"):
        f = Files(gtfs_file)
        path = f.export(file_name)
        return path

    @classmethod
    def export(cls):
        r = Routes()

