from ott.utils import exe_utils
from ott.utils import file_utils
from ott.utils import object_utils
from ott.utils import web_utils
from ott.utils import string_utils
from ott.utils.cache_base import CacheBase
from .osm_info import OsmInfo
from .osm_rename import OsmRename

import os
import re
import logging
log = logging.getLogger(__file__)


class OsmCache(CacheBase):
    """ Does a 'smart' cache of a gtfs file
         1. it will look to see if a gtfs.zip file is in the cache, and download it and put it in the cache if not
         2. once cached, it will check to see that the file in the cache is the most up to date data...
    """
    pbf_url = None
    pbf_name = None
    pbf_path = None
    pbf_url = None

    meta_url = None
    meta_name = None
    meta_path = None
    meta_url = None

    osm_name = None
    osm_path = None

    top = None
    bottom = None
    left = None
    right = None

    def __init__(self):
        """ check osm cache
        """
        super(OsmCache, self).__init__(section='osm')

        # step 1: cache dir management
        self.cache_expire = self.config.get_int('cache_expire', def_val=self.cache_expire)

        # step 2: .pbf and .html (meta data) urls and file names
        self.pbf_url = self.config.get('pbf_url')
        self.pbf_name = web_utils.get_name_from_url(self.pbf_url)
        self.meta_url = self.config.get('meta_url')
        self.meta_name = web_utils.get_name_from_url(self.meta_url)

        # step 3: output .osm file name
        name = self.config.get('name')
        self.osm_name = string_utils.safe_append(name, ".osm")

        # step 4: file cache paths
        self.pbf_path = string_utils.safe_path_join(self.cache_dir, self.pbf_name)
        self.meta_path = string_utils.safe_path_join(self.cache_dir, self.meta_name)
        self.osm_path = string_utils.safe_path_join(self.cache_dir, self.osm_name)

    def check_cached_osm(self, force_update=False):
        """
        if OSM .pbf file is out of date, download a new one.
        convert .pbf to .osm if .pbf file is newer than .osm file
        :return indication if updated
        """
        is_updated = force_update

        min_size = self.config.get_int('min_size', def_val=100000)

        # step 1: download new osm pbf file if it's not new
        fresh = self.is_fresh_in_cache(self.pbf_path)
        sized = file_utils.is_min_sized(self.pbf_path, min_size)
        if force_update or not fresh or not sized:
            self.download_pbf()
            is_updated = True

        # step 2: .pbf to .osm
        if not file_utils.is_min_sized(self.pbf_path, min_size):
            log.warn("OSM PBF file {} is not big enough".format(self.pbf_path))
        else:
            fresh = self.is_fresh_in_cache(self.osm_path)
            sized = file_utils.is_min_sized(self.osm_path, min_size)
            pbf_newer = file_utils.is_a_newer_than_b(self.pbf_path, self.osm_path, offset_minutes=10)
            if is_updated or pbf_newer or not fresh or not sized:
                self.clip_to_bbox(input_path=self.pbf_path, output_path=self.osm_path)
                is_updated = True
            else:
                is_updated = False

        # step 3: .osm file check
        if not file_utils.is_min_sized(self.osm_path, min_size):
            e = "OSM file {} is not big enough".format(self.osm_path)
            raise Exception(e)

        # step 4: other OSM processing steps on a new (fresh) .osm file
        if is_updated:
            OsmRename.rename(self.osm_path, do_bkup=False)
            OsmInfo.cache_stats(self.osm_path)
            self.osm_to_pbf()
            self.other_exports()
        return is_updated

    def get_osmosis_exe(self):
        """ get the path osmosis binary
            TODO - we should look for system installed osmosis first
        """
        # step 1: get osmosis binary path (for ux or dos, ala c:\\ in path will get you a .bin extension)
        osmosis_dir = os.path.join(self.this_module_dir, "osmosis")
        osmosis_exe = os.path.join(osmosis_dir, "bin", "osmosis")
        if ":\\" in osmosis_exe:
            osmosis_exe = osmosis_exe + ".bat"

        # step 2: osmosis installed?
        if not os.path.exists(osmosis_exe):
            e = "OSMOSIS {} doesn't exist...\nMaybe cd into {} and run osmosis.sh".format(osmosis_exe, osmosis_dir)
            raise Exception(e)
        return osmosis_exe

    def clip_to_bbox(self, input_path, output_path, bbox_ini_section="bbox"):
        """ use osmosis to clip a bbox out of a .pbf, and output .osm file
            (file paths derrived by the cache paths & config)
            outputs: both an .osm file and a .pbf file of the clipped area
        """
        # import pdb; pdb.set_trace()
        top, bottom, left, right = self.config.get_bbox(bbox_ini_section)
        osmosis_exe = self.get_osmosis_exe()
        osmosis = "{} --rb {} --bounding-box top={} bottom={} left={} right={} completeWays=true --wx {}"
        osmosis_cmd = osmosis.format(osmosis_exe, input_path, top, bottom, left, right, output_path)
        log.info(osmosis_cmd)
        exe_utils.run_cmd(osmosis_cmd, shell=True)

    def osm_to_pbf(self, osm_path=None, pbf_path=None):
        """ use osmosis to convert .osm file to .pbf
        """
        if osm_path is None:
            osm_path = self.osm_path
        if pbf_path is None:
            pbf_path = re.sub('.osm$', '', osm_path) + ".pbf"
        osmosis_exe = self.get_osmosis_exe()
        osmosis = '{} --read-xml {} --write-pbf {}'
        osmosis_cmd = osmosis.format(osmosis_exe, osm_path, pbf_path)
        exe_utils.run_cmd(osmosis_cmd, shell=True)

    def pbf_to_osm(self, osm_path=None, pbf_path=None):
        """ use osmosis to convert .pbf to .osm file
        """
        if osm_path is None:
            osm_path = self.osm_path
        if pbf_path is None:
            pbf_path = re.sub('.osm$', '', osm_path) + ".pbf"
        osmosis_exe = self.get_osmosis_exe()
        osmosis = '{} --read-pbf {} --write-xml {}'
        osmosis_cmd = osmosis.format(osmosis_exe, pbf_path, osm_path)
        exe_utils.run_cmd(osmosis_cmd, shell=True)

    def download_pbf(self):
        log.info("wget {} to {}".format(self.pbf_url, self.pbf_path))
        file_utils.bkup(self.pbf_path)
        web_utils.wget(self.pbf_url, self.pbf_path)
        if self.meta_url:
            web_utils.wget(self.meta_url, self.meta_path)

    @classmethod
    def check_osm_file_against_cache(cls, app_dir, force_update=False):
        """
        check the .osm file in this cache against an osm file in another app's directory (e.g., OTP folder)
        """
        ret_val = False
        try:
            osm = OsmCache()
            app_osm_path = os.path.join(app_dir, osm.osm_name)
            refresh = file_utils.is_a_newer_than_b(osm.osm_path, app_osm_path, offset_minutes=10)
            if refresh or force_update:
                # step a: copy the .osm file to this foreign cache
                log.info("cp {} to {}".format(osm.osm_name, app_dir))
                osm.cp_cached_file(osm.osm_name, app_dir)

                # step b: copy the stats file to this foreign cache
                cache_file = OsmInfo.get_stats_file_path(osm.osm_name)
                osm.cp_cached_file(cache_file, app_dir)
                ret_val = True
        except Exception, e:
            log.warn(e)
        return ret_val

    def is_configured(self):
        return self.osm_name and self.osm_path and self.pbf_name and self.pbf_path

    @classmethod
    def update(cls, force_update):
        """ check OSM for freshness
        """
        # import pdb; pdb.set_trace()
        ret_val = False
        osm = OsmCache()
        if osm.is_configured():
            ret_val = osm.check_cached_osm(force_update)
        return ret_val

    @classmethod
    def load(cls):
        """ run the SUM loader routines
        """
        osm = OsmCache()
        osm.check_cached_osm(force_update=object_utils.is_force_update())

    @classmethod
    def convert_osm_to_pbf(cls):
        """ run the SUM loader routines
        """
        osm = OsmCache()
        osm.osm_to_pbf()

    @classmethod
    def convert_pbf_to_osm(cls):
        """ run the SUM loader routines
        """
        osm = OsmCache()
        osm.pbf_to_osm()

    @classmethod
    def other_exports(cls):
        """ export other .osm files
        """
        osm = OsmCache()
        exports = osm.config.get_json('other_exports')
        for e in exports:
            in_path = os.path.join(osm.cache_dir,  e['in'])
            out_path = os.path.join(osm.cache_dir, e['out'])
            osm.clip_to_bbox(input_path=in_path, output_path=out_path, bbox_ini_section=e['bbox'])
