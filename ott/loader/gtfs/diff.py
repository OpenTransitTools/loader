import os
import inspect
import logging

from ott.utils import file_utils
from ott.loader.gtfs.base import Base
from ott.loader.gtfs.info import Info

class Diff(Base):
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

        # step 2: make tmp dir and cd into it
        self.tmp_dir = self.get_tmp_dir()
        file_utils.cd(self.tmp_dir)

        # step 3: unzip some stuff
        self.old_info = Info(self.old_gtfs_zip, "old_")
        self.new_info = Info(self.new_gtfs_zip, "new_")

    def is_different(self):
        ''' compare feed_info.txt and calendar_dates.txt between two zips
        '''
        feed_info_diff = file_utils.diff_files(self.old_info.feed_info_file, self.new_info.feed_info_file)
        if feed_info_diff:
            logging.info("feed_info.txt files are different")
        calendar_dates_diff  = file_utils.diff_files(self.old_info.calendar_dates_file, self.new_info.calendar_dates_file)
        if calendar_dates_diff:
            logging.info("calender_dates.txt files are different")
        calendar_diff  = file_utils.diff_files(self.old_info.calendar_file, self.new_info.calendar_file)
        if calendar_diff:
            logging.info("calender.txt files are different")
        return feed_info_diff or calendar_diff or calendar_dates_diff
