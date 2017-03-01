from ott.utils import object_utils

from ott.loader.gtfs.gtfs_cache import GtfsCache
from ott.loader.osm.osm_cache import OsmCache
from ott.loader.otp.graph.otp_deployer import OtpDeployer
from ott.loader.otp.graph.otp_builder import OtpBuilder
from ott.loader.gtfsdb.gtfsdb_loader import GtfsdbLoader
from ott.loader.sum.sum_cache import SumCache
from ott.loader.solr.solr_loader import SolrLoader

import logging
# logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__file__)


def load_data():
    """ just download data

        does the following:
          1.  update GTFS feeds in cache
          2.  update OSM data in cache
          3.  update SUM data in cache
    """
    force_update=object_utils.is_force_update()

    log.info("step 1: cache latest gtfs feeds")
    gtfs = GtfsCache()
    gtfs.check_cached_feeds(force_update=force_update)

    log.info("step 2: cache latest osm data")
    osm = OsmCache()
    osm.check_cached_osm(force_update=force_update)

    log.info("step 3: download SUM data (BIKETOWN)")
    sum_update = SumCache.load


def load_all():
    """ will load OTP and gtfsdb

          3a. load gtfsdb
          3b. export gtfsdb to production

          4a. build OTP graph
          4b. test OTP graph
          4c. deploy graphs that pass tests to production servers

          5. load SOLR with cached datad
    """
    force_update=object_utils.is_force_update()

    load_data()

    log.info("step 4: load gtfsdb")
    db = GtfsdbLoader()
    db.check_db(force_update=force_update)

    log.info("step 5: load otp (build new graph)")
    otp = OtpBuilder(force_update=force_update)
    otp.build_and_test_graphs(force_update=force_update)

    log.info("step 6: load various data layers into SOLR")
    solr_load = SolrLoader.load()

    export_all()


def export_all():
    """ @todo: maybe export Graphs and the like
    """
    GtfsdbLoader.dump()

def deploy_all():
    """ load (production) new database extracts and deploy new otp graphs

        does the following:
          1. will  any postgres exports into local (production) db
          2. enable new OTP graph

    """
    log.info("step 1: load any new gtfsdb snapshot")
    GtfsdbLoader.restore()

    log.info("step 2: load any new OSM database snapshot")
    osm = OsmCache()
    #osm.deploy_db_snapshot()

    log.info("step 3: deploy otp graph")
    otp = OtpDeployer()
    otp.deploy()
    #otp.deploy_graphs()

    log.info("step 4: deploy SOLR updates")
    #solr_load = SolrLoader.load


def load_and_deploy():
    log.info("***load and build things, then deploy them***")
    load_all()
    deploy_all()




