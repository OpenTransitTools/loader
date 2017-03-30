from ott.utils import object_utils
from ott.utils import db_utils
from ott.utils.cache_base import CacheBase

from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine

import os
import logging
log = logging.getLogger(__file__)


class Landmarks(CacheBase):
    """ export Transit data from 
    """
    db_url = None

    def __init__(self):
        self.db_url = self.config.get('transit_url', section='db', def_val='postgresql+psycopg2://ott@127.0.0.1:5432/ott')

    def x(self):

        Base = automap_base()

        # engine, suppose it has two tables 'user' and 'address' set up
        engine = create_engine(self.db_url);

        # reflect the tables
        Base.prepare(engine, reflect=True)

        Address = Base.classes.address

        session = Session(engine)

        # rudimentary relationships are produced
        session.add(Address(email_address="foo@bar.com", user=User(name="foo")))
        session.commit()

        # collection-based relationships are by default named
        # "<classname>_collection"
        print (u1.address_collection)


    @classmethod
    def export(cls):
        l = Landmarks()
        l.x()
