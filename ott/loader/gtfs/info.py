import datetime
import logging
import csv

from ott.loader.gtfs import utils as file_utils
from ott.loader.gtfs.base import Base

class Info(Base):
    """ Get info on a
         1. it will look to see if a gtfs.zip file is in the cache, and download it and put it in the cache if not
         2. once cached, it will check to see that the file in the cache is the most up to date data...
    """

    tmp_dir = None
    gtfs_path = None
    file_prefix = None
    calendar_file = None
    calendar_dates_file = None
    info_file = None

    def __init__(self, gtfs_path, file_prefix=''):
        self.tmp_dir = self.get_tmp_dir()
        self.gtfs_path = gtfs_path
        self.file_prefix = file_prefix
        self.unzip_calendar_and_info_files(file_prefix)

    def unzip_calendar_and_info_files(self, file_prefix, calendar_file='calendar.txt', calendar_dates_file='calendar_dates.txt', info_file='feed_info.txt'):
        """ unzip a file (calendar_dates.txt by default) from our old & new gtfs.zip files
        """
        #import pdb; pdb.set_trace()
        self.calendar_file = file_prefix + calendar_file
        self.calendar_dates_file = file_prefix + calendar_dates_file
        self.info_file = file_prefix + info_file
        file_utils.unzip_file(self.gtfs_path, self.calendar_file,calendar_file)
        file_utils.unzip_file(self.gtfs_path, self.calendar_dates_file,calendar_dates_file)
        file_utils.unzip_file(self.gtfs_path, self.info_file, info_file)

    def get_feed_version(self):
        start_date,end_date,id,version = self.get_feed_info()
        return version

    def get_feed_dates(self):
        start_date,end_date = self.get_feed_date_range()
        return "{0} to {1}".format(start_date, end_date)

    def is_gtfs_out_of_date(self):
        """ calculate whether we think gtfs is out of date
        """
        ret_val = False
        sdays, edays = self.get_days_since_stats()
        if sdays > 30 or edays < 30:
            ret_val = True
        return ret_val

    def get_days_since_stats(self):
        """ calculate the number of days since the gtfs was generated, and number of days left within the calendar
        """
        start_date,end_date=self.get_feed_date_range()
        sdate = datetime.datetime.strptime(start_date, '%Y%m%d')
        edate = datetime.datetime.strptime(end_date, '%Y%m%d')
        sdiff = datetime.datetime.now() - sdate
        ediff = edate - datetime.datetime.now()
        logging.info("first - {0} was {1} days ago".format(start_date, sdiff.days))
        logging.info("last  - {0} is  {1} days after today".format(end_date, ediff.days))
        return sdiff.days, ediff.days

    def get_feed_date_range(self):
        return self._get_feed_date_range(self.calendar_file, self.calendar_dates_file)

    @classmethod
    def _get_feed_date_range(cls, calendar_name, calendar_dates_name):
        """ date range of new gtfs file
        """
        start_date = 'ZZZ'
        end_date = ''
        start_date, end_date, today_position, total_positions = cls._get_calendar_dates_range(calendar_dates_name)
        return start_date, end_date

    @classmethod
    def _get_calendar_dates_range(cls, calendar_dates_name):
        """ date range of new gtfs file
        """
        start_date = 'ZZZ'
        end_date = ''
        today = datetime.datetime.now().strftime("%Y%m%d")
        today_position = -111
        total_positions = 0

        file = open(calendar_dates_name, 'r')
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

        logging.info(" date range of file {}: {} to {}, and today {} position is {} of {}".format(calendar_dates_name, start_date, end_date, today, today_position, total_positions))

        return start_date, end_date, today_position, total_positions

    def get_feed_info(self):
        return self._get_feed_info(self.info_file)

    @classmethod
    def _get_feed_info(cls, feed_info_name):
        """ return feed version, start/end dates and id info from the feed_info.txt file...
        """
        version = '???'
        start_date = 'ZZZ'
        end_date = ''
        id = '???'

        logging.info("opening file {0}".format(feed_info_name))
        file = open(feed_info_name, 'r')
        reader = csv.DictReader(file)
        for i, row in enumerate(reader):
            id = row['feed_id']
            start_date = row['feed_start_date']
            end_date = row['feed_end_date']
            version = row['feed_version']

        logging.info("feed version {0} ... date range {1} to {2}".format(version, start_date, end_date))
        return start_date, end_date, id, version
