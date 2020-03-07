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

    def __init__(self, db_url=None):
        super(GtfsdbRealtimeLoader, self).__init__(section='gtfs_realtime')
        self.feeds = gtfs_utils.get_realtime_feed_from_config(self.config)
        if db_url and db_url not in ('def', 'default', 'local'):
            self.db_url = db_url
        else:
            self.db_url = self.config.get('url', section='db', def_val='postgresql+psycopg2://ott@127.0.0.1:5432/ott')

    def load_all(self, api_key=None, is_geospatial=True, create_db=False):
        from ott.gtfsdb_realtime import loader
        for f in self.feeds:
            if api_key:
                f['api_key'] = api_key
            loader.load_feeds_via_config(f, self.db_url, is_geospatial, create_db)

    @classmethod
    def load(cls):
        """
        run the gtfsdb realtime loader against all the specified feeds from config/app.ini
        NOTE: this is effectively a main method for updating all the realtime feeds
        """
        # import pdb; pdb.set_trace()
        args = cls.make_cmdline()
        rt = GtfsdbRealtimeLoader()
        rt.load_all(args.api_key, args.is_geospatial, args.create)

    @classmethod
    def make_cmdline(cls):
        """ make a command line with options for app keys and creating new dbs, etc... """
        from ott.utils.parse.cmdline.gtfs_cmdline import gtfs_rt_parser
        args = gtfs_rt_parser(exe_name='bin/gtfsrt_load', do_parse=True)
        return args
