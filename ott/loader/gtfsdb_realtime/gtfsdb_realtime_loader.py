from ott.utils import gtfs_utils
from ott.utils import object_utils
from ott.utils import db_utils
from ott.utils import file_utils
from ott.utils.cache_base import CacheBase

from ott.gtfsdb_realtime import loader


import logging
log = logging.getLogger(__file__)


class GtfsdbRealtimeLoader(CacheBase):
    """
    load GTFS Realtime data into a companion gtfsdb database
    TODO: do we need to abstract some common gtfsdb and gtfs-realtime methods into a new parent class? IoC?
    """
    feeds = []
    db_url = None

    def __init__(self):
        super(GtfsdbRealtimeLoader, self).__init__(section='gtfs_realtime')

        self.feeds = gtfs_utils.get_realtime_feed_from_config(self.config)
        self.db_url = self.config.get('url', section='db', def_val='postgresql+psycopg2://ott@127.0.0.1:5432/ott')

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

    def load_all(self, force_update=False):
        pass

    @classmethod
    def load(cls):
        """ run the gtfsdb realtime loader against all the specified feeds from config/app.ini
            NOTE: this is effectively a main method for updating all the realtime feeds
        """
        db = GtfsdbRealtimeLoader()
        db.load_all(force_update=object_utils.is_force_update())
