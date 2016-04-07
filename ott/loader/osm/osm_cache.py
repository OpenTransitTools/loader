import os
import logging

from ott.utils import file_utils
from ott.loader.gtfs.base import Base


class OsmCache(Base):
    """ Does a 'smart' cache of a gtfs file
         1. it will look to see if a gtfs.zip file is in the cache, and download it and put it in the cache if not
         2. once cached, it will check to see that the file in the cache is the most up to date data...
    """
    url = None
    file_name = None
    file_path = None
    cache_dir = None
    cache_expire = 31

    def __init__(self, url, file_name, cache_dir=None, cache_expire=31):

        # step 1: temp dir
        tmp_dir = self.get_tmp_dir()

        # step 2: cache dir management
        self.cache_dir = self.get_cache_dir(cache_dir)
        self.cache_expire = cache_expire

        # step 3: file name
        self.file_name = file_name
        self.file_path = os.path.join(self.cache_dir, self.file_name)

        # step 4: download new osm file
        self.url = url
        tmp_path = os.path.join(tmp_dir, self.file_name)
        file_utils.wget(self.url, tmp_path)

        # step 5: check the cache whether we should update or not
        update = False
        if self.is_fresh_in_cache():
            logging.info("diff gtfs file")
            diff = Diff(self.file_path, tmp_path)
            if diff.is_different():
                update = True
        else:
            update = True

        # step 6: mv old file to backup then mv new file in tmp dir to cache
        if update:
            logging.info("move to cache")
            file_utils.bkup(self.file_path)
            os.rename(tmp_path, self.file_path)


def main():
    pass

if __name__ == '__main__':
    main()
