""" NOTE: below there are queries that are specific to TriMet's geo database (PostGIS), and a street intersection table.
"""
import os

from sqlalchemy.orm import Session
from sqlalchemy import text
from geoalchemy2.shape import to_shape

from ott.utils import file_utils
from ott.utils import geo_utils
from .db_exporter import DbExporter

import logging
log = logging.getLogger(__file__)


class Intersections(DbExporter):
    """ export Transit data from
    """

    def __init__(self):
        super(Intersections, self).__init__()
        self.schema = 'prod'
        csv_output = self.config.get('intersections_csv', section='geocoder', def_val="intersections.csv")
        self.file_path = os.path.join(self.cache_dir, csv_output)

    def query_and_output(self):
        IntersectionsOrm = self.get_table_orm('geocode')
        session = Session(self.engine)
        fp = open(self.file_path, 'w')
        csv_writer = file_utils.make_csv_writer(fp, self.csv_columns)

        intersections = session.query(IntersectionsOrm).filter(text('type = 2')).all()
        for i, a in enumerate(intersections):
            x = to_shape(a.geom).x
            y = to_shape(a.geom).y
            lon, lat = geo_utils.to_lon_lat(x, y)
            row = {'name':a.address, 'lon':lon, 'lat':lat, 'layer_id':'intersections'}
            csv_writer.writerow(row)

    @classmethod
    def export(cls):
        l = Intersections()
        l.query_and_output()
