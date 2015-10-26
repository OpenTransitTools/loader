
import os
import sys
import inspect
import logging

from ott.loader.gtfs.cache import Cache

class Load(object):
    """ load GTFS data into a gtfsdb
    """
    this_module_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

    local_cache_dir = None
    gtfs_zip_files  = None

    def __init__(self, config=None, gtfs_zip_files=Cache.get_gtfs_feeds(), force_reload=False):
        reload = force_reload
        self.gtfs_zip_files = gtfs_zip_files
        self.local_cache_dir = Cache.local_get_cache_dir(self.this_module_dir)
        if Cache.check_gtfs_files_against_cache(self.gtfs_zip_files, self.local_cache_dir):
            reload_= True
        if reload:
            pass

def main(argv=sys.argv):
    Load()

if __name__ == '__main__':
    main()
