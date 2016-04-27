import os
import logging

from ott.utils import file_utils
from ott.utils import object_utils
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

    top    = None
    bottom = None
    left   = None
    right  = None

    def __init__(self, force_update=False):
        ''' check osm cache
        '''
        #import pdb; pdb.set_trace()
        super(OsmCache, self).__init__(section='osm')

        # step 1: cache dir management
        self.cache_expire = self.config.get_int('cache_expire', def_val=self.cache_expire)
        min_size = self.config.get_int('min_size', def_val=1000000)

        # step 2: urls
        self.pbf_url  = self.config.get('pbf_url')
        self.meta_url = self.config.get('meta_url')

        # step 3: file names
        name = self.config.get('name')
        self.pbf_name  = name + ".pbf"
        self.meta_name = name + ".html"
        self.osm_name  = name + ".osm"

        # step 4: file cache paths
        self.pbf_path  = os.path.join(self.cache_dir, self.pbf_name)
        self.meta_path = os.path.join(self.cache_dir, self.meta_name)
        self.osm_path  = os.path.join(self.cache_dir, self.osm_name)

        # step 5: get bbox from config
        self.top, self.bottom, self.left, self.right = self.config.get_bbox()

        # step 6: download new osm pbf file if it's not new
        if force_update or \
           not self.is_fresh_in_cache(self.pbf_path) or \
           not file_utils.is_min_sized(self.pbf_path, min_size):
            self.download_pbf()

        # step 7: .pbf to .osm
        if file_utils.is_min_sized(self.pbf_path, min_size) and \
           (
               not self.is_fresh_in_cache(self.osm_path) or \
               file_utils.is_a_newer_than_b(self.pbf_path, self.osm_path)
           ):
            self.pbf_to_osm()

    def get_osmosis_cmd(self):
        ''' use osmosis to convert .pbf to .osm file
        '''
        osmosis_exe = os.path.join(self.this_module_dir, "osmosis", "bin", "osmosis")
        if ":\\" in osmosis_exe:
            osmosis_exe = osmosis_exe + ".bat"
        osmosis = "{} --rb {} --bounding-box top={} bottom={} left={} right={} completeWays=true --wx {}"
        osmosis = osmosis.format(osmosis_exe, self.pbf_path, self.top, self.bottom, self.left, self.right, self.osm_path)
        return osmosis

    def pbf_to_osm(self):
        ''' use osmosis to convert .pbf to .osm file
        '''
        osmosis = self.get_osmosis_cmd()
        logging.info(osmosis)
        os.system(osmosis)

    def download_pbf(self):
        logging.info("wget {} to {}".format(self.pbf_url, self.pbf_path))
        file_utils.bkup(self.pbf_path)
        file_utils.wget(self.pbf_url, self.pbf_path)
        if self.meta_url:
            file_utils.wget(self.meta_url, self.meta_path)

    @classmethod
    def check_osm_file_against_cache(cls, app_dir):
        ''' check the .osm file in this cache against an osm file in another app's directory
        '''
        ret_val = False
        try:
            cache = OsmCache()
            logging.info("cp {} to {}".format(cache.osm_name, app_dir))
            cache.cp_cached_file(cache.osm_name, app_dir)
            ret_val = True
        except Exception, e:
            logging.warn(e)
        return ret_val


def main():
    #import pdb; pdb.set_trace()
    OsmCache(force_update=object_utils.is_force_update())

if __name__ == '__main__':
    main()
