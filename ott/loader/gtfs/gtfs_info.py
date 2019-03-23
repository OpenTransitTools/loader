import os
import csv
import datetime

from ott.utils import file_utils
from ott.utils import object_utils

from ott.utils.cache_base import CacheBase

import logging
logging.basicConfig()
log = logging.getLogger(__file__)


class GtfsInfo(CacheBase):
    """ Get info on a gtfs.zip file:
         1. will unzip the two calendar plus the feed_info .txt files
         2. will read the calendar .txt files, and provide date ranges and the like
         3. will calulate based on the calendar how old the feed is (and how many days it has left)
         4. will read the feed_info and pull out various date ranges and feed ids
    """
    gtfs_path = None
    file_prefix = None

    def __init__(self, gtfs_path, file_prefix=''):
        """ note: file_prefix allows us to have old_gtfs.zip and new_gtfs.zip names to compare against either other
        """
        # import pdb; pdb.set_trace()
        super(GtfsInfo, self).__init__(section='gtfs')

        self.gtfs_path = gtfs_path
        self.dir_path = os.path.dirname(gtfs_path)
        self.file_prefix = file_prefix

    def is_feed_valid(self):
        ret_val = True

        # check routes
        r = self.unzip_routes()
        if not file_utils.exists_and_sized(r, 100):
            log.warning("VALID FEED?: {} routes.txt looks wrong".format(self.gtfs_path))
            ret_val = False

        # check stops
        s = self.unzip_stops()
        if not file_utils.exists_and_sized(s, 100):
            log.warning("VALID FEED?: {} stops.txt looks wrong".format(self.gtfs_path))
            ret_val = False

        # check trips
        t = self.unzip_trips()
        if not file_utils.exists_and_sized(t, 100):
            log.warning("VALID FEED?: {} trips.txt looks wrong".format(self.gtfs_path))
            ret_val = False

        return ret_val

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
        return self._get_feed_date_range()

    def get_feed_details(self, feed_name):
        """
        """
        r = self.get_feed_date_range()
        v = self.get_feed_version()
        d = self.get_days_since_stats()
        ret_val = {}
        ret_val['name'] = feed_name
        ret_val['start'] = r[0]
        ret_val['end'] = r[1]
        ret_val['version'] = v
        ret_val['since'] = d[0]
        ret_val['until'] = d[1]
        return ret_val

    def get_feed_msg(self, feed_name, prefix=" ", suffix="\n"):
        """ get feed details msg string for the .vlog file
        """
        f = self.get_feed_details(feed_name)
        msg = "{}{} : date range {} to {} ({:>3} more calendar days), version {}{}"\
            .format(prefix, f['name'], f['start'], f['end'], f['until'], f['version'], suffix)
        return msg

    def get_feed_info(self):
        return self._get_feed_info()

    @classmethod
    def get_cache_msgs(cls, cache_dir, feeds, filter=None):
        """ returns string .vlog messages based on all cached gtfs feeds
        """
        #import pdb; pdb.set_trace()
        ret_val = ""
        info = cls.get_cache_info_list(cache_dir, feeds, filter)
        for i in info:
            ret_val = "{}{}".format(ret_val, i.get_feed_msg(i.name))
        return ret_val

    @classmethod
    def get_cache_info_list(cls, cache_dir, feeds, filter=None):
        """ returns updated [] of Info objects, based on a directory of feeds
        """
        ret_val = []
        try:
            for f in feeds:
                if filter and f['name'] not in filter:
                    continue
                gtfs_path = os.path.join(cache_dir, f['name'])
                if os.path.exists(gtfs_path):
                    info = GtfsInfo(gtfs_path)
                    info.name = f['name']
                    ret_val.append(info)
                else:
                    log.info("feed {} doesn't exist".format(gtfs_path))
        except Exception as e:
            log.warn(e)
        return ret_val

    def unzip_calendar_txt(self, calendar_name='calendar.txt'):
        return file_utils.unzip_file(self.gtfs_path, file_name=calendar_name)

    def unzip_calendar_dates_txt(self,  calendar_dates_name='calendar_dates.txt'):
        return file_utils.unzip_file(self.gtfs_path, file_name=calendar_dates_name)

    def unzip_feed_info_txt(self, feed_info_name='feed_info.txt'):
        return file_utils.unzip_file(self.gtfs_path, file_name=feed_info_name)

    def unzip_stops(self, stops_name='stops.txt'):
        return file_utils.unzip_file(self.gtfs_path, file_name=stops_name)

    def unzip_routes(self, routes_name='routes.txt'):
        return file_utils.unzip_file(self.gtfs_path, file_name=routes_name)

    def unzip_trips(self, trips_name='trips.txt'):
        return file_utils.unzip_file(self.gtfs_path, file_name=trips_name)

    def _get_calendar_range(self):
        """ get the date range from calendar.txt
        """
        start_date = None
        end_date = None

        calendar_path = self.unzip_calendar_txt()
        file = open(calendar_path, 'r')
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

        logging.debug(" date range of file {}: {} to {}".format(calendar_path, start_date, end_date))
        file.close()
        return start_date, end_date

    def _get_calendar_dates_range(self):
        """ get the date range from calendar_dates.txt (as well as today's position, etc...)
        """
        start_date = None
        end_date = None
        today = datetime.datetime.now().strftime("%Y%m%d")
        today_position = -111
        total_positions = 0

        calendar_dates_path = self.unzip_calendar_dates_txt()
        file = open(calendar_dates_path, 'r')
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

        logging.debug(" date range of file {}: {} to {}, and today {} position is {} of {}".format(calendar_dates_path, start_date, end_date, today, today_position, total_positions))
        file.close()
        return start_date, end_date, today_position, total_positions

    def _get_feed_info(self):
        """ return feed version, start/end dates and id info from the feed_info.txt file...
        """
        #import pdb; pdb.set_trace()
        version = '???'
        start_date = 'ZZZ'
        end_date = ''
        id = '???'

        feed_info_path = self.unzip_feed_info_txt()
        file = open(feed_info_path, 'r')
        reader = csv.DictReader(file)
        for i, row in enumerate(reader):
            id = row.get('feed_id', id)
            start_date = row.get('feed_start_date', start_date)
            end_date = row.get('feed_end_date', end_date)
            version = row.get('feed_version', version)

        logging.debug("feed version {0} ... date range {1} to {2}".format(version, start_date, end_date))
        file.close()
        return start_date, end_date, id, version

    def _get_feed_date_range(self):
        """ date range of new gtfs file based on both calendar.txt and calendar_dates.txt
        """
        # step 1: get dates from the two gtfs calendar files
        start_date, end_date, today_position, total_positions = self._get_calendar_dates_range()
        sdate, edate = self._get_calendar_range()

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
    def cached_feeds_info(cls):
        ret_val = []

        # step 1: read the cache
        from ott.loader.gtfs.gtfs_cache import GtfsCache
        cache = GtfsCache()

        # step 2: update the cache first before getting info ???
        force_update=object_utils.is_force_update()
        if force_update:
            cache.check_cached_feeds(force_update=True)

        # step 3:
        for f in cache.feeds:
            url, name = cache.get_url_filename(f)
            cache_path = os.path.join(cache.cache_dir, name)
            info = GtfsInfo(cache_path)
            start_date,end_date,id,version = info.get_feed_info()

            i = {
                'name'       : name,
                'url'        : url,
                'version'    : version,
                'id'         : id,
                'start_date' : start_date,
                'end_date'   : end_date
            }
            ret_val.append(i)

        return ret_val

    @classmethod
    def cached_feeds_info_str(cls, info_fmt="name: {name}, version: {version}, id: {id}, dates: {start_date}-{end_date}\n"):
        ret_val = ""
        info = cls.cached_feeds_info()
        for i in info:
            n = info_fmt.format(info_fmt, **i)
            ret_val = ret_val + n
        return ret_val

    @classmethod
    def feed_looks_valid(cls, feed_path):
        info = GtfsInfo(feed_path)
        return info.is_feed_valid()


def main():
    logging.basicConfig()
    # print(GtfsInfo.cached_feeds_info_str())
    print(GtfsInfo.feed_looks_valid('./ott/loader/gtfs/cache/TRIMET.zip'))


if __name__ == '__main__':
    main()
