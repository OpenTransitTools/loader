import os
import logging

from ott.utils import file_utils
from .osm_cache import OsmCache


class GeoFabrikCache(OsmCache):
    """ Does a 'smart' cache of a gtfs file
         1. it will look to see if a gtfs.zip file is in the cache, and download it and put it in the cache if not
         2. once cached, it will check to see that the file in the cache is the most up to date data...
    """
    pbf_url = ""
    meta_url = ""

    def __init__(self, force_download=False):
        super().__init__(args)

    def download_pbf(self):
        file_utils.bkup(self.pbf_path)
        pass


def main():
    pass

if __name__ == '__main__':
    main()
