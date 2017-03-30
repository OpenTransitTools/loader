from ott.utils import object_utils
from ott.utils import db_utils
from ott.utils.cache_base import CacheBase

from sqlalchemy.ext.automap import automap_base
from sqlalchemy.schema import MetaData
from sqlalchemy.orm import Session
from sqlalchemy import Table
from sqlalchemy import create_engine


import logging
log = logging.getLogger(__file__)


class Landmarks(CacheBase):
    """ export Transit data from 
    """
    db_url = None

    def __init__(self):
        self.db_url = self.config.get('transit_url', section='db', def_val='postgresql+psycopg2://127.0.0.1:5432/ott')
        self.schema = self.config.get('transit_schema', section='db', def_val="TRIMET")

    def x(self):
        # engine, suppose it has two tables 'user' and 'address' set up
        engine = create_engine(self.db_url)

        # reflect the tables
        meta = MetaData(schema=self.schema)
        Base = automap_base(bind=engine, metadata=meta)
        Base.prepare(engine, reflect=True)
        #print Base.classes.keys()

        #a = Table('agency', meta, autoload=True, autoload_with=engine)
        #print a.all()
        Agency = Base.classes.agency

        session = Session(engine)
        for a in session.query(Agency).all():
            print a.__dict__

    @classmethod
    def export(cls):
        l = Landmarks()
        l.x()
