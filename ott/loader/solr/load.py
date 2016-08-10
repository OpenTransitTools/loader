import os
import logging
log = logging.getLogger(__file__)

from ott.utils import file_utils
from ott.loader.solr.solr_cache import SolrCache


class Load(object):
    """ load GTFS data into a gtfsdb
    """
    cache = None
    config = None
    post_process_dir = None

    def __init__(self):
        self.cache = SolrCache()
        self.config = self.cache.config
        self.post_process_dir = os.path.join(self.cache.cache_dir, 'processed')
        file_utils.mkdir(self.post_process_dir)

    @classmethod
    def solr_loader(cls):
        '''
        '''
        loader = Load()
        loader.process_del_files()
        loader.process_add_files()

    def process_add_files(self):
        '''
        '''
        files = file_utils.ls(self.cache.cache_dir, "_add.xml")
        for f in files:
            self._process_file(f)

    def process_del_files(self):
        ''' run thru all the <name_del.xml> files in the cache
            TODO: should I first check that an add file exists, and that it contains valid content?
        '''
        files = file_utils.ls(self.cache.cache_dir, "_del.xml")
        for f in files:
            self._process_file(f)

    def _process_file(self, file_name):
        '''
        '''

        # step 1: load file
        file_path = os.path.join(self.cache.cache_dir, file_name)
        print file_path

        url   = self.config.get('url')
        if ":{}" in url or ":{0}" in url:
            ports = self.config.get_list('ports', def_val='80')
            for p in ports:
                print url.format(p)
        else:
            print url

        # step 2: mv file to processed folder
        to_path = os.path.join(self.post_process_dir, file_name)
        #file_utils.mv(file_path, to_path)

        # step 3:


