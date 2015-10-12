import os
import inspect
import logging
import shutil

from ott.loader.gtfs import utils
from ott.loader.gtfs.diff import Diff

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

    def __init__(self, url, file_name, cache_dir=None, cache_expire=31):

        # step 1: temp dir
        tmp_dir = self.get_tmp_dir()
        utils.mkdir(tmp_dir)

        # step 2: cache dir management
        self.cache_dir = self.get_cache_dir(cache_dir)
        utils.mkdir(self.cache_dir)
        self.cache_expire = cache_expire

        # step 3: file name
        self.file_name = file_name
        self.file_path = os.path.join(self.cache_dir, self.file_name)

        # step 4: download new gtfs file
        self.url = url
        tmp_path = os.path.join(tmp_dir, self.file_name)
        utils.wget(self.url, tmp_path)

        # step 5: check the cache whether we should update or not
        update = False
        if self.is_fresh_in_cache():
            logging.info("diff gtfs file")
            diff = Diff(self.file_path, tmp_path)
            if diff.is_different():
                update = True
        else:
            update = True

        if update:
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

    @classmethod
    def cmp_file_to_cached(cls, gtfs_zip_name, cmp_dir):
        ''' returns a Diff object with cache/gtfs_zip_name & cmp_dir/gtfs_zip_name
        '''
        cache_path = os.path.join(cls.get_cache_dir(), gtfs_zip_name)
        other_path = os.path.join(cmp_dir, gtfs_zip_name)
        diff = Diff(cache_path, other_path)
        return diff

    @classmethod
    def get_tmp_dir(cls):
        this_module_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
        tmp_dir = os.path.join(this_module_dir, "tmp")
        return tmp_dir

    @classmethod
    def get_cache_dir(cls, dir=None, def_name="cache"):
        ''' returns either dir (stupid check) or <current-directory>/$def_name
        '''
        ret_val = dir
        if dir is None:
            this_module_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
            ret_val = os.path.join(this_module_dir, def_name)
        return ret_val

    @classmethod
    def get_cached_file(cls, gtfs_zip_name, dir=None, def_name="cache"):
        cache_dir = cls.get_cache_dir(dir, def_name)
        file = os.path.join(cache_dir, gtfs_zip_name)
        return file

    @classmethod
    def cp_cached_gtfs_zip(cls, gtfs_zip_name, destination_dir, dir=None, def_name="cache"):
        file = cls.get_cached_file(gtfs_zip_name, dir, def_name)
        dest = os.path.join(destination_dir, gtfs_zip_name)
        shutil.copyfile(file, dest)

    @classmethod
    def get_url_filename(cls, gtfs_struct):
        url  = gtfs_struct.get('url')
        name = gtfs_struct.get('name', None)
        if name is None:
            name = utils.get_file_name_from_url(url)
        return url, name

    @classmethod
    def get_gtfs_feeds(cls):
        gtfs_feeds = [
            {'url':"http://developer.trimet.org/schedule/gtfs.zip", 'name':"trimet.zip"},
            {'url':"http://www.c-tran.com/images/Google/GoogleTransitUpload.zip", 'name':"c-tran.zip"},
        ]
        return gtfs_feeds

def main():
    logging.basicConfig(level=logging.INFO)
    for g in Cache.get_gtfs_feeds():
        url,name = Cache.get_url_filename(g)
        Cache(url, name)

if __name__ == '__main__':
    main()
