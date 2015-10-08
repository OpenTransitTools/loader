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
    cache_dir = None

    def __init__(self, url, file_name):
        if file_name is None:
            file_name = utils.get_file_name_from_url(url)


    def is_in_cache(self, file_name):
        pass


def main():
    gtfs_feeds = [
        {'url':"http://developer.trimet.org/schedule/gtfs.zip", 'name':"trimet.zip"},
        {'url':"http://www.c-tran.com/images/Google/GoogleTransitUpload.zip", 'name':"c-tran.zip"},
    ]
    for g in gtfs_feeds:
        c = Cache(g.get('url'), g.get('name', None))

if __name__ == '__main__':
    main()
