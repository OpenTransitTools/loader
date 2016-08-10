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

    def commit(self):
        ''' send solr_commit.xml to SOLR to commit any index changes
        '''

    def optimize(self):
        ''' send solr_optimize.xml (<optimize/>) to SOLR to commit any index changes
        '''

    def _process_file(self, file_name):
        '''
        '''

        # step 1: grab file path
        file_path = os.path.join(self.cache.cache_dir, file_name)
        print file_path

        # step 2: grab SOLR properties for url (and optionally the web ports where SOLR instance(es) run
        url  = self.config.get('url')
        port = None
        if ":{}" in url or ":{0}" in url:
            ports = self.config.get_list('ports', def_val='80')

        # step 3: update SOLR
        if ports:
            # step 3a: update one instance of SOLR (assumes they use a shared index)
            print url.format(ports[0])

            # step 3b: refresh all instances of SOLR
            for p in ports:
                print url.format(p)
        else:
            # step 3c: update and refresh the single instance of SOLR
            print url
            print url

        # step 4: mv file to processed folder
        to_path = os.path.join(self.post_process_dir, file_name)
        #file_utils.mv(file_path, to_path)
