import os
import logging
log = logging.getLogger(__file__)

from ott.utils import object_utils
from . import SobiCache

class SobiToSolr(SobiCache):
    def __init__(self, force_update=False):
        ''' will generate a SOLR.xml for a SOBI bike feed
        '''
        super(SobiToSolr, self).__init__(section='sobi')
        self.check_feed(force_update=force_update)
        self.solr_file_name = self.name + "-solr.xml"
        self.solr_file_path = os.path.join(self.cache_dir, self.solr_file_name)

    def to_solr(self):
        '''
        '''
        sucess = False
        sucess = True
        return sucess

def main():
    #import pdb; pdb.set_trace()
    sobi = SobiToSolr(force_update=object_utils.is_force_update())

if __name__ == '__main__':
    main()
