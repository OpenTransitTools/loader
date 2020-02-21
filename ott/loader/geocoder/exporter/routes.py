import os
from ott.utils import file_utils
from ott.loader.gtfs.files import Files
from ott.utils.cache_base import CacheBase

import logging
log = logging.getLogger(__file__)


class Routes(CacheBase):
    """
    export routes data from gtfs data
    """
    def __init__(self, lon="-122.5", lat="45.5"):
        super(Routes, self).__init__(section='geocoder')
        self.gtfs_file = self.config.get('gtfs_zip', def_val="TRIMET.zip")
        self.routes_path = self.get_gtfs_routes_txt(self.gtfs_file)
        self.csv_file = self.config.get('routes_csv', def_val="TRIMET-routes.csv")
        self.csv_path = os.path.join(self.cache_dir, self.csv_file)
        self.lon = lon
        self.lat = lat

    def make_pelias_csv(self, layer='routes', source='transit'):
        # step 1: read routes.txt (gtfs csv file) and format into route record
        routes = file_utils.make_csv_reader(self.routes_path)

        rlist = []
        for r in routes:
            id = self.make_id(r, type=layer)
            nm = self.make_route_name(r)
            rec = {'id': id, 'name': nm, 'lon': self.lon, 'lat': self.lat, 'layer_id': layer, 'source': source}
            rlist.append(rec)

        # step 2: create/open Pelias .csv file

        # step 3: write the route records to the Pelias .csv file
        for r in rlist:
            print(r)

    @classmethod
    def make_id(cls, route_rec, agency=None, type="routes"):
        route = route_rec.get('route_id')
        if agency is None:
            agency = route_rec.get('agency_id')
        ret_val = "{}::{}::{}".format(route, agency, type)
        return ret_val

    @classmethod
    def make_route_name(cls, route_rec, sep="-", def_val=""):
        ret_val = def_val

        rsn = route_rec.get('route_short_name')
        rln = route_rec.get('route_long_name')
        rid = route_rec.get('route_id')

        if rsn and rln:
            ret_val = "{}{}{}".format(rsn, sep, rln)
        elif rsn:
            ret_val = rsn
        elif rln:
            ret_val = rln
        elif rid:
            ret_val = rid

        return ret_val

    @classmethod
    def get_gtfs_routes_txt(cls, gtfs_file, file_name="routes.txt"):
        f = Files(gtfs_file)
        path = f.export(file_name)
        return path

    @classmethod
    def export(cls):
        r = Routes()
        r.make_pelias_csv()

