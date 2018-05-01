from ott.utils import gtfs_utils
from ott.utils.cache_base import CacheBase

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

    def load_all(self, api_key=None, is_geospatial=True, create_db=False):
        from ott.gtfsdb_realtime import loader
        for f in self.feeds:
            if api_key: f['api_key'] = api_key
            loader.load_feeds_via_config(f, self.db_url, is_geospatial, create_db)

    @classmethod
    def cmdline(cls):
        """ make a command line with options for app keys and creating new dbs, etc... """
        from ott.utils.parse.cmdline import db_cmdline
        from ott.utils.parse.cmdline import gtfs_cmdline
        parser = gtfs_cmdline.blank_parser('bin/gtfsdb_rt_load')
        gtfs_cmdline.api_key(parser)
        db_cmdline.create_and_clear(parser)
        db_cmdline.is_spatial(parser)
        args = parser.parse_args()
        return args

    @classmethod
    def load(cls):
        """ run the gtfsdb realtime loader against all the specified feeds from config/app.ini
            NOTE: this is effectively a main method for updating all the realtime feeds
        """
        # import pdb; pdb.set_trace()
        args = cls.cmdline()
        rt = GtfsdbRealtimeLoader()
        rt.load_all(args.api_key, args.is_geospatial, args.create)
