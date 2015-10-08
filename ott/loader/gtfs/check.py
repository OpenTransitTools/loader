import os
import inspect

import shutil
import csv

import urllib2
import filecmp
import shutil
import zipfile
import datetime
import logging

class Check():
    """ Compares Two Gtfs Zip Files, looking at feed_info.txt & calendar_date.txt file to see if it's older than
        cached gtfs.zip file
    """
    def __init__(self, cache_dir=None, gtfs_url="http://developer.trimet.org/schedule/gtfs.zip"):

        # step 1: set up some dirs
        self.tmp_dir      = "./tmp"
        self.cache_dir    = cache_dir

        # step 2: file names
        self.gtfs_url = gtfs_url
        self.gtfs_file_name = self.gtfs_url.split('/')[-1:][0]
        self.new_gtfs_zip   = os.path.join(self.tmp_dir, self.gtfs_file_name)
        self.old_gtfs_zip = os.path.join(self.cache_dir, self.gtfs_file_name)
        self.old_cal = self.new_cal = self.old_info = self.new_info = None


    def download_gtfs(self, url=None, zip=None):
        """ grab gtfs.zip file from url
            IMPORTANT NOTE: this will *not* work if the URL is a redirect, etc...
        """
        if url is None:
            url = self.gtfs_url
        if zip is None:
            zip = self.new_gtfs_zip
        
        try:
            # get gtfs file from url
            req = urllib2.Request(url)
            res = urllib2.urlopen(req)

            # write it out
            f = open(zip, 'w')
            f.write(res.read())
            f.flush()
            f.close()
            res.close()

            logging.info("check_gtfs: downloaded " + url + " into file " + zip)
        except:
            logging.warn('could not get data from url:\n', url, '\n(not a friendly place)')
            pass


    def unzip_file(self, zip_file, target_file, file_name):
        """ unzips a file from a zip file...
            @returns True if there's a problem...
        """
        ret_val = False
        try:
            zip  = zipfile.ZipFile(zip_file, 'r')
            file = open(target_file, 'w')
            file.write(zip.read(file_name))
            file.flush()
            file.close()
            zip.close()
        except:
            ret_val = False
            logging.warn("problems extracting " + file_name + " from " + zip_file + " into file " + target_file)

        return ret_val

    def unzip_calendar_and_info_files(self, cal_file='calendar_dates.txt', info_file='feed_info.txt'):
        """ unzip a file (calendar_dates.txt by default) from our old & new gtfs.zip files
        """
        # step 1: unzip the cal_file from the old gtfs file
        self.old_cal = "old_" + cal_file
        self.old_info = "old_" + info_file
        self.unzip_file(self.old_gtfs_zip, self.old_cal, cal_file)
        self.unzip_file(self.old_gtfs_zip, self.old_info, info_file)

        # step 2: unzip the cal_file from the old gtfs file
        self.new_cal = "new_" + cal_file
        self.new_info = "new_" + info_file
        self.unzip_file(self.new_gtfs_zip, self.new_cal, cal_file)
        self.unzip_file(self.new_gtfs_zip, self.new_info, info_file)
        return self.old_cal, self.new_cal, self.old_info, self.new_info

    def cmp_files(self, old_name, new_name):
        """ return whether files are the same or not...
        """
        ret_val = False
        try:
            #import pdb; pdb.set_trace()

            # check #1
            ret_val = filecmp.cmp(old_name, new_name)
            logging.info("It's {0} that {1} is the same as {2} (according to os.stat)".format(ret_val, old_name, new_name))

            # check #2
            # adapted from http://stackoverflow.com/questions/3043026/comparing-two-text-files-in-python
            of = open(old_name, "r")
            nf = open(new_name, "r")
            olist = of.readlines()
            nlist = nf.readlines()
            k=1
            for i,j in zip(olist, nlist): #note: zip is used to iterate variables in 2 lists in single loop
                if i != j:
                    logging.info("At line #{0}, there's a difference between the files:\n\t{1}\t\t--vs--\n\t{2}\n".format(k, i, j))
                    ret_val = False
                    break 
                k=k+1
        except:
            ret_val = False
            logging.warn("problems comparing " + old_name + " and " + new_name)
        return ret_val


    def get_feed_info(self, file_name):
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

    def get_feed_version(self, file_name):
        start_date,end_date,id,version = self.get_feed_info(file_name)
        return version

    def get_new_feed_version(self):
        start_date,end_date,id,version = self.get_feed_info(self.new_info)
        return version

    def get_new_feed_dates(self):
        start_date, end_date, tday, tpos = self.get_date_range_of_calendar_dates(self.new_cal)
        return "{0} to {1}".format(start_date, end_date)

    def get_date_range_of_calendar_dates(self, file_name):
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


    def gtfs_calendar_age(self, gtfs):
        """ calculate the number of days since the gtfs was generated, and number of days left within the calendar
        """
        start_date,end_date,pos,total=self.get_date_range_of_calendar_dates(gtfs)
        sdate = datetime.datetime.strptime(start_date, '%Y%m%d')
        edate = datetime.datetime.strptime(end_date, '%Y%m%d')
        sdiff = datetime.datetime.now() - sdate
        ediff = edate - datetime.datetime.now()
        logging.info("first - {0} was {1} days ago".format(start_date, sdiff.days))
        logging.info("last  - {0} is  {1} days after today".format(end_date, ediff.days))
        return sdiff.days, ediff.days


    def is_gtfs_out_of_date(self, gtfs):
        """ calculate whether we think gtfs is out of date
        """
        ret_val = False
        start_date,end_date,pos,total=self.get_date_range_of_calendar_dates(gtfs)
        pos_diff=pos * 1.0001 / total

        sdays, edays = self.gtfs_calendar_age(gtfs)
        if pos_diff > 0.40 or sdays > 30 or edays < 30:
            ret_val = True
        return ret_val


    def mk_tmp_dir(self):
        """ remove existing ./tmp directory, and make new / empty one
        """
        shutil.rmtree(self.tmp_dir, True)
        if not os.path.exists(self.tmp_dir):
            os.makedirs(self.tmp_dir)

    def cd_tmp_dir(self):
        """ make a ./tmp directory, and cd into it...
        """
        if not os.path.exists(self.tmp_dir):
            os.makedirs(self.tmp_dir)
        os.chdir(self.tmp_dir)


    def update_gtfs(self):
        """ backup old gtfs file, and move new gtfs file into graph cache...
        """
        if os.path.isfile(self.old_gtfs_zip):
            today = datetime.datetime.now().strftime("%Y-%m-%d")
            shutil.copy2(self.old_gtfs_zip, self.old_gtfs_zip + today)
        if os.path.isfile(self.new_gtfs_zip):
            shutil.copy2(self.new_gtfs_zip, self.old_gtfs_zip)


def main():
    logging.basicConfig(level=logging.INFO)
    cmp = CompareTwoGtfsZipFiles()
    cmp.cd_tmp_dir()
    cmp.download_gtfs()
    old_cal, new_cal, old_info, new_info = cmp.unzip_calendar_and_info_files()
    is_same_gtfs = cmp.cmp_files(old_info, new_info)
    start_date,end_date,pos,total = cmp.get_date_range_of_calendar_dates(new_cal)
    start_date,end_date,id,version = cmp.get_feed_info(new_info)
    print cmp.get_new_feed_version()


if __name__ == '__main__':
    main()
