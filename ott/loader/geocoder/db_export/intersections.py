""" NOTE: below there are queries that are specific to TriMet's geo database (PostGIS), and a street intersection table.
"""
import os
from ott.utils import file_utils
from sqlalchemy.orm import Session
from .db_exporter import DbExporter

import logging
log = logging.getLogger(__file__)


class Intersections(DbExporter):
    """ export Transit data from
    """
    def __init__(self):
        super(Intersections, self).__init__()
        csv_output = self.config.get('intersections_csv', section='geocoder', def_val="intersections.csv")
        self.file_path = os.path.join(self.cache_dir, csv_output)

    def query_and_output(self):
        IntersectionsOrm = self.get_table_orm('intersections')
        session = Session(self.engine)
        fp = open(self.file_path, 'w')
        csv_writer = file_utils.make_csv_writer(fp, ['name', 'address', 'lon', 'lat', 'layer_id'])

        type_ids = LANDMARK_TYPES.keys()
        for i, a in enumerate(session.query(IntersectionsOrm).all()):
            if a.type in type_ids:
                row = {'name':a.name, 'address':a.address, 'lon':a.lon, 'lat':a.lat, 'layer_id':LANDMARK_TYPES[a.type]}
                csv_writer.writerow(row)

    @classmethod
    def export(cls):
        l = Intersections()
        l.query_and_output()

