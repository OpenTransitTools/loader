import logging
import logging.config
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__file__)

from ott.utils import object_utils

from ott.loader.gtfs.gtfs_cache import GtfsCache
from ott.loader.osm.osm_cache import OsmCache
from ott.loader.otp.graph.build import Build
from ott.loader.gtfsdb.load import Load


def load_all():
    ''' will load OTP and gtfsdb

        does the following:
          1.  update GTFS feeds in cache

          2.  update OSM data

          3a. load gtfsdb
          3b. export gtfsdb to production

          4a. build OTP graph
          4b. test OTP graph
          4c. deploy graphs that pass tests to production servers
    '''
    force_update=object_utils.is_force_update()

    log.info("step 1: cache latest gtfs feeds")
    gtfs = GtfsCache()
    gtfs.check_cached_feeds(force_update=force_update)

    log.info("step 2: cache latest osm data")
    osm = OsmCache()
    osm.check_cached_osm(force_update=force_update)

    log.info("step 3: load gtfsdb")
    db = Load()
    db.check_db(force_update=force_update)

    log.info("step 4: load otp (build new graph)")
    otp = Build()
    otp.build_and_test_graphs(force_update=force_update)


def deploy_all():
    ''' load (production) new database extracts and deploy new otp graphs

        does the following:
          1. will load any postgres exports into local (production) db
          2. enable new OTP graph

    '''
    print "@TODO @TODO @TODO @TODO @TODO"


def main():
    #import pdb; pdb.set_trace()
    load_all()
    deploy_all()

if __name__ == '__main__':
    main()
