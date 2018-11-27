from ott.utils.cache_base import CacheBase

from sqlalchemy.ext.automap import automap_base
from sqlalchemy.schema import MetaData
from sqlalchemy import create_engine
from geoalchemy2.shape import to_shape  # don't delete me, if you want the geom column to be a WKB type

import logging
log = logging.getLogger(__file__)


class DbExporter(CacheBase):
    """ export Transit data from 
    """
    csv_columns = ['id', 'name', 'address', 'zipcode', 'lon', 'lat', 'layer_id']

    def __init__(self):
        super(DbExporter, self).__init__('geocoder')
        self.db_url = self.config.get('transit_url',    section='db', def_val='postgresql+psycopg2://geoserve@localhost:5432/trimet')
        self.schema = self.config.get('transit_schema', section='db', def_val="current")

    def make_database(self):
        # engine, suppose it has two tables 'user' and 'address' set up
        self.engine = create_engine(self.db_url)

        # reflect the tables
        meta = MetaData(schema=self.schema)
        Base = automap_base(bind=self.engine, metadata=meta)
        Base.prepare(self.engine, reflect=True)
        return Base

    def get_table_orm(self, table_name):
        Base = self.make_database()
        TableOrm = Base.classes[table_name]
        #print(Base.classes.keys())
        return TableOrm

    @classmethod
    def export(cls):
        log.warn("abstract base method ... no export work being done")
        pass

    @classmethod
    def export_all(cls):
        """ will run all the xporters sub-classed off of DbExporter """

        # have to import the classes first, so reflection below picks up the inheritance chain
        from .intersections import Intersections
        from .landmarks import Landmarks

        # iterate thru all the children, and call export
        for subclass in cls.__subclasses__():
            print(subclass)
            subclass.export()
