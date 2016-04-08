import os
import logging

from ott.utils import file_utils
from ott.loader.gtfs.base import Base


class OsmCache(Base):
    """ Does a 'smart' cache of a gtfs file
         1. it will look to see if a gtfs.zip file is in the cache, and download it and put it in the cache if not
         2. once cached, it will check to see that the file in the cache is the most up to date data...
    """
    pbf_url   = None
    pbf_name  = None
    pbf_path  = None
    meta_url  = None
    meta_name = None
    meta_path = None
    osm_name  = None
    osm_path  = None

    cache_dir = None
    cache_expire = 31

    def __init__(self, name, pbf_url, meta_url=None, cache_dir=None, cache_expire=2, min_size=1000000000, force_download=False):

        # step 1: cache dir management
        self.cache_dir = self.get_cache_dir(cache_dir)
        self.cache_expire = cache_expire

        # step 3: file names
        self.pbf_name  = name + ".pbf"
        self.meta_name = name + ".html"
        self.osm_name  = name + ".osm"

        # step 3: file cache paths
        self.pbf_path  = os.path.join(self.cache_dir, self.pbf_name)
        self.meta_path = os.path.join(self.cache_dir, self.meta_name)
        self.osm_path  = os.path.join(self.cache_dir, self.osm_name)

        # step 4: download new osm pbf file if it's not new
        if force_download or \
           not self.is_fresh_in_cache() or \
           not self.is_fresh_in_cache():
            self.download_pbf()

        # step 5: .pbf to .osm
        self.pbf_to_osm()

    def pbf_to_osm(self):
        pass

    def download_pbf(self):
        logging.info("empty method ... override me")
        pass
