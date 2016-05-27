import os
import logging
log = logging.getLogger(__file__)

from ott.utils import exe_utils
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

    def __init__(self):
        ''' check osm cache
        '''
        super(OsmCache, self).__init__(section='osm')

        # step 1: cache dir management
        self.cache_expire = self.config.get_int('cache_expire', def_val=self.cache_expire)

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

    def check_cached_osm(self, force_update=False):
        ''' if OSM .pbf file is out of date, download a new one.
            convert .pbf to .osm if .pbf file is newer than .osm file
        '''
        min_size = self.config.get_int('min_size', def_val=1000000)

        # step 1: download new osm pbf file if it's not new
        fresh = self.is_fresh_in_cache(self.pbf_path)
        sized = file_utils.is_min_sized(self.pbf_path, min_size)
        if force_update or not fresh or not sized:
            self.download_pbf()

        # step 2: .pbf to .osm
        if not file_utils.is_min_sized(self.pbf_path, min_size):
            log.warn("OSM PBF file {} is not big enough".format(self.pbf_path))
        else:
            fresh = self.is_fresh_in_cache(self.osm_path)
            newer = file_utils.is_a_newer_than_b(self.pbf_path, self.osm_path)
            if force_update or not fresh or newer:
                self.pbf_to_osm()

        # step 3: .osm file check
        if not file_utils.is_min_sized(self.osm_path, min_size):
            e = "OSM file {} is not big enough".format(self.osm_path)
            raise Exception(e)


    def get_osmosis_cmd(self):
        ''' build osmosis cmd line to convert .pbf to .osm file
        '''

        # step 1: get osmosis binary path (for ux or dos, ala c:\\ in path will get you a .bin extension)
        osmosis_dir = os.path.join(self.this_module_dir, "osmosis")
        osmosis_exe = os.path.join(osmosis_dir, "bin", "osmosis")
        if ":\\" in osmosis_exe:
            osmosis_exe = osmosis_exe + ".bat"

        # step 2: osmosis installed?
        if not os.path.exists(osmosis_exe):
            e = "OSMOSIS {} doesn't exist...\nMaybe cd into {} and run osmosis.sh".format(osmosis_exe, osmosis_dir)
            raise Exception(e)

        # step 3: build full osmosis cmd line
        osmosis = "{} --rb {} --bounding-box top={} bottom={} left={} right={} completeWays=true --wx {}"
        osmosis = osmosis.format(osmosis_exe, self.pbf_path, self.top, self.bottom, self.left, self.right, self.osm_path)
        return osmosis

    def pbf_to_osm(self):
        ''' use osmosis to convert .pbf to .osm file
        '''
        osmosis = self.get_osmosis_cmd()
        log.info(osmosis)
        exe_utils.run_cmd(osmosis, shell=True)

    def download_pbf(self):
        log.info("wget {} to {}".format(self.pbf_url, self.pbf_path))
        file_utils.bkup(self.pbf_path)
        exe_utils.wget(self.pbf_url, self.pbf_path)
        if self.meta_url:
            exe_utils.wget(self.meta_url, self.meta_path)

    @classmethod
    def check_osm_file_against_cache(cls, app_dir, force_update=False):
        ''' check the .osm file in this cache against an osm file in another app's directory
        '''
        ret_val = False
        try:
            osm = OsmCache()
            app_osm_path = os.path.join(app_dir, osm.osm_name)
            refresh = file_utils.is_a_newer_than_b(osm.osm_path, app_osm_path)
            if refresh or force_update:
                log.info("cp {} to {}".format(osm.osm_name, app_dir))
                osm.cp_cached_file(osm.osm_name, app_dir)
                ret_val = True
        except Exception, e:
            log.warn(e)
        return ret_val


def main():
    #import pdb; pdb.set_trace()
    osm = OsmCache()
    osm.check_cached_osm(force_update=object_utils.is_force_update())

if __name__ == '__main__':
    main()
