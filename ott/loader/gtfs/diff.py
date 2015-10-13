import os
import inspect
import logging

from ott.loader.gtfs import utils
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
        os.chdir(self.tmp_dir)

        # step 3: unzip some stuff
        self.old_info = Info(self.old_gtfs_zip, "old_")
        self.new_info = Info(self.new_gtfs_zip, "new_")

    def is_different(self):
        ''' compare feed_info.txt and calendar_dates.txt between two zips
            TODO: compare calendar.txt eventually
        '''
        info_diff = utils.diff_files(self.old_info.info_file, self.new_info.info_file)
        if info_diff:
            logging.info("feed_info.txt files are different")
        cal_diff  = utils.diff_files(self.old_info.calendar_dates_file, self.new_info.calendar_dates_file)
        if cal_diff:
            logging.info("calender_dates.txt files are different")
        return info_diff or cal_diff


def main():
    #import pdb; pdb.set_trace()
    this_module_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    this_module_dir = os.path.join(this_module_dir, "tests")
    gtfsA = os.path.join(this_module_dir, "gtfsA.zip")
    gtfsB = os.path.join(this_module_dir, "gtfsB.zip")
    diff = Diff(gtfsA, gtfsB)
    diff.is_different()
    print diff.new_info.get_feed_info()
    print diff.new_info.get_feed_version()
    print diff.new_info.get_feed_date_range()
    print diff.new_info.get_days_since_stats()
    print diff.new_info.is_gtfs_out_of_date()

if __name__ == '__main__':
    main()
