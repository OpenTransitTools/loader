import sys

from ott.utils.cache_base import CacheBase
from ott.loader.gtfs.cache import Cache

class Load(CacheBase):
    """ load GTFS data into a gtfsdb
    """
    gtfs_zip_files  = None

    def __init__(self, config=None, force_reload=False):
        super(Load, self).__init__(section='gtfs')
        reload = force_reload

        feeds = self.config.get_json('feeds')
        if Cache.check_gtfs_files_against_cache(feeds, self.cache_dir):
            reload = True
        if reload:
            # TODO
            print "TODO ... implement load of gtfsdb"

def main(argv=sys.argv):
    #import pdb; pdb.set_trace()
    Load()

if __name__ == '__main__':
    main()
