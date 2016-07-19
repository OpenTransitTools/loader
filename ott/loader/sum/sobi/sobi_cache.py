import os
import logging
log = logging.getLogger(__file__)

from ott.utils.cache_base import CacheBase
from ott.loader.solr.solr_add import SolrAdd


class SobiCache(CacheBase):
    """ cache a SOBI .json file
        @see http://socialbicycles.com/
    """
    url = None
    name = None
    type = 'bikeshare'
    file_name = None
    file_path = None
    solr_file_name = None
    solr_file_path = None

    def __init__(self):
        super(SobiCache, self).__init__(section='sobi')
        self.url = self.config.get('download_url')
        self.name = self.config.get('name')

        self.file_name = self.name + ".json"
        self.file_path = os.path.join(self.cache_dir, self.file_name)

        self.solr_file_name = self.name + "-solr.xml"
        self.solr_file_path = os.path.join(self.cache_dir, self.solr_file_name)

    def check_feed(self, force_update=False):
        #import pdb; pdb.set_trace()
        ret_val = self.simple_cache_item_update(self.file_name, self.url, force_update)
        if True or ret_val:
            ret_val = self.to_solr()
        return ret_val

    def get_active_racks(self):
        ret_val = []
        f = None
        try:
            f = open(self.file_path)

        finally:
            if f:
                f.close()
        pass

    def to_solr(self):
        '''
        '''
        solr = SolrAdd(type=self.type, type_name=self.name)

        for r in self.get_rack_data():
            solr.new_doc(id='xxx')
            solr.add_lon_lat('-122.5', '45.5')

        return solr


def mock():
    ''' mock up
    '''
    s = SolrAdd(type='bikeshare', type_name='BIKETOWN')
    s.new_doc(id='xxx')
    s.add_lon_lat('-122.5', '45.5')

    s.new_doc(id='zzz')
    s.add_lon_lat('-122.5', '45.5')

    print s.document_to_string()
