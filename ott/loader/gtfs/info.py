import datetime
import logging
import csv

from ott.loader.gtfs import utils as file_utils

class Info(Base):
    """ Get info on a
         1. it will look to see if a gtfs.zip file is in the cache, and download it and put it in the cache if not
         2. once cached, it will check to see that the file in the cache is the most up to date data...
    """

    tmp_dir = None
    gtfs_path = None
    file_prefix = None
    calendar_dates_file = None
    info_file = None

    def __init__(self, gtfs_path, file_prefix=''):
        self.tmp_dir = self.get_tmp_dir()
        self.gtfs_path = gtfs_path
        self.file_prefix = file_prefix
        self.unzip_calendar_and_info_files(file_prefix)

    @classmethod
    def unzip_calendar_and_info_files(self, file_prefix, calendar_dates_file='calendar_dates.txt', info_file='feed_info.txt'):
        """ unzip a file (calendar_dates.txt by default) from our old & new gtfs.zip files
        """
        self.calendar_dates_file = file_prefix + calendar_dates_file
        self.info_file = file_prefix + info_file
        file_utils.unzip_file(self.gtfs_path, self.calendar_dates_file,  calendar_dates_file)
        file_utils.unzip_file(self.gtfs_path, self.info_file, info_file)

    def get_feed_version(self):
        start_date,end_date,id,version = self.get_feed_info(self.info_file):
        return version

    def get_feed_info(self):
        return self._get_feed_info(self.info_file)

    @classmethod
    def _get_feed_info(cls, file_name):
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

    def get_date_range_of_calendar_dates(self):
        return self._get_date_range_of_calendar_dates(self.calendar_dates_file)

    @classmethod
    def _get_date_range_of_calendar_dates(cls, file_name):
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

    def gtfs_calendar_age(self):
        return self.gtfs_calendar_age(self, self.gtfs_path)

    @classmethod
    def _gtfs_calendar_age(cls, gtfs):
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


    def is_gtfs_out_of_date(self):
        return self._is_gtfs_out_of_date(self.gtfs_path)

    @classmethod
    def _is_gtfs_out_of_date(cls, gtfs):
        """ calculate whether we think gtfs is out of date
        """
        ret_val = False
        start_date,end_date,pos,total=cls.get_date_range_of_calendar_dates(gtfs)
        pos_diff=pos * 1.0001 / total

        sdays, edays = self.gtfs_calendar_age(gtfs)
        if pos_diff > 0.40 or sdays > 30 or edays < 30:
            ret_val = True
        return ret_val

