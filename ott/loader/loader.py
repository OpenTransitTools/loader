from ott.utils import object_utils

from ott.osm.osm_cache import OsmCache
from ott.loader.gtfs.gtfs_cache import GtfsCache
from ott.loader.otp.graph.otp_exporter import OtpExporter
from ott.loader.otp.graph.otp_builder import OtpBuilder
from ott.loader.gtfsdb.gtfsdb_loader import GtfsdbLoader
from ott.loader.gtfsdb.gtfsdb_exporter import GtfsdbExporter
from ott.loader.gtfsdb_realtime.gtfsdb_realtime_loader import GtfsdbRealtimeLoader
from ott.loader.sum.sum_cache import SumCache
from ott.loader.solr.solr_loader import SolrLoader

import logging
log = logging.getLogger(__file__)


def download_data():
    """ just download data

        does the following:
          1.  update GTFS feeds in cache
          2.  update OSM data in cache
          3.  update SUM data in cache
    """
    force_update=object_utils.is_force_update()

    log.info("step 1: cache latest gtfs feeds")
    gtfs = GtfsCache()
    updated_feeds = gtfs.check_cached_feeds(force_update=force_update)
    # NOTE: to do item could be to check updated_feeds (list of feed names) for certain agency names, and selectively force update
    if updated_feeds and len(updated_feeds) > 0:
        force_update = True

    log.info("step 2: cache latest osm data")
    updated_osm = OsmCache.update(force_update=force_update)
    if updated_osm:
        force_update = True

    log.info("step 3: download SUM data (BIKETOWN)")
    sum_update = SumCache.load

    return force_update


def load_all():
    """ will load OTP and gtfsdb

          load gtfsdb
          pg_dump an export file for gtfsdb

          build OTP graph
          test OTP graph

          load SOLR with cached data
    """
    force_update=object_utils.is_force_update()

    # steps 1 - 3: download data (see above)
    # import pdb; pdb.set_trace()
    download_data()

    log.info("step 4: load gtfsdb")
    db = GtfsdbLoader()
    GtfsdbExporter.scp()
    db.check_db(force_update=force_update)

    log.info("step 5: load gtfsdb_realtime db")
    rt = GtfsdbRealtimeLoader()
    rt.load_all(is_geospatial=True, create_db=True)

    log.info("step 6: load otp (build new graph)")
    otp = OtpBuilder(force_update=force_update)
    otp.build_and_test_graphs(force_update=force_update)

    log.info("step 7: load various data layers into SOLR")
    solr_load = SolrLoader.load()


def export_all():
    """
    """
    log.info("step 1: scp any gtfsdb pg_dump files created in the load_all() call ")
    GtfsdbExporter.scp()

    log.info("step 2: load any new OSM database snapshot")
    osm = OsmCache()
    #osm.deploy_db_snapshot()

    log.info("step 3: export otp graph")
    OtpExporter.export()

    log.info("step 4: export... SOLR updates")
    #solr_load = SolrLoader.load


def load_and_export():
    log.info("***load and build things, then export them and scp' them to production servers ***")
    load_all()
    export_all()


def restore_production():
    """ load (production) new database extracts and deploy new otp graphs

        does the following:
          1. will  any postgres exports into local (production) db
          2. enable new OTP graph

    """
    log.info("step 1: restore gtfsdb from export")
    GtfsdbLoader.restore()

    log.info("step 2: load any new OSM database snapshot")
    osm = OsmCache()
    #osm.restore_db_snapshots()

    log.info("step 4: export... SOLR updates")
    #solr_load = SolrLoader.load
