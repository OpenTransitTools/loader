import os
import inspect
import datetime
import logging
import csv

from ott.loader.gtfs import utils

class Diff():
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
        this_module_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
        self.tmp_dir = os.path.join(this_module_dir, "tmp")
        utils.mkdir(self.tmp_dir)
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
        cal_diff  = utils.diff_files(self.old_cal,  self.old_info)
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

    @classmethod
    def get_feed_version(cls, file_name):
        start_date,end_date,id,version = cls.get_feed_info(file_name)
        return version

    @classmethod
    def get_feed_info(cls, file_name):
        """ return feed version, start/end dates and id info from the feed_info.txt file...
        """
        version = '???'
        start_date = 'ZZZ'
        end_date = ''
        id = '???'

        logging.info("opening file {0}".format(file_name))
        file = open(file_name, 'r')
        reader = csv.DictReader(file)
        for i, row in enumerate(reader):
            id = row['feed_id']
            start_date = row['feed_start_date']
            end_date = row['feed_end_date']
            version = row['feed_version']

        logging.info("feed version {0} ... date range {1} to {2}".format(version, start_date, end_date))
        return start_date, end_date, id, version

    @classmethod
    def get_date_range_of_calendar_dates(cls, file_name):
        """ date range of new gtfs file
        """
        start_date = 'ZZZ'
        end_date = ''
        today = datetime.datetime.now().strftime("%Y%m%d")
        today_position = -111
        total_positions = 0

        file = open(file_name, 'r')
        reader = csv.DictReader(file)
        for i, row in enumerate(reader):
            date = row['date']
            if date < start_date:
                start_date = date
            if date > end_date:
                end_date = date
            if date == today:
                today_position = i
            total_positions = i

        # give total positions some value
        if today_position < 0:
            today_position = total_positions

        logging.info(" date range of file " + file_name + ": " + start_date + " to " + end_date +
                     ", and today " + today + " position is " + str(today_position) + " of " + str(total_positions))
        return start_date, end_date, today_position, total_positions

    @classmethod
    def gtfs_calendar_age(cls, gtfs):
        """ calculate the number of days since the gtfs was generated, and number of days left within the calendar
        """
        start_date,end_date,pos,total=cls.get_date_range_of_calendar_dates(gtfs)
        sdate = datetime.datetime.strptime(start_date, '%Y%m%d')
        edate = datetime.datetime.strptime(end_date, '%Y%m%d')
        sdiff = datetime.datetime.now() - sdate
        ediff = edate - datetime.datetime.now()
        logging.info("first - {0} was {1} days ago".format(start_date, sdiff.days))
        logging.info("last  - {0} is  {1} days after today".format(end_date, ediff.days))
        return sdiff.days, ediff.days

    @classmethod
    def is_gtfs_out_of_date(cls, gtfs):
        """ calculate whether we think gtfs is out of date
        """
        ret_val = False
        start_date,end_date,pos,total=cls.get_date_range_of_calendar_dates(gtfs)
        pos_diff=pos * 1.0001 / total

        sdays, edays = self.gtfs_calendar_age(gtfs)
        if pos_diff > 0.40 or sdays > 30 or edays < 30:
            ret_val = True
        return ret_val


def main():
    logging.basicConfig(level=logging.INFO)
    diff = Diff()
    diff.is_different()
    print diff.get_new_feed_version()
    print diff.get_old_feed_version()

if __name__ == '__main__':
    main()
