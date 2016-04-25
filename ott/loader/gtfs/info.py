import datetime
import logging
import csv

from ott.utils import file_utils
from ott.utils.cache_base import CacheBase

class Info(CacheBase):
    """ Get info on a gtfs.zip file:
         1. will unzip the two calendar plus the feed_info .txt files
         2. will read the calendar .txt files, and provide date ranges and the like
         3. will calulate based on the calendar how old the feed is (and how many days it has left)
         4. will read the feed_info and pull out various date ranges and feed ids
    """
    gtfs_path = None
    file_prefix = None
    calendar_file = None
    calendar_dates_file = None
    feed_info_file = None

    def __init__(self, gtfs_path, file_prefix=''):
        ''' note: file_prefix allows us to have old_gtfs.zip and new_gtfs.zip names to compare against either other
        '''
        #import pdb; pdb.set_trace()
        self.gtfs_path = gtfs_path
        self.file_prefix = file_prefix
        self.unzip_calendar_and_info_files(file_prefix)

    def unzip_calendar_and_info_files(self, file_prefix, calendar_file='calendar.txt', calendar_dates_file='calendar_dates.txt', info_file='feed_info.txt'):
        """ unzip a file (calendar_dates.txt by default) from our old & new gtfs.zip files
        """
        self.calendar_file = file_prefix + calendar_file
        self.calendar_dates_file = file_prefix + calendar_dates_file
        self.feed_info_file = file_prefix + info_file
        file_utils.unzip_file(self.gtfs_path, self.calendar_file,calendar_file)
        file_utils.unzip_file(self.gtfs_path, self.calendar_dates_file,calendar_dates_file)
        file_utils.unzip_file(self.gtfs_path, self.feed_info_file, info_file)

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
        """ date range of new gtfs file based on both calendar.txt and calendar_dates.txt
        """

        # step 1: get dates from the two gtfs calendar files
        start_date, end_date, today_position, total_positions = cls._get_calendar_dates_range(calendar_dates_name)
        sdate, edate = cls._get_calendar_range(calendar_name)

        # step 2: eliminate null values default values
        if start_date is None: start_date = sdate
        if end_date is None:   end_date = edate

        # step 3: set return values based on oldest and youngest dates...
        if sdate and sdate < start_date:
            start_date = sdate
        if edate and edate > end_date:
            end_date = edate

        return start_date, end_date

    @classmethod
    def _get_calendar_range(cls, calendar_name):
        """ get the date range from calendar.txt
        """
        start_date = None
        end_date = None

        file = open(calendar_name, 'r')
        reader = csv.DictReader(file)
        for i, row in enumerate(reader):
            # step 1: grab dates from .csv
            sdate = row['start_date']
            edate = row['end_date']

            # step 2: set default dates
            if start_date is None:  start_date = sdate
            if end_date is None:    end_date = edate

            # step 3: check and set dates to smaller/larger values
            if sdate and sdate < start_date:
                start_date = sdate
            if edate and edate > end_date:
                end_date = edate

        logging.info(" date range of file {}: {} to {}".format(calendar_name, start_date, end_date))

        return start_date, end_date

    @classmethod
    def _get_calendar_dates_range(cls, calendar_dates_name):
        """ get the date range from calendar_dates.txt (as well as today's position, etc...)
        """
        start_date = None
        end_date = None
        today = datetime.datetime.now().strftime("%Y%m%d")
        today_position = -111
        total_positions = 0

        file = open(calendar_dates_name, 'r')
        reader = csv.DictReader(file)
        for i, row in enumerate(reader):
            # step 1: grab date from .csv
            date = row['date']

            # step 2: set default dates
            if start_date is None:  start_date = date
            if end_date is None:    end_date = date

            # step 3: check and set dates to smaller/larger values
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
        return self._get_feed_info(self.feed_info_file)

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

