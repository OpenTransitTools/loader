import os
import json
import logging
log = logging.getLogger(__file__)

from ott.utils.cache_base import CacheBase
from ott.loader.solr.solr_add import SolrAdd


class GbfsCache(CacheBase):
    """ cache GBFS .json files
        @see https://github.com/NABSA/gbfs
    """
    name = None
    type = 'bikeshare'
    file_name = None
    file_path = None

    def __init__(self):
        super(GbfsCache, self).__init__(section='gbfs')
        self.name = self.config.get('name')
        self.url = self.config.get('download_url')
        self.file_name = self.name + ".json"
        self.file_path = os.path.join(self.cache_dir, self.file_name)

    def check_feed(self, force_update=False):
        ret_val = self.simple_cache_item_update(self.file_name, self.url, force_update)
        if True or ret_val:
            ret_val = self.to_solr()
        return ret_val

    def to_solr(self):
        solr = SolrAdd(type=self.type, type_name=self.name)
        for i,r in enumerate(self.get_racks()):
            solr.new_doc(id=str(r.get('id', i)), name=r.get('name'))
            solr.add_field('address', r.get('address'))
            solr.add_point(r.get('middle_point'))

        #import pdb; pdb.set_trace()
        solr.to_file(path=self.cache_dir)
        return solr
