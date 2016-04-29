from ott.utils import object_utils
from ott.utils.cache_base import CacheBase
from ott.loader.gtfs.gtfs_cache import GtfsCache

class Load(CacheBase):
    """ load GTFS data into a gtfsdb
    """
    feeds = []
    url = None
    is_geospatial = False

    def __init__(self, force_update=False):
        super(Load, self).__init__(section='gtfs')

        # step 1: config
        self.feeds  = self.config.get_json('feeds')
        self.url    = self.config.get_json('url', section='db')
        self.is_geospatial = self.config.get_json('is_geospatial',  section='db')

        # step 2: check the cache whether we should update or not
        reload = force_update
        if not force_update:
            if GtfsCache.check_gtfs_files_against_cache(self.feeds, self.cache_dir):
                reload = True

        # step 3: reload database
        if reload:
            self.load_db()


    def load_db(self):
        ''' insert
        '''
        for f in self.feeds:
            print f


def main():
    #import pdb; pdb.set_trace()
    Load(force_update=object_utils.is_force_update())

if __name__ == '__main__':
    main()
