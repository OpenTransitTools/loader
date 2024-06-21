import os
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
        if db_url and db_url not in ('x', 'def', 'default', 'local'):
            self.db_url = db_url
        else:
            self.db_url = self.config.get('url', section='db', def_val='postgresql+psycopg2://ott@127.0.0.1:5432/ott')

    def load_all(self, agency, is_geospatial=True, create_db=False, vehicles_only=False):
        # import pdb; pdb.set_trace()
        feed = gtfs_utils.get_realtime_feed_from_config(self.config, agency)
        if isinstance(feed, list):
            print("Make sure agency is one of these: ", gtfs_utils.get_agency_names_from_feeds_list(feed))
            return

        do_trips = not vehicles_only
        do_alerts = not vehicles_only
        do_vehicles = True
        from ott.gtfsdb_realtime import loader
        loader.load_feeds_via_config(feed, self.db_url, do_trips, do_alerts, do_vehicles, is_geospatial, create_db)

    @classmethod
    def load(cls):
        """
        run the gtfsdb realtime loader against all the specified feeds from config/app.ini
        NOTE: this is effectively a main method for updating all the realtime feeds
        """
        from ott.utils.parse.cmdline.gtfs_cmdline import gtfs_rt_parser
        args = gtfs_rt_parser(exe_name='bin/gtfsrt_load')
        rt = GtfsdbRealtimeLoader()
        rt.load_all(args.agency_id, args.is_geospatial, args.create, args.vehicles_only)



    # junk
    def Xload_all(self, is_geospatial=True, create_db=False, vehicles_only=False):
        from ott.gtfsdb_realtime import loader
        for f in self.feeds:
            if api_key and len(api_key) > 3:
                f['api_key'] = api_key

            # control to do just vehicles
            do_trips = not vehicles_only
            do_alerts = not vehicles_only
            do_vehicles = True

            # load db feed
            loader.load_feeds_via_config(f, self.db_url, do_trips, do_alerts, do_vehicles, is_geospatial, create_db)

    def Yload_all(self, is_geospatial=True, create_db=False, vehicles_only=False):        
        for f in self.feeds:
            # control to do just vehicles

            # import pdb; pdb.set_trace()
            # load db feed
            pid = os.fork()
            if pid:
                pass
            else:
                from ott.gtfsdb_realtime import loader
                loader.load_feeds_via_config(f, self.db_url, do_trips, do_alerts, do_vehicles, is_geospatial, create_db)
