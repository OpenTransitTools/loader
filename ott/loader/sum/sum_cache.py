import os
import logging
log = logging.getLogger(__file__)

from ott.utils.cache_base import CacheBase
from ott.utils import object_utils

from ott.loader.sum.gbfs.gbfs_cache import GbfsCache
from ott.loader.sum.sobi.sobi_cache import SobiCache

class SumCache(CacheBase):
    """ Does a 'smart' cache of a SUM data
         -
    """
    def __init__(self, force_update=False):
        ''' check osm cache
        '''
        super(SumCache, self).__init__(section='sum')

        # check gbfs feed(s)
        # todo: should we support multiple feeds?
        if self.config.get('name', 'gbfs'):
            gbfs = GbfsCache()
            gbfs.check_feed(force_update)

        # check sobi
        if self.config.get('name', 'sobi'):
            sobi = SobiCache()
            sobi.check_feed(force_update)

    @classmethod
    def loader(cls):
        ''' run the SUM loader routines
        '''
        #import pdb; pdb.set_trace()
        sum = SumCache(force_update=object_utils.is_force_update())
        return sum
