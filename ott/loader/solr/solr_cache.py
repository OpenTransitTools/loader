import os
import logging
log = logging.getLogger(__file__)

from ott.utils.cache_base import CacheBase


class SolrCache(CacheBase):
    """ load
    """
    def __init__(self):
        super(SolrCache, self).__init__(section='solr')

    @classmethod
    def add_to_cache(self, solr):
        """ copy solr files to the cache where the SOLR loader will find and load them into SOLR
        """
        cache = SolrCache()
        solr.to_file(path=cache.cache_dir)
