""" NOTE: below there are queries that are specific to TriMet's geo database (PostGIS), and a landmarks table.
"""
import os
from ott.utils import file_utils
from sqlalchemy.orm import Session
from .db_exporter import DbExporter

import logging
log = logging.getLogger(__file__)


# map TriMet landmark types to something more readable / relatable
LANDMARK_TYPES = {}
LANDMARK_TYPES[2] = 'airport'  # maybe we do this if we need the PDX alias
LANDMARK_TYPES[9] = "transportation"
LANDMARK_TYPES[7] = 'station'
LANDMARK_TYPES[10] = 'pr'
LANDMARK_TYPES[14] = 'tc'
LANDMARK_TYPES[17] = 'br'
LANDMARK_TYPES[15] = 'facility'
LANDMARK_TYPES[16] = 'fare_outlet'
LANDMARK_TYPES[26] = 'tvm'

LANDMARK_TYPES[1]  = "activity_center"
LANDMARK_TYPES[22] = "community_center"
LANDMARK_TYPES[23] = "town_center"
LANDMARK_TYPES[18] = "social_service"
LANDMARK_TYPES[6]  = "library"
LANDMARK_TYPES[3]  = "city_hall"
LANDMARK_TYPES[25] = "government_agency"
LANDMARK_TYPES[11] = "post_office"
LANDMARK_TYPES[4]  = "fire_station"
LANDMARK_TYPES[20] = "correctional_facility"

LANDMARK_TYPES[5]  = "hospital"
LANDMARK_TYPES[24] = "medical_clinic"
LANDMARK_TYPES[19] = "major_employer"

LANDMARK_TYPES[8]  = "museum"
LANDMARK_TYPES[12] = "school"
LANDMARK_TYPES[13] = "shopping"
LANDMARK_TYPES[21] = "hotel_motel"


class Landmarks(DbExporter):
    """ export Transit data from
    """
    def __init__(self):
        super(Landmarks, self).__init__()
        csv_output = self.config.get('landmarks_csv', section='geocoder', def_val="TRIMET-landmarks.csv")
        self.file_path = os.path.join(self.cache_dir, csv_output)

    def query_and_output(self):
        LandmarksOrm = self.get_table_orm('landmark_ext')
        session = Session(self.engine)
        fp = open(self.file_path, 'wb')
        csv_writer = file_utils.make_csv_writer(fp, self.csv_columns)

        type_ids = LANDMARK_TYPES.keys()
        for i, a in enumerate(session.query(LandmarksOrm).all()):
            if a.type in type_ids:
                row = {'id': a.id, 'name': a.name, 'address': a.address, 'zipcode': a.zip_code, 'lon': a.lon, 'lat': a.lat, 'layer_id': LANDMARK_TYPES[a.type]}
                csv_writer.writerow(row)

    @classmethod
    def export(cls):
        l = Landmarks()
        l.query_and_output()
