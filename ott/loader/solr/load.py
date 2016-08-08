import os
import logging
log = logging.getLogger(__file__)

from ott.utils import file_utils
from ott.utils import object_utils
from ott.utils.cache_base import CacheBase

class Load(CacheBase):
    """ load GTFS data into a gtfsdb
    """
    post_process_dir = None

    def __init__(self):
        super(Load, self).__init__(section='solr')

        self.post_process_dir = os.path.join(self.this_cache_dir, 'processed')
        file_utils.mkdir(self.post_process_dir)

    def refresh(self):
        '''
        '''

    def process_add_files(self):
        '''
        '''

    def process_del_files(self):
        ''' run thru all the <name_del.xml> files in the cache
            TODO: should I first check that an add file exists, and that it contains valid content?
        '''

    def _process_file(self, file_name):
        '''
        '''

        # step 1: load file


        # step 2: mv file to processed folder
        file_utils.mv(file_name, self.post_process_dir)

        # step 3:


