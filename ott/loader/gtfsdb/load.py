import sys

from ott.utils import config
from ott.utils.cache_base import CacheBase
from ott.loader.gtfs.cache import Cache

class Load(CacheBase):
    """ load GTFS data into a gtfsdb
    """
    gtfs_zip_files  = None

    def __init__(self, config=None, gtfs_zip_files=Cache.get_gtfs_feeds(), force_reload=False):
        reload = force_reload
        self.gtfs_zip_files = gtfs_zip_files
        if Cache.check_gtfs_files_against_cache(self.gtfs_zip_files, self.cache_dir):
            reload = True
        if reload:
            # TODO
            print "TODO ... implement load of gtfsdb"
            pass

def main(argv=sys.argv):
    #import pdb; pdb.set_trace()
    config.get_parser()
    print config.get('fff', section='BBB')
    Load()

if __name__ == '__main__':
    main()
