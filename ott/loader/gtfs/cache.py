import os
import inspect

import shutil
import csv

import urllib2
import datetime
import logging

class Cache():
    """ Does a 'smart' cache of a gtfs file
         1. it will look to see if a gtfs.zip file is in the cache, and download it and put it in the cache if not
         2. once cached, it will check to see that the file in the cache is the most up to date data...
    """
    def __init__(self, url, file_name):
        if file_name is None:
            file_name = self.get_file_name_from_url(url)

        print url, file_name

    @classmethod
    def get_file_name_from_url(cls, url):
        ret_val = url.split('/')[-1:][0]
        return ret_val

    @classmethod
    def wget(cls, url, file_name):
        """ wget a file from url
            IMPORTANT NOTE: this will *not* work if the URL is a redirect, etc...
        """
        try:
            # get gtfs file from url
            req = urllib2.Request(url)
            res = urllib2.urlopen(req)

            # write it out
            f = open(file_name, 'w')
            f.write(res.read())
            f.flush()
            f.close()
            res.close()

            logging.info("check_gtfs: downloaded " + url + " into file " + file_name)
        except:
            logging.warn('could not get data from url:\n', url, '\n(not a friendly place)')

def main():
    gtfs_feeds = [
        {'url':"http://developer.trimet.org/schedule/gtfs.zip", 'name':"trimet.zip"},
        {'url':"http://www.c-tran.com/images/Google/GoogleTransitUpload.zip", 'name':"c-tran.zip"},
    ]
    for g in gtfs_feeds:
        c = Cache(g.get('url'), g.get('name', None))

if __name__ == '__main__':
    main()
