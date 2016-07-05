import os
import logging
log = logging.getLogger(__file__)

from ott.utils.cache_base import CacheBase
from ott.utils import object_utils

from ott.loader.sum.sobi.sobi_cache import SobiCache

class SumCache(CacheBase):
    """ Does a 'smart' cache of a SUM data
         -
    """
    def __init__(self, force_update=False):
        ''' check osm cache
        '''
        super(SumCache, self).__init__(section='sum')

        # check sobi
        if True or self.config.get('name', 'sobi'):
            sobi = SobiCache()
            sobi.check_feed(force_update)


def main():
    #import pdb; pdb.set_trace()
    sum = SumCache(force_update=object_utils.is_force_update())

if __name__ == '__main__':
    main()
