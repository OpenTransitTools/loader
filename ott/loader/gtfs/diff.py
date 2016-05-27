import os
import inspect
import logging

from ott.utils import file_utils
from ott.utils.cache_base import CacheBase
from ott.loader.gtfs.info import Info

class Diff(CacheBase):
    """ Diff Two Gtfs Zip Files, looking at feed_info.txt & calendar_date.txt file to see differences between them
    """
    old_info = None
    new_info = None
    old_gtfs_zip = None
    new_gtfs_zip = None

    def __init__(self, old_gtfs_zip, new_gtfs_zip):
        # step 1: set up some dirs
        self.old_gtfs_zip = old_gtfs_zip
        self.new_gtfs_zip = new_gtfs_zip

        # step 2: make our  stuff
        self.old_info = Info(self.old_gtfs_zip, "old_")
        self.new_info = Info(self.new_gtfs_zip, "new_")

    def is_different(self):
        ''' compare feed_info.txt and calendar_dates.txt between two zips
        '''
        feed_info_diff = file_utils.diff_files(self.old_info.unzip_feed_info_txt(), self.new_info.unzip_feed_info_txt())
        if feed_info_diff:
            logging.info("feed_info.txt files are different")
        calendar_dates_diff = file_utils.diff_files(self.old_info.unzip_calendar_dates_txt(), self.new_info.unzip_calendar_dates_txt())
        if calendar_dates_diff:
            logging.info("calender_dates.txt files are different")
        calendar_diff = file_utils.diff_files(self.old_info.unzip_calendar_txt(), self.new_info.unzip_calendar_txt())
        if calendar_diff:
            logging.info("calender.txt files are different")
        return feed_info_diff or calendar_diff or calendar_dates_diff
