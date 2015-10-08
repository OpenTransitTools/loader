import os
import inspect

import shutil
import csv

import urllib2
import datetime
import logging

class Download():
    """ Does a 'smart' cache of a gtfs file...
         check to see if we've go t a GTFS file cached
    """

    def __init__(self, cache_dir=None, gtfs_url="http://developer.trimet.org/schedule/gtfs.zip"):
        self.wget(gtfs_url, "trimet.zip")
        pass


    @classmethod
    def get_file_name_from_url(cls, url):
        ret_val = url.split('/')[-1:][0]
        return ret_val

    @classmethod
    def wget(cls, url, file_name=None):
        """ wget a file from url
            IMPORTANT NOTE: this will *not* work if the URL is a redirect, etc...
        """
        try:
            if file_name is None:
                file_name = cls.get_file_name_from_url(url)

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
    d = Download()