
def run_all():
    ''' will load OTP and gtfsdb
        does the following:
          1. update GTFS feeds in cache
          2. update OSM data
          3. load gtfsdb
          4. build OTP graph

    '''
    force_update=object_utils.is_force_update()

    cache = GtfsCache()
    cache.check_cached_feeds(force_update=force_update)

def main():
    #import pdb; pdb.set_trace()
    run_all()

if __name__ == '__main__':
    main()
