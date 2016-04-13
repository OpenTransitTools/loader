import os
import logging

from ott.utils import file_utils
from .osm_cache import OsmCache


class GeoFabrikCache(OsmCache):
    """ Does a 'smart' cache of a gtfs file
         1. it will look to see if a gtfs.zip file is in the cache, and download it and put it in the cache if not
         2. once cached, it will check to see that the file in the cache is the most up to date data...
    """
    pbf_url = "http://download.geofabrik.de/north-america/us-west-latest.osm.pbf"
    meta_url = "http://download.geofabrik.de/north-america/us-west.html"

    def __init__(self, name, force_download=False):
        super(GeoFabrikCache, self).__init__(name, pbf_url=self.meta_url, meta_url=self.meta_url, force_download=force_download)

def main():
    #import pdb; pdb.set_trace()
    g = GeoFabrikCache(name="or-wa")

if __name__ == '__main__':
    main()
