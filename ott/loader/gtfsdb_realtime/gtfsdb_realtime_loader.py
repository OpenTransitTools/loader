from ott.utils import gtfs_utils
from ott.utils import object_utils
from ott.utils import db_utils
from ott.utils import file_utils
from ott.loader.gtfs.gtfs_cache import GtfsCache
from gtfsdb.api import database_load

import os
import logging
log = logging.getLogger(__file__)


class GtfsdbRealtimeLoader(object):
    """
    load GTFS Realtime data into a companion gtfsdb database
    """
    feeds = []
    db_url = None

    def __init__(self):
        super(GtfsdbRealtimeLoader, self).__init__(section='gtfs')

        self.feeds = gtfs_utils.get_feeds_from_config(self.config)
        self.db_url = self.config.get('url', section='db', def_val='postgresql+psycopg2://ott@127.0.0.1:5432/ott')
        self.is_geospatial = self.config.get_bool('is_geospatial', section='db')

    def get_feed_name(self, feed):
        """  """
        db_schema_name = gtfs_utils.get_schema_name_from_feed(feed)
        return db_schema_name

    def get_feed_path(self, feed):
        """  """
        feed_path = os.path.join(self.cache_dir, feed['name'])
        return feed_path

    def load_feed(self, feed):
        """
        insert a GTFS feed into configured db
        """
        ret_val = True

        # step 1: get cached feed path and feed name (see 'feeds' in config/app.ini)
        feed_path = self.get_feed_path(feed)
        feed_name = self.get_feed_name(feed)

        # step 2: make args for gtfsdb
        kwargs = {}
        kwargs['url'] = self.db_url
        if "sqlite:" not in self.db_url:
            kwargs['is_geospatial'] = self.is_geospatial
            kwargs['schema'] = feed_name

        # step 3: load this feed into gtfsdb
        log.info("loading {} ({}) into gtfsdb {}".format(feed_name, feed_path, self.db_url))
        try:
            database_load(feed_path, **kwargs)
        except Exception, e:
            ret_val = False
            file_utils.mv(feed_path, feed_path + self.err_ext)
            log.error("DATABASE ERROR : {}".format(e))
        return ret_val

    def check_db(self, force_update=False):
        """
        check the local cache of GTFS feeds, and decide whether we should reload a given feed based on feed info
        """
        # step 1: loop thru all our feeds
        purged = False
        for f in self.feeds:
            reload = False

            # step 2: see if the GTFS cache has a newer feed than what we have in this GTFS-DB cache
            if GtfsCache.compare_feed_against_cache(f, self.cache_dir, force_update):
                reload = True

            # step 3: okay, reload this GTFS feed into the database
            if reload or force_update:
                # step 3a: we should purge any GTFS-error files that might have been generated on the last load
                #          NOTE: we'll also check the database onthis step ... make sure it's available and ready
                if not purged:
                    db_utils.check_create_db(self.db_url, self.is_geospatial)
                    file_utils.purge(self.cache_dir, ".*" + self.err_ext)
                    purged = True

                # step 3b: load the feed into the database
                self.load_feed(f)

    @classmethod
    def load(cls):
        """ run the gtfsdb loader against all the specified feeds from config/app.ini
            NOTE: this is effectively a main method for downloading, caching and db loading new/updated gtfs feeds
        """
        db = GtfsdbLoader()
        db.check_db(force_update=object_utils.is_force_update())
