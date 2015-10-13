import os

from ott.loader.gtfs import utils
from ott.loader.gtfs.base import Base

class Diff(Base):
    """ Diff Two Gtfs Zip Files, looking at feed_info.txt & calendar_date.txt file to see if it's older than
        cached gtfs.zip file
    """
    old_cal  = None
    new_cal  = None
    old_info = None
    new_info = None
    tmp_dir  = None

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
        self.unzip_calendar_and_info_files()

    def unzip_calendar_and_info_files(self, cal_file='calendar_dates.txt', info_file='feed_info.txt'):
        """ unzip a file (calendar_dates.txt by default) from our old & new gtfs.zip files
        """

        # step 1: unzip the cal_file from the old gtfs file
        self.old_cal = "old_" + cal_file
        self.old_info = "old_" + info_file
        utils.unzip_file(self.old_gtfs_zip, self.old_cal, cal_file)
        utils.unzip_file(self.old_gtfs_zip, self.old_info, info_file)

        # step 2: unzip the cal_file from the old gtfs file
        self.new_cal = "new_" + cal_file
        self.new_info = "new_" + info_file
        utils.unzip_file(self.new_gtfs_zip, self.new_cal, cal_file)
        utils.unzip_file(self.new_gtfs_zip, self.new_info, info_file)

        return self.old_cal, self.new_cal, self.old_info, self.new_info

    def is_different(self):
        ''' compare feed_info.txt and calendar_dates.txt between two zips
            NOTE: we have to handle calendar.txt too...
        '''
        info_diff = utils.diff_files(self.old_info, self.new_info)
        if info_diff:
            logging.info("feed_info.txt files are different")
        cal_diff  = utils.diff_files(self.old_cal,  self.new_cal)
        if cal_diff:
            logging.info("calender_dates.txt files are different")
        return info_diff or cal_diff

    def get_old_feed_version(self):
        start_date,end_date,id,version = self.get_feed_info(self.old_info)
        return version

    def get_new_feed_version(self):
        start_date,end_date,id,version = self.get_feed_info(self.new_info)
        return version

    def get_new_feed_dates(self):
        start_date, end_date, tday, tpos = self.get_date_range_of_calendar_dates(self.new_cal)
        return "{0} to {1}".format(start_date, end_date)


def main():
    logging.basicConfig(level=logging.INFO)
    diff = Diff("C:\\java\\DEV\\loader\\ott\\loader\\gtfs\\cache\\trimet.zip", "C:\\java\\DEV\\loader\\ott\\loader\\gtfs\\cache\\trimet.zip.20151008")
    #diff = Diff("/java/DEV/loader/ott/loader/gtfs/cache/trimet.zip", "/java/DEV/loader/ott/loader/gtfs/cache/trimet.zip.20151008")
    diff.is_different()
    print diff.get_new_feed_version()
    print diff.get_old_feed_version()

if __name__ == '__main__':
    main()
