import os
import inspect
import logging

import shutil
import csv

import datetime


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

        # step 0: temp dir
        this_module_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
        tmp_dir = os.path.join(this_module_dir, "tmp")
        utils.mkdir(tmp_dir)

        # step 1: cache dir management
        self.cache_dir = cache_dir
        if self.cache_dir is None:
            self.cache_dir = os.path.join(this_module_dir, "cache")
        utils.mkdir(self.cache_dir)
        self.cache_expire = cache_expire

        # step 2: file name
        self.file_name = file_name
        if self.file_name is None:
            self.file_name = utils.get_file_name_from_url(url)
        self.file_path = os.path.join(self.cache_dir, self.file_name)

        # step 3: download new gtfs file
        self.url = url
        tmp_path = os.path.join(tmp_dir, self.file_name)
        utils.wget(self.url, tmp_path)

        # step 4: check the cache whether we should update or not
        if self.is_fresh_in_cache():
            logging.info("diff gtfs file")
        else:
            logging.info("move to cache")
            utils.bkup(self.file_path)
            os.rename(tmp_path, self.file_path)

    def is_fresh_in_cache(self):
        ''' determine if file exists and is newer than the cache expire time
        '''
        #import pdb; pdb.set_trace()
        ret_val = False
        try:
            # NOTE if the file isn't in the cache, we'll get an exception
            age = utils.file_age(self.file_path)
            if age <= self.cache_expire:
                ret_val = True
        except:
            ret_val = False
        return ret_val

def main():
    logging.basicConfig(level=logging.INFO)
    gtfs_feeds = [
        {'url':"http://developer.trimet.org/schedule/gtfs.zip", 'name':"trimet.zip"},
        {'url':"http://www.c-tran.com/images/Google/GoogleTransitUpload.zip", 'name':"c-tran.zip"},
    ]
    for g in gtfs_feeds:
        Cache(g.get('url'), g.get('name', None))

if __name__ == '__main__':
    main()
