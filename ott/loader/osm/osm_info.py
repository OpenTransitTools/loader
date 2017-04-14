from osmread import parse_file, Way

from ott.utils import json_utils
from ott.utils import date_utils
from ott.utils import file_utils

import logging
log = logging.getLogger(__file__)



class OsmInfo(object):
    """ Utility for getting stats on an osm file 
    """
    def __init__(self):
        """ 
        """
        self.way_count = 0
        self.highway_count = 0
        class Last(object):
            timestamp = 0
            changeset = 0
        self.last = Last()

    def __str__(self):
        return json_utils.json_repr(self, pretty_print=True)

    def to_json(self, pretty_print=False):
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
        self.last.date = date_utils.pretty_date_from_ms(self.last.timestamp * 1000)

    @classmethod
    def get_stats(cls, osm_file, stats_file=None, pretty_print=True):
        """ will either read a cache'd -stats file into memory, or calculate the stats, cache them and then return
            :return dict representing the json stats object
        """
        ret_val = None

        # step 1: make sure we have a stats file path
        if stats_file is None:
            stats_file = osm_file + "-stats"

        # step 2: if the stats file exists and is newere than the .osm file, try to read it in
        #import pdb; pdb.set_trace()
        if file_utils.exists(stats_file) and file_utils.is_a_newer_than_b(stats_file, osm_file):
            ret_val = json_utils.get_json(stats_file)

        # step 3: if we don't have stats from a cache'd file, calculate new stats and write them out
        if ret_val is None or len(ret_val) < 2:
            stats = OsmInfo()
            stats.calculate_osm_stats(osm_file)
            stats.write_json_file(stats_file, pretty_print)
            ret_val = stats.to_json()

        # step 4: return the stats as a string
        return ret_val

    @classmethod
    def print_stats(cls):
        """ run the SUM loader routines
        """
        from .osm_cache import OsmCache
        c = OsmCache()
        s = OsmInfo.get_stats(c.osm_name)
        print json_utils.dict_to_json_str(s, pretty_print=True)
