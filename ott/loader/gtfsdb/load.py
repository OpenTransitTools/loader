import os
from ott.utils import object_utils
from ott.utils.cache_base import CacheBase
from ott.loader.gtfs.gtfs_cache import GtfsCache

from gtfsdb.api import database_load

import logging.config
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__file__)

class Load(CacheBase):
    """ load GTFS data into a gtfsdb
    """
    feeds = []
    db_url = None
    is_geospatial = False

    def __init__(self, force_update=False):
        super(Load, self).__init__(section='gtfs')

        # step 1: config
        self.feeds  = self.config.get_json('feeds', section='gtfs')
        self.db_url = self.config.get('url', section='db')
        self.is_geospatial = self.config.get_bool('is_geospatial', section='db')

        # step 2: check the cache whether we should update or not
        reload = force_update
        if GtfsCache.check_gtfs_files_against_cache(self.feeds, self.cache_dir, force_update):
            reload = True

        # step 3: reload database
        if reload:
            self.load_db()

    def load_db(self):
        ''' insert feeds into configured db (see config/app.ini)
        '''
        for f in self.feeds:
            # get cached feed path and feed name (see 'feeds' in config/app.ini)
            feed_path = os.path.join(self.cache_dir, f['name'])
            feed_name = f['name'].rstrip(".zip")

            # make args for gtfsdb
            kwargs = {}
            kwargs['url'] = self.db_url
            if "sqlite:" not in self.db_url:
                kwargs['is_geospatial'] = self.is_geospatial
                kwargs['schema'] = feed_name

            # load this feed into gtfsdb
            log.info("loading {} ({}) into gtfsdb {}".format(feed_name, feed_path, self.db_url))
            database_load(feed_path, **kwargs)


def main():
    #import pdb; pdb.set_trace()
    Load(force_update=object_utils.is_force_update())

if __name__ == '__main__':
    main()
