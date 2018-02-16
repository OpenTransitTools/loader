from osmread import parse_file, Way

from ott.utils import json_utils
from ott.utils import date_utils
from ott.utils import file_utils

import logging
log = logging.getLogger(__file__)


class OsmInfo(object):
    """
    Utility for getting stats on an osm file
    """
    def __init__(self):
        """ TODO think about rewriting this to simply read file line by line and find latest stamps and count tags...
        will be much faster than osmread on big files...
        """
        self.way_count = 0
        self.highway_count = 0

        class Last(object):
            timestamp = 0
            changeset = 0
        self.last = Last()

    def __str__(self):
        return json_utils.json_repr(self, pretty_print=True)

    def to_json(self):
        return json_utils.obj_to_dict(self)

    def write_json_file(self, file_path, pretty_print=False):
        json_utils.object_to_json_file(file_path, self, pretty_print)

    def calculate_osm_stats(self, osm_path):
        """ reads the .osm file and captures certain stats like last update and number of ways, etc... 
        """
        log.info("calculating stats for {}".format(osm_path))
        for entity in parse_file(osm_path):
            if isinstance(entity, Way):
                self.way_count += 1
                if 'highway' in entity.tags:
                    self.highway_count += 1
                if entity.timestamp > self.last.timestamp:
                    self.last.timestamp = entity.timestamp
                    self.last.changeset = entity.changeset

        # clean up data
        self.last.changeset_url = "http://openstreetmap.org/changeset/{}".format(self.last.changeset)
        self.last.edit_date = date_utils.pretty_date_from_ms(self.last.timestamp * 1000, fmt="%B %d, %Y")
        self.last.file_date = file_utils.file_pretty_date(osm_path, fmt="%B %d, %Y")

    @classmethod
    def find_osm_files(cls, dir_path):
        ret_val = []
        osm = file_utils.find_files(dir_path, ".osm")
        if osm:
            ret_val.extend(osm)
        pbf = file_utils.find_files(dir_path, ".pbf")
        if pbf:
            ret_val.extend(pbf)
        return ret_val

    @classmethod
    def get_stats_file_path(cls, osm_file, stats_file=None):
        if stats_file is None:
            stats_file = osm_file + "-stats"
        return stats_file

    @classmethod
    def cache_stats(cls, osm_path, stats_file=None, pretty_print=True):
        """ return OSM .osm-stats info json
            will either read the .osm-stats file or create a new stats file calculated via the .osm file
        """
        # import pdb; pdb.set_trace()
        stats_path = cls.get_stats_file_path(osm_path, stats_file)
        is_stats_good = False

        # step 1: read the .osm-stats cache file (if exists and stats are newer than osm)
        if not file_utils.is_a_newer_than_b(osm_path, stats_path):
            j = json_utils.get_json(stats_path)
            if j.get('way_count') and j.get('highway_count') and j.get('last'):
                is_stats_good = True
                ret_val = j

        # step 2: if .osm-stats don't exists or are out of date, cache them
        if not is_stats_good:
            stats = OsmInfo()
            stats.calculate_osm_stats(osm_path)
            stats_file = cls.get_stats_file_path(osm_path, stats_file)
            stats.write_json_file(stats_file, pretty_print)
            ret_val = stats.to_json()

        return ret_val

    @classmethod
    def get_stats(cls, osm_file, stats_file=None, pretty_print=True):
        """ will either read a cache'd -stats file into memory, or calculate the stats, cache them and then return
            :return dict representing the json stats object
        """
        ret_val = None

        # step 1: validate stats file path
        stats_file = cls.get_stats_file_path(osm_file, stats_file)

        # step 2: if the stats file exists and is newere than the .osm file, try to read it in
        if file_utils.exists(stats_file) and file_utils.is_a_newer_than_b(stats_file, osm_file):
            ret_val = json_utils.get_json(stats_file)

        # step 3: if we don't have stats from a cache'd file, calculate new stats and write them out
        if ret_val is None or len(ret_val) < 2:
            ret_val = cls.cache_stats(osm_file, stats_file, pretty_print)

        # step 4: return the stats as a string
        return ret_val

    @classmethod
    def get_osm_feed_msg(cls, file_path, prefix=" ", suffix="\n"):
        """ get osm feed details msg string for the .v log file
        """
        file_name = file_utils.get_file_name_from_path(file_path)
        stats = OsmInfo.get_stats(file_path)
        msg = "{}{} : file date: {} -- last OSM update: {}, changeset {}{}"\
            .format(prefix, file_name, stats['last'].get('file_date'), stats['last'].get('edit_date'), stats['last'].get('changeset'), suffix)
        return msg

    @classmethod
    def get_cache_msgs(cls, cache_path, def_msg=""):
        """return message for all OSM feeds in the cache directory """
        osm_msg = def_msg
        try:
            osm_files = OsmInfo.find_osm_files(cache_path)
            for f in osm_files:
                osm_msg += OsmInfo.get_osm_feed_msg(f)
        except Exception, e:
            log.info(e)
        return osm_msg

    @classmethod
    def print_stats(cls):
        """ run the SUM loader routines
        """
        from .osm_cache import OsmCache
        c = OsmCache()
        s = OsmInfo.get_stats(c.osm_path)
        print json_utils.dict_to_json_str(s, pretty_print=True)
        print ""
        print OsmInfo.get_cache_msgs(c.cache_dir)
