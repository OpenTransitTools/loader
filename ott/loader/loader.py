
from ott.loader.gtfs.gtfs_cache import GtfsCache
from ott.loader.osm.osm_cache import OsmCache
from ott.loader.otp.graph.build import Build

def run_all():
    ''' will load OTP and gtfsdb
        does the following:
          1. update GTFS feeds in cache
          2. update OSM data
          3. load gtfsdb
          4. build OTP graph

    '''
    force_update=object_utils.is_force_update()

    gtfs = GtfsCache()
    gtfs.check_cached_feeds(force_update=force_update)
    osm = OsmCache()
    osm.check_cached_osm(force_update=force_update)
    otp = Build()
    otp.run_graph_builder(force_update=force_update)

def main():
    #import pdb; pdb.set_trace()
    run_all()

if __name__ == '__main__':
    main()
