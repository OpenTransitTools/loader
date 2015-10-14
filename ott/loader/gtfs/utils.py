import os
import logging
import datetime
import urllib2
import zipfile
import filecmp

##
## FILE UTILS
##


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

def file_size(file):
    s = os.stat(file)
    return s.st_size

def exists_and_sized(file, size, expire):
    ret_val = True
    if os.path.exists(file) is False:
        logging.info("{} doesn't exist ".format(file))
        ret_val = False
    elif file_age(file) > expire:
        logging.info("{} is {} days old, thus older than the {} day refresh threshold".format(file, file_age(file), expire))
        ret_val = False
    elif file_size(file) < size:
        logging.info("{} is smaller than {} bytes in size".format(file, size))
        ret_val = False
    return ret_val

def bkup(file):
    #import pdb; pdb.set_trace()
    if os.path.exists(file):
        mtime = file_time(file)
        tmp_file = "{}.{:%Y%m%d}".format(file, mtime)
        rm(tmp_file)
        os.rename(file, tmp_file)

def mv(src, dst):
    os.rename(src, dst)

def rm(file):
    if os.path.exists(file):
        os.remove(file)

def cd(dir):
    os.chdir(dir)

def mkdir(dir):
    if not os.path.exists(dir):
        os.makedirs(dir)

def get_file_name_from_url(url):
    ret_val = url.split('/')[-1:][0]
    return ret_val

def diff_files(old_name, new_name):
    """ return True if the files are DIFFERENT ... False == files are THE SAME...
    """
    ret_val = True

    #import pdb; pdb.set_trace()
    try:
        # check #1
        ret_val = not filecmp.cmp(old_name, new_name)
        logging.info("It's {0} that {1} is different from {2} (according to os.stat)".format(ret_val, old_name, new_name))

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
                ret_val = True
                break
            k=k+1
    except Exception, e:
        logging.warn("problems comparing {} and {}".format(old_name, new_name))
        ret_val = True
    return ret_val


def unzip_file(zip_file, target_file, file_name):
    """ unzips a file from a zip file...
        @returns True if there's a problem...
    """
    ret_val = False

    #import pdb; pdb.set_trace()
    try:
        rm(target_file)
        zip = zipfile.ZipFile(zip_file, 'r')
        file = open(target_file, 'wb')
        file.write(zip.read(file_name))
        file.flush()
        file.close()
        zip.close()
    except Exception, e:
        logging.warn("problems extracting {} from {} into file {}".format(file_name, zip_file, target_file))
        ret_val = True

    return ret_val


##
## WEB UTILS
##

def wget(url, file_name):
    """ wget a file from url
        IMPORTANT NOTE: this will *not* work if the URL is a redirect, etc...
    """
    try:
        # get gtfs file from url
        req = urllib2.Request(url)
        res = urllib2.urlopen(req)

        # write it out
        f = open(file_name, 'wb')
        f.write(res.read())
        f.flush()
        f.close()
        res.close()

        logging.info("check_gtfs: downloaded " + url + " into file " + file_name)
    except:
        logging.warn('could not get data from url:\n', url, '\n(not a friendly place)')

