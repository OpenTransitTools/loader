from osmread import parse_file, Way

from ott.utils import json_utils
from ott.utils import date_utils

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

    def get_osm_stats(self, osm_path):
        """ 
        """
        log.info("calculating stats for {}".format(osm_path))
        for entity in parse_file(osm_path):
            if isinstance(entity, Way):
                #import pdb; pdb.set_trace()
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
    def print_stats(cls):
        """ run the SUM loader routines
        """
        from .osm_cache import OsmCache
        c = OsmCache()
        stats = OsmInfo()
        stats.get_osm_stats(c.osm_name)
        print json_utils.json_repr(stats, pretty_print=True)
