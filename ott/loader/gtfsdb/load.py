
import os
import sys
import inspect
import logging

from ott.loader.gtfs.cache import Cache

class Load(object):
    """ load GTFS data into a gtfsdb
    """
    this_module_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

    cache_dir = None
    gtfs_zip_files  = None

    def __init__(self, config=None, gtfs_zip_files=Cache.get_gtfs_feeds()):
        self.gtfs_zip_files = gtfs_zip_files
        self.build_cache_dir = self.get_build_cache_dir()

def main(argv=sys.argv):
    Load()

if __name__ == '__main__':
    main()
