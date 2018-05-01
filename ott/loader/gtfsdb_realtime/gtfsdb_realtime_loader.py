from ott.utils import gtfs_utils
from ott.utils import object_utils
from ott.utils.cache_base import CacheBase

from ott.gtfsdb_realtime import loader

import logging
logging.basicConfig()
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

    def load_all(self, app_id=None, is_geospatial=True, create_db=False):
        for f in self.feeds:
            if app_id: f.app_id = app_id
            loader.load_feeds_via_config(f, self.db_url, is_geospatial, create_db)

    @classmethod
    def load(cls):
        """ run the gtfsdb realtime loader against all the specified feeds from config/app.ini
            NOTE: this is effectively a main method for updating all the realtime feeds
        """
        # import pdb; pdb.set_trace()
        rt = GtfsdbRealtimeLoader()
        rt.load_all()
