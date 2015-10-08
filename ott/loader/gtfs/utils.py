import os
import logging
import urllib2
import datetime

def file_time(file):
    ''' datetime for the modified file time '''
    mtime = os.path.getmtime(file)
    dt = datetime.datetime.fromtimestamp(mtime)
    return dt

def file_age(file):
    ''' age in days '''
    mtime = file_time(file)
    now = datetime.datetime.now()
    diff = now - mtime
    return diff.days

def bkup(file):
    #import pdb; pdb.set_trace()
    if os.path.exists(file):
        mtime = file_time(file)
        tmp_file = "{}.{:%Y%m%d}".format(file, mtime)
        rm(tmp_file)
        os.rename(file, tmp_file)

def rm(file):
    if os.path.exists(file):
        os.remove(file)

def mkdir(dir):
    if not os.path.exists(dir):
        os.makedirs(dir)

def get_file_name_from_url(url):
    ret_val = url.split('/')[-1:][0]
    return ret_val

def wget(url, file_name):
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
