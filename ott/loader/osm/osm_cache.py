import os
import logging

from ott.utils import file_utils
from ott.utils.cache_base import CacheBase

class OsmCache(CacheBase):
    """ Does a 'smart' cache of a gtfs file
         1. it will look to see if a gtfs.zip file is in the cache, and download it and put it in the cache if not
         2. once cached, it will check to see that the file in the cache is the most up to date data...
    """
    pbf_url   = None
    pbf_name  = None
    pbf_path  = None
    pbf_url   = None

    meta_url  = None
    meta_name = None
    meta_path = None
    meta_url  = None

    osm_name  = None
    osm_path  = None

    top=45.8
    bottom=44.68
    left=-123.8
    right=-121.5

    def __init__(self, name, pbf_url=None, meta_url=None, cache_dir=None, cache_expire=2, min_size=1000000000, force_download=False):

        # step 1: cache dir management
        self.cache_expire = cache_expire

        # step 2: urls
        if pbf_url:  self.pbf_url  = pbf_url
        if meta_url: self.meta_url = meta_url

        # step 3: file names
        self.pbf_name  = name + ".pbf"
        self.meta_name = name + ".html"
        self.osm_name  = name + ".osm"

        # step 4: file cache paths
        self.pbf_path  = os.path.join(self.cache_dir, self.pbf_name)
        self.meta_path = os.path.join(self.cache_dir, self.meta_name)
        self.osm_path  = os.path.join(self.cache_dir, self.osm_name)

        # step 5: download new osm pbf file if it's not new
        if force_download or \
           not self.is_fresh_in_cache(self.pbf_path) or \
           not file_utils.is_min_sized(self.pbf_path, min_size):
            self.download_pbf()

        # step 6: .pbf to .osm
        #import pdb; pdb.set_trace()
        if file_utils.is_min_sized(self.pbf_path, min_size) and \
           (
               not self.is_fresh_in_cache(self.osm_path) or \
               file_utils.is_a_newer_than_b(self.pbf_path, self.osm_path)
           ):
            self.pbf_to_osm()

    def pbf_to_osm(self):
        ''' use osmosis to convert .pbf to .osm file
        '''
        osmosis = "{}/osmosis/bin/osmosis --rb {} --bounding-box top={} bottom={} left={} right={} completeWays=true --wx {}"
        osmosis = osmosis.format(self.this_module_dir, self.pbf_path, self.top, self.bottom, self.left, self.right, self.osm_path)
        logging.info(osmosis)
        os.system(osmosis)

    def download_pbf(self):
        logging.info("wget {} to {}".format(self.pbf_url, self.pbf_path))
        file_utils.bkup(self.pbf_path)
        file_utils.wget(self.pbf_url, self.pbf_path)
        if self.meta_url:
            file_utils.wget(self.meta_url, self.meta_path)
