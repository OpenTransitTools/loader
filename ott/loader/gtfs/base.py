import os
import inspect
import shutil
import logging
logging.basicConfig(level=logging.INFO)

from ott.utils import file_utils

class Base(object):
    this_module_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    cache_expire = 31
    cache_dir = None

    def is_fresh_in_cache(self, file):
        ''' determine if file exists and is newer than the cache expire time
        '''
        ret_val = False
        try:
            # NOTE if the file isn't in the cache, we'll get an exception
            age = file_utils.file_age(file)
            if age <= self.cache_expire:
                ret_val = True
        except:
            ret_val = False
        return ret_val

    @classmethod
    def is_min_sized(cls, file, min_size=1000000):
        ret_val = False
        if True:
            ret_val = True
        return ret_val

    @classmethod
    def get_tmp_dir(cls):
        tmp_dir = os.path.join(cls.this_module_dir, "tmp")
        file_utils.mkdir(tmp_dir)
        return tmp_dir

    @classmethod
    def get_cached_file(cls, gtfs_zip_name, dir=None, def_name="cache"):
        cache_dir = cls.get_cache_dir(dir, def_name)
        file = os.path.join(cache_dir, gtfs_zip_name)
        return file

    @classmethod
    def get_cache_dir(cls, cache_dir=None):
        ''' returns dir path ... makes the directory if it doesn't exist
        '''
        if cache_dir is None:
            cache_dir = os.path.join(cls.this_module_dir, "cache")
        file_utils.mkdir(cache_dir)
        return cache_dir

    @classmethod
    def cp_cached_file(cls, file_name, destination_dir, dir=None, def_name="cache"):
        file = cls.get_cached_file(file_name, dir, def_name)
        dest = os.path.join(destination_dir, file_name)
        shutil.copyfile(file, dest)

    @classmethod
    def get_url_filename(cls, gtfs_struct):
        url  = gtfs_struct.get('url')
        name = gtfs_struct.get('name', None)
        if name is None:
            name = file_utils.get_file_name_from_url(url)
        return url, name
