import os
import inspect

import shutil
import csv

import urllib2
import datetime
import logging

from ott.loader.gtfs import utils

class Cache():
    """ Does a 'smart' cache of a gtfs file
         1. it will look to see if a gtfs.zip file is in the cache, and download it and put it in the cache if not
         2. once cached, it will check to see that the file in the cache is the most up to date data...
    """
    url = None
    file_name = None
    file_path = None
    cache_dir = None
    cache_expire = 31

    def __init__(self, url, file_name=None, cache_dir=None, cache_expire=31):
        # step 1: cache dir management
        self.cache_dir = cache_dir
        if self.cache_dir is None:
            this_module_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
            self.cache_dir = os.path.join(this_module_dir, "cache")
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)
        self.cache_expire = cache_expire

        # step 2: file name
        self.file_name = file_name
        if self.file_name is None:
            self.file_name = utils.get_file_name_from_url(url)
        self.file_path = os.path.join(self.cache_dir, self.file_name)

        is_fresh_in_cache()

    def is_fresh_in_cache(self):
        ''' determine if file exists and is newer than the cache expire time
        '''
        ret_val = False
        try:
            mtime = os.path.getmtime(self.file_path)
            now = datetime.datetime.now()
            diff = now - mtime
            if diff.total_days() <= self.cache_expire:
                ret_val = True
        except:
            ret_val = False
        return ret_val


def main():
    gtfs_feeds = [
        {'url':"http://developer.trimet.org/schedule/gtfs.zip", 'name':"trimet.zip"},
        {'url':"http://www.c-tran.com/images/Google/GoogleTransitUpload.zip", 'name':"c-tran.zip"},
    ]
    for g in gtfs_feeds:
        Cache(g.get('url'), g.get('name', None))

if __name__ == '__main__':
    main()
