import sys

from ott.utils.cache_base import CacheBase
from ott.loader.gtfs.cache import Cache

class Load(CacheBase):
    """ load GTFS data into a gtfsdb
    """
    gtfs_zip_files  = None
    cache_dir = None

    def __init__(self, config=None, gtfs_zip_files=Cache.get_gtfs_feeds(), force_reload=False):
        reload = force_reload
        self.gtfs_zip_files = gtfs_zip_files

        if Cache.check_gtfs_files_against_cache(self.gtfs_zip_files, self.cache_dir):
            reload_= True
        if reload:
            print "TODO ... implement load of gtfsdb"
            pass

def main(argv=sys.argv):
    Load()

if __name__ == '__main__':
    main()
