""" NOTE: below there are queries that are specific to TriMet's geo database (PostGIS), and a landmarks table.
"""
import os
from ott.utils import file_utils
from ott.utils.ws.otp_ti_base import OtpTiBase
from sqlalchemy.orm import Session
from .db_exporter import DbExporter

import logging
log = logging.getLogger(__file__)


class ParkRideTi(OtpTiBase):
    pass


class ParkRideExporter(DbExporter):
    """
    export Park & Ride data as a .json format
    """
    def __init__(self):
        super(ParkRideExporter, self).__init__()
        self.url_fmt = self.config.get('park_ride_url_fmt', section='geocoder', def_val="")
        output = self.config.get('park_ride_ti_json', section='geocoder', def_val="park_ride.json")
        self.file_path = os.path.join(self.cache_dir, output)

    def query_and_output(self, clz=ParkRideTi):
        LandmarksOrm = self.get_table_orm('landmark_ext')
        session = Session(self.engine)
        fp = open(self.file_path, 'wb')
        csv_writer = file_utils.make_csv_writer(fp, self.csv_columns)

        type_ids = LANDMARK_TYPES.keys()
        for i, a in enumerate(session.query(LandmarksOrm).all()):
            if a.type in type_ids:
                p = {'id': a.id, 'name': a.name, 'address': a.address, 'zipcode': a.zip_code, 'lon': a.lon, 'lat': a.lat}
                o = clz(p)
                csv_writer.writerow(o)

    @classmethod
    def export(cls):
        l = ParkRideExporter()
        l.query_and_output()
