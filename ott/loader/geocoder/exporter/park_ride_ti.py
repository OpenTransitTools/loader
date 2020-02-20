"""
NOTE: below there are queries that are specific to TriMet's geo database (PostGIS), and a landmarks table.
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
        # TODO

    def query_and_output(self, clz=ParkRideTi):
        LandmarksOrm = self.get_table_orm('landmark_ext')
        session = Session(self.engine)
        # TODO

    @classmethod
    def export(cls):
        l = ParkRideExporter()
        l.query_and_output()
