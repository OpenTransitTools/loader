import os
import json
import logging
log = logging.getLogger(__file__)

from ott.utils.cache_base import CacheBase
from ott.loader.solr.solr_add import SolrAdd

from ott.gbfsdb.stations import Stations

class GbfsCache(CacheBase):
    """ cache GBFS .json files
        @see https://github.com/NABSA/gbfs
    """
    name = None
    feed_url = None
    type = 'bikeshare'

    def __init__(self):
        super(GbfsCache, self).__init__(section='gbfs')
        self.name = self.config.get('name')
        self.feed_url = self.config.get('feed_url')

    def check_feed(self, force_update=False):
        ret_val = True
        stations = Stations(self.feed_url)
        if ret_val:
            ret_val = self.to_solr(stations)
        return ret_val

    def to_solr(self, stations):
        solr = SolrAdd(type=self.type, type_name=self.name)
        for i, s in enumerate(stations.active_stations()):
            #status = s.get('status')
            station = s.get('station')
            solr.new_doc(id=str(station.get('station_id', i)), name=station.get('name'))
            solr.add_field('address', station.get('address'))
            solr.add_lon_lat(station.get('lon'), station.get('lat'))

        #import pdb; pdb.set_trace()
        solr.to_file(path=self.cache_dir)
        return solr
