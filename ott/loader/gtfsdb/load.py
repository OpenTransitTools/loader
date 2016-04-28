from ott.utils import object_utils
from ott.utils.cache_base import CacheBase
from ott.loader.gtfs.gtfs_cache import GtfsCache

class Load(CacheBase):
    """ load GTFS data into a gtfsdb
    """



    def __init__(self, force_update=False):
        super(Load, self).__init__(section='gtfs')

        # step 1: config
        feeds = self.config.get_json('feeds')

        # step 2: check the cache whether we should update or not
        reload = force_update
        if not force_update:
            if GtfsCache.check_gtfs_files_against_cache(feeds, self.cache_dir):
                reload = True

        # step 3: reload database
        if reload:
            self.load_db()


    def load_db(self):
        ''' insert
        '''
        

def main():
    #import pdb; pdb.set_trace()
    Load(force_update=object_utils.is_force_update())

if __name__ == '__main__':
    main()
