import os
import logging

from ott.utils import file_utils
from ott.utils.cache_base import CacheBase


class Fix(CacheBase):
    """ Diff Two Gtfs Zip Files, looking at feed_info.txt & calendar_date.txt file to see differences between them
    """
    gtfs_zip = None

    def __init__(self, gtfs_zip):
        self.gtfs_zip = gtfs_zip

    def cp(self, filter_file_names=None):
        if cp_file_name:
            pass

    def rename_agency(self, agency_name="TRIMET", cp_file_name=None):
        '''
        '''
        file_path = os.path.join(self.dir_path, self.file_prefix + file_name)
        file_utils.unzip_file(self.gtfs_path, file_path, file_name)
        if calendar_diff:
            logging.info("calender.txt files are different")
        return feed_info_diff or calendar_diff or calendar_dates_diff
