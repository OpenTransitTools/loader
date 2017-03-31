""" NOTE: below there are queries that are specific to TriMet's geo database (PostGIS), and a landmarks table.
"""
import os

from ott.utils import file_utils
from ott.utils.cache_base import CacheBase

from sqlalchemy.ext.automap import automap_base
from sqlalchemy.schema import MetaData
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from geoalchemy2.shape import to_shape  # don't delete me, if you want the geom column to be a WKB type



import logging
log = logging.getLogger(__file__)


types = {}
types[7] = 'station'
types[10] = 'pr'
types[14] = 'tc'
types[15] = 'facility'
types[16] = 'fare_outlet'
types[26] = 'tvm'


class Landmarks(CacheBase):
    """ export Transit data from 
    """
    db_url = None

    def __init__(self):
        #self.db_url = self.config.get('transit_url', section='db', def_val='postgresql+psycopg2://127.0.0.1:5432/ott')
        #self.schema = self.config.get('transit_schema', section='db', def_val="TRIMET")
        self.db_url = self.config.get('transit_url',    section='db', def_val='postgresql+psycopg2://geoserve@maps6:5432/trimet')
        self.schema = self.config.get('transit_schema', section='db', def_val="current")
        csv_output = self.config.get('landmarks_csv', section='geocoder', def_val="TRIMET-landmarks.csv")
        self.file_path = os.path.join(self.cache_dir, csv_output)

    def query_and_output(self):
        # engine, suppose it has two tables 'user' and 'address' set up
        engine = create_engine(self.db_url)

        # reflect the tables
        meta = MetaData(schema=self.schema)
        Base = automap_base(bind=engine, metadata=meta)
        Base.prepare(engine, reflect=True)
        #print Base.classes.keys()

        LandmarksDao = Base.classes.landmark_ext
        session = Session(engine)

        fp = open(self.file_path, 'w')
        csv_writer = file_utils.make_csv_writer(fp, ['name', 'address', 'lon', 'lat', 'layer_id'])

        type_ids = types.keys()
        for i, a in enumerate(session.query(LandmarksDao).all()):
            if a.type in type_ids:
                row = {'name':a.name, 'address':a.address, 'lon':a.lon, 'lat':a.lat, 'layer_id':types[a.type]}
                csv_writer.writerow(row)
                #print to_shape(a.geom).x
                #print to_shape(a.geom).y

    @classmethod
    def export(cls):
        l = Landmarks()
        l.query_and_output()
