import os
import logging
import logging.config
log = logging.getLogger(__file__)


from ott.utils import file_utils
from ott.utils import object_utils
from ott.utils import web_utils
from ott.utils.cache_base import CacheBase

from ott.loader.gtfs.info import Info
from ott.loader.gtfs.diff import Diff


class SobiCache(CacheBase):
    """ Does a 'smart' cache of a gtfs file
         1. it will look to see if a gtfs.zip file is in the cache, and download it and put it in the cache if not
         2. once cached, it will check to see that the file in the cache is the most up to date data...
    """
    url = None
    name = None
    file_name = None
    file_path = None

    def __init__(self):
        super(SobiCache, self).__init__(section='gbfs')
        self.url = self.config.get('download_url')
        self.name = self.config.get_json('name')
        self.file_name = self.name + ".json"
        self.file_path = os.path.join(self.cache_dir, self.file_name)

    def check_feed(self, force_update=False):
        ''' download feed from url, and check it against the cache
            if newer, then replace cached feed .zip file with new version
        '''
        # step 1: check the cache whether we should update or not
        update = force_update
        if not force_update and not self.is_fresh_in_cache(self.file_path):
            update = True

        # step 2: backup then wget new feed
        if update:
            log.info("wget {} to cache {}".format(self.url, self.file_path))
            file_utils.bkup(self.file_path)
            web_utils.wget(self.url, self.file_path)


def main():
    #import pdb; pdb.set_trace()
    sobi = SobiCache()
    sobi.check_feed(force_update=object_utils.is_force_update())

if __name__ == '__main__':
    main()
