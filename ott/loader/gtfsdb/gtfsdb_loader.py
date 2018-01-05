from ott.utils import gtfs_utils
from ott.utils import object_utils
from ott.utils import db_utils
from ott.utils import exe_utils
from ott.utils import file_utils
from ott.utils.cache_base import CacheBase
from ott.loader.gtfs.gtfs_cache import GtfsCache
from gtfsdb.api import database_load

import os
import logging
log = logging.getLogger(__file__)


class GtfsdbLoader(CacheBase):
    """
    load GTFS data into a gtfsdb
    """
    feeds = []
    db_url = None
    is_geospatial = False
    err_ext = "-error_loading"

    def __init__(self):
        super(GtfsdbLoader, self).__init__(section='gtfs')

        self.feeds = gtfs_utils.get_feeds_from_config(self.config)
        self.db_url = self.config.get('url', section='db', def_val='postgresql+psycopg2://ott@127.0.0.1:5432/ott')
        self.is_geospatial = self.config.get_bool('is_geospatial', section='db')

    def get_feed_name(self, feed):
        """ """
        db_schema_name = gtfs_utils.get_schema_name_from_feed(feed)
        return db_schema_name

    def get_feed_path(self, feed):
        """  """
        feed_path = os.path.join(self.cache_dir, feed['name'])
        return feed_path

    def get_dump_path(self, feed_name):
        """ get a name for the database (amoungst other systems) """
        return "{}/{}.tar".format(self.cache_dir, feed_name)

    def load_feed(self, feed):
        """ insert a GTFS feed into configured db
        """
        ret_val = True

        # step 1: get cached feed path and feed name (see 'feeds' in config/app.ini)
        feed_path = self.get_feed_path()
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
        """ check the local cache of GTFS feeds, and decide whether we should reload a given feed based on feed info
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

    def dump_feed(self, feed):
        """ run the db dumper
        """
        ret_val = True
        feed_name = ""
        try:
            feed_name = self.get_feed_name(feed)
            dump_path = self.get_dump_path(feed_name)
            dump_exe = self.config.get('dump', section='db').format(schema=feed_name, dump_file=dump_path)
            log.info(dump_exe)
            exe_utils.run_cmd(dump_exe, shell=True)
        except Exception, e:
            ret_val = False
            log.error("DB DUMP ERROR {} : {}".format(feed_name, e))
        return ret_val

    def restore_feed(self, feed):
        """ run the db restore
        """
        ret_val = True
        feed_name = ""
        try:
            feed_name = self.get_feed_name(feed)
            dump_path = self.get_dump_path(feed_name)
            restore_exe = self.config.get('restore', section='db').format(schema=feed_name, dump_file=dump_path)
            log.info(restore_exe)
            exe_utils.run_cmd(restore_exe, shell=True)
        except Exception, e:
            ret_val = False
            log.error("DB RESTORE ERROR {} : {}".format(feed_name, e))
        return ret_val

    @classmethod
    def load(cls):
        """ run the gtfsdb loader against all the specified feeds from config/app.ini
            NOTE: this is effectively a main method for downloading, caching and db loading new/updated gtfs feeds
        """
        db = GtfsdbLoader()
        db.check_db(force_update=object_utils.is_force_update())

    @classmethod
    def dump(cls):
        """ export """
        db = GtfsdbLoader()

        # step 1: loop thru all our feeds
        for f in db.feeds:
            db.dump_feed(f)
            # step 2: check date on last export file vs. date of GTFS feed
            # step 3: when export is either older than feed or missing entirely, create a new export and then scp it

    @classmethod
    def restore(cls):
        """ export """

        # step 1: loop thru all our feeds
        db = GtfsdbLoader()
        for f in db.feeds:
            db.restore_feed(f)
            # step 2: check date on last export file vs. date of GTFS feed
            # step 3: when export is either older than feed or missing entirely, create a new export and then scp it
